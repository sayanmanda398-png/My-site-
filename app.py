from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, datetime, os
app = Flask(__name__)
app.secret_key = "babu_pro_123"
os.makedirs('static/uploads', exist_ok=True)
ADMIN_USER="Sayan"
ADMIN_PASS="Sayan@123"
def ist_now(): return (datetime.datetime.utcnow()+datetime.timedelta(hours=5,minutes=30)).strftime("%I:%M %p - %d/%m")
def init_db():
 conn=sqlite3.connect('users.db')
 conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, photo TEXT, bio TEXT)')
 conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0, media TEXT, mtype TEXT)')
 conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))')
 conn.commit();conn.close()
init_db()
CSS="body{margin:0;background:#0a0a20;display:flex;justify-content:center;padding:20px;font-family:sans-serif}.phone{width:100%;max-width:360px;min-height:800px;background:linear-gradient(180deg,#2e40e6,#050516);border-radius:35px;padding:15px;color:white}.chat-pill{background:#2a2fb8;border-radius:20px;padding:12px;margin:8px 0}.post-media{width:100%;border-radius:15px;margin-top:8px}.btn-follow{background:#5a7cff;padding:6px 14px;border-radius:20px;color:white;text-decoration:none;font-size:11px}.btn-unfollow{background:gray;padding:6px 14px;border-radius:20px;color:white;text-decoration:none;font-size:11px}"
@app.route('/', methods=['GET','POST'])
def home():
 user=session.get('user')
 if not user: return redirect('/login')
 conn=sqlite3.connect('users.db');cur=conn.cursor()
 if request.method=='POST':
  txt=request.form.get('content','').strip()
  if txt: cur.execute('INSERT INTO posts (username,content,time,likes) VALUES (?,?,?,0)',(user,txt,ist_now()));conn.commit()
 cur.execute('SELECT bio FROM users WHERE username=?',(user,));r=cur.fetchone();bio=r[0] if r and r[0] else "No bio - Edit!"
 cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(user,));followers=cur.fetchone()[0]
 cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(user,));following=cur.fetchone()[0]
 cur.execute('SELECT COUNT(*) FROM posts WHERE username=?',(user,));pc=cur.fetchone()[0]
 cur.execute('SELECT id,username,content,time,likes FROM posts ORDER BY id DESC');posts=cur.fetchall()
 html=""
 for pid,uname,cont,tm,likes in posts:
  fb=""
  if uname!=user:
   cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(user,uname))
   fb=f"<a href='/unfollow/{uname}' class='btn-unfollow' style='float:right'>Following</a>" if cur.fetchone() else f"<a href='/follow/{uname}' class='btn-follow' style='float:right'>+ Follow</a>"
  html+=f"<div class='chat-pill'><b>@{uname}</b>{fb}<div>{cont}</div><small>{tm} ❤️{likes}</small></div>"
 conn.close()
 return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><b>@{user}</b> | {followers} Followers | {following} Following<br>{bio} <a href='/edit_profile' class='btn-follow'>Edit Bio</a><form method='POST'><input name='content' placeholder='Post...' style='width:70%;padding:10px;border-radius:20px;color:black'><button>↑</button></form>{html}</div></body></html>"
@app.route('/follow/<u>')
def follow(u): me=session.get('user');conn=sqlite3.connect('users.db');conn.execute('INSERT OR IGNORE INTO follows VALUES (?,?)',(me,u));conn.commit();conn.close();return redirect('/')
@app.route('/unfollow/<u>')
def unfollow(u): me=session.get('user');conn=sqlite3.connect('users.db');conn.execute('DELETE FROM follows WHERE follower=? AND following=?',(me,u));conn.commit();conn.close();return redirect('/')
@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
 me=session.get('user');conn=sqlite3.connect('users.db');cur=conn.cursor()
 if request.method=='POST': cur.execute('UPDATE users SET bio=? WHERE username=?',(request.form.get('bio','')[:150],me));conn.commit();conn.close();return redirect('/')
 cur.execute('SELECT bio FROM users WHERE username=?',(me,));r=cur.fetchone();bio=r[0] if r and r[0] else "";conn.close()
 return f"<html><head><style>{CSS}</style></head><body><div class='phone'><a href='/'>Back</a><h3>Edit Bio</h3><form method='POST'><textarea name='bio' style='width:100%;height:80px;color:black'>{bio}</textarea><button>Save</button></form></div></body></html>"
@app.route('/like/<int:pid>')
def like(pid): conn=sqlite3.connect('users.db');conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,));conn.commit();conn.close();return redirect('/')
@app.route('/signup', methods=['GET','POST'])
def signup():
 if request.method=='POST':
  u=request.form.get('username');e=request.form.get('email');p=request.form.get('password');conn=sqlite3.connect('users.db')
  try: conn.execute('INSERT INTO users VALUES (?,?,?,?,?)',(u,e,p,None,None));conn.commit();conn.close();return redirect('/login')
  except: conn.close();return redirect('/signup')
 return "<html><body><h2>Signup</h2><form method='POST'><input name='username'><input name='email'><input name='password' type='password'><button>Sign up</button></form></body></html>"
@app.route('/login', methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=request.form.get('username');p=request.form.get('password');conn=sqlite3.connect('users.db');cur=conn.cursor();cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p));ok=cur.fetchone();conn.close()
  if ok: session['user']=u;return redirect('/')
 return "<html><body><h2>Login</h2><form method='POST'><input name='username'><input name='password' type='password'><button>Login</button></form><a href='/signup'>Signup</a></body></html>"
@app.route('/logout')
def logout(): session.clear();return redirect('/login')
