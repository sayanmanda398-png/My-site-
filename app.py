from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, datetime, os
app = Flask(__name__)
app.secret_key = "babu_pro_123"
os.makedirs('static/uploads', exist_ok=True)
def ist_now():
    return (datetime.datetime.utcnow()+datetime.timedelta(hours=5,minutes=30)).strftime("%I:%M %p - %d/%m")
def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, photo TEXT, bio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0, media TEXT, mtype TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))')
    conn.commit(); conn.close()
init_db()
CSS = """
body{margin:0;min-height:100vh;background:#08081a;display:flex;justify-content:center;padding:20px 0;font-family:system-ui,sans-serif}
.phone{width:100%;max-width:380px;min-height:850px;background:linear-gradient(180deg,#2e40e6 0%, #1a2480 45%, #050516 100%);border-radius:40px;padding:16px;box-shadow:0 0 0 8px #e8e8e8, 0 30px 80px rgba(0,0,0,0.7);box-sizing:border-box;color:white}
.top{ display:flex; justify-content:space-between; align-items:center; padding:6px 4px }
.pill{ background:rgba(40,50,150,0.75); border-radius:28px; padding:14px; margin:10px 0; border:1px solid rgba(255,255,255,0.12) }
.stat{ display:flex; gap:18px; justify-content:center; margin:10px 0; font-size:12px }
.post{ background:#2a2fb8; border-radius:22px; padding:12px 14px; margin:10px 0 }
.btn{ background:#5a7cff; color:white; padding:7px 16px; border-radius:20px; text-decoration:none; font-size:12px; border:none; display:inline-block }
.btn2{ background:rgba(255,255,255,0.18); color:white; padding:7px 16px; border-radius:20px; text-decoration:none; font-size:12px; border:1px solid rgba(255,255,255,0.25); display:inline-block }
.inp{ width:100%; padding:12px 16px; border-radius:28px; border:none; outline:none; box-sizing:border-box }
"""
@app.route('/static/uploads/<f>')
def upl(f): return send_from_directory('static/uploads', f)
@app.route('/', methods=['GET','POST'])
def home():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        t=request.form.get('content','').strip()
        if t: cur.execute('INSERT INTO posts (username,content,time,likes) VALUES (?,?,?,0)',(u,t,ist_now())); conn.commit()
    cur.execute('SELECT bio FROM users WHERE username=?',(u,)); r=cur.fetchone(); bio=r[0] if r and r[0] else "No bio yet. Click Edit Bio"
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(u,)); following=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM posts WHERE username=?',(u,)); pc=cur.fetchone()[0]
    cur.execute('SELECT id,username,content,time,likes FROM posts ORDER BY id DESC'); posts=cur.fetchall()
    posts_html=""
    for pid,uname,cont,tm,lk in posts:
        if uname!=u:
            cur.execute('SELECT 1 FROM follows WHERE follower=? AND following=?',(u,uname))
            is_f=cur.fetchone()
            fbtn=f"<a href='/unfollow/{uname}' class='btn2' style='float:right'>Following</a>" if is_f else f"<a href='/follow/{uname}' class='btn' style='float:right'>+ Follow</a>"
        else:
            fbtn="<span style='float:right;opacity:0.5;font-size:10px'>You</span>"
        posts_html+=f"<div class='post'><div style='display:flex;justify-content:space-between'><span style='font-size:11px;opacity:0.7'>@{uname} - {tm}</span>{fbtn}</div><div style='margin:8px 0'>{cont}</div><div style='font-size:11px'><a href='/like/{pid}' style='color:#00e5ff;text-decoration:none'>❤️ {lk}</a> <a href='/profile/{uname}' style='color:#ffb07c;text-decoration:none;margin-left:12px'>View</a></div></div>"
    conn.close()
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top'><b>@{u}</b><div style='display:flex;gap:8px'><a href='/edit_profile' class='btn2'>Edit</a><a href='/logout' class='btn2'>Out</a></div></div><div class='pill' style='text-align:center'><div style='font-size:42px'>👤</div><div style='font-weight:800;margin-top:6px'>@{u}</div><div style='font-size:11px;opacity:0.8;margin:6px 0'>{bio}</div><div class='stat'><span><b>{pc}</b> Posts</span><span><b>{followers}</b> Followers</span><span><b>{following}</b> Following</span></div><a href='/edit_profile' class='btn'>Edit Profile + Bio</a></div><form method='POST' class='pill' style='display:flex;gap:8px'><input name='content' class='inp' placeholder='What is happening?!' style='background:rgba(80,80,130,0.6);color:white'><button class='btn' style='border-radius:50%;width:42px;height:42px'>↑</button></form><div style='max-height:420px;overflow:auto'>{posts_html}</div></div></body></html>"
@app.route('/follow/<u2>')
def follow(u2):
    me=session.get('user')
    if me and me!=u2:
        conn=sqlite3.connect('users.db'); conn.execute('INSERT OR IGNORE INTO follows VALUES (?,?)',(me,u2)); conn.commit(); conn.close()
    return redirect('/')
@app.route('/unfollow/<u2>')
def unfollow(u2):
    me=session.get('user')
    conn=sqlite3.connect('users.db'); conn.execute('DELETE FROM follows WHERE follower=? AND following=?',(me,u2)); conn.commit(); conn.close()
    return redirect('/')
@app.route('/profile/<u2>')
def profile(u2):
    me=session.get('user')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT bio FROM users WHERE username=?',(u2,)); r=cur.fetchone()
    if not r: return "No user"
    bio=r[0] or "No bio"
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u2,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(u2,)); following=cur.fetchone()[0]
    cur.execute('SELECT content,time,likes FROM posts WHERE username=? ORDER BY id DESC',(u2,)); posts=cur.fetchall()
    if me!=u2:
        cur.execute('SELECT 1 FROM follows WHERE follower=? AND following=?',(me,u2))
        is_f=cur.fetchone()
        fbtn=f"<a href='/unfollow/{u2}' class='btn2'>Following</a>" if is_f else f"<a href='/follow/{u2}' class='btn'>+ Follow</a>"
    else: fbtn=""
    conn.close()
    ph="".join([f"<div class='post'>{c}<br><small>{t} ❤️{l}</small></div>" for c,t,l in posts])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top'><a href='/' class='btn2'>Back</a><b>@{u2}</b><span></span></div><div class='pill' style='text-align:center'><div style='font-size:42px'>👤</div><div><b>@{u2}</b></div><div style='font-size:11px'>{bio}</div><div class='stat'><span><b>{len(posts)}</b> Posts</span><span><b>{followers}</b> Followers</span><span><b>{following}</b> Following</span></div>{fbtn}</div>{ph}</div></body></html>"
@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    me=session.get('user')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        b=request.form.get('bio','')[:150]
        cur.execute('UPDATE users SET bio=? WHERE username=?',(b,me)); conn.commit(); conn.close(); return redirect('/')
    cur.execute('SELECT bio FROM users WHERE username=?',(me,)); r=cur.fetchone(); bio=r[0] if r and r[0] else ""; conn.close()
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top'><a href='/' class='btn2'>Back</a><b>Edit Bio</b><span></span></div><div class='pill'><form method='POST'><label style='font-size:11px'>Your Bio (150 chars)</label><textarea name='bio' maxlength='150' class='inp' style='height:90px;background:rgba(80,80,130,0.6);color:white;margin-top:8px'>{bio}</textarea><button class='btn' style='width:100%;margin-top:12px;padding:12px'>Save Bio</button></form></div></div></body></html>"
@app.route('/like/<int:pid>')
def like(pid): conn=sqlite3.connect('users.db'); conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,)); conn.commit(); conn.close(); return redirect('/')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password'); conn=sqlite3.connect('users.db'); cur=conn.cursor(); cur.execute('SELECT 1 FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok: session['user']=u; return redirect('/')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><h2 style='text-align:center;margin-top:60px'>Login</h2><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;color:black'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;color:black'><button class='btn' style='width:100%'>Login</button></form><a href='/signup' style='display:block;text-align:center;color:#0ff'>Signup</a></div></body></html>"
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        u=request.form.get('username'); e=request.form.get('email',''); p=request.form.get('password'); conn=sqlite3.connect('users.db')
        try: conn.execute('INSERT INTO users (username,email,password,bio) VALUES (?,?,?,?)',(u,e,p,'')); conn.commit(); conn.close(); return redirect('/login')
        except: conn.close(); return redirect('/signup')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><h2 style='text-align:center;margin-top:40px'>Create Account</h2><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;color:black'><input name='email' class='inp' placeholder='EMAIL' type='email' required style='margin-bottom:10px;color:black'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;color:black'><button class='btn' style='width:100%'>Sign up</button></form></div></body></html>"
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
