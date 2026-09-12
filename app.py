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
 conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, time TEXT)')
 conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))')
 conn.commit();conn.close()
init_db()
CSS="""
body{margin:0;min-height:100vh;background:#0a0a20;display:flex;justify-content:center;align-items:flex-start;padding:20px 0;font-family:Inter,sans-serif}
.phone{width:100%;max-width:360px;min-height:850px;background:linear-gradient(180deg,#2e40e6 0%, #1a2480 40%, #050516 100%);border-radius:35px;padding:15px;box-shadow:0 0 0 6px #e5e5e5, 0 20px 60px rgba(0,0,0,0.6);box-sizing:border-box;color:white;overflow:hidden}
.top-bar{display:flex;justify-content:space-between;align-items:center;padding:8px 5px}
.icon-btn{width:32px;height:32px;background:rgba(0,0,0,0.35);border-radius:50%;display:flex;justify-content:center;align-items:center;color:white;text-decoration:none}
.user-photo-box{width:100%;background:rgba(40,50,150,0.6);border-radius:30px;margin:10px 0;display:flex;flex-direction:column;align-items:center;padding:15px 10px;border:1px solid rgba(255,255,255,0.1)}
.user-photo-box img{width:90px;height:90px;object-fit:cover;border-radius:50%;border:3px solid #5a7cff}
.follow-stats{display:flex;gap:15px;margin:10px 0;font-size:12px}
.chat-pill{background:#2a2fb8;border-radius:20px;padding:12px 14px;margin:8px 0;width:100%;box-sizing:border-box}
.chat-pill img.post-media{width:100%;border-radius:15px;margin-top:8px;max-height:220px;object-fit:cover;display:block}
.chat-pill video.post-media{width:100%;border-radius:15px;margin-top:8px;max-height:280px;display:block}
.comment-box{background:rgba(0,0,0,0.25);border-radius:12px;padding:6px 10px;margin-top:6px;font-size:11px}
.comment-input{flex:1;background:rgba(255,255,255,0.1);border-radius:20px;padding:6px 10px;color:white;outline:none;font-size:11px}
.search-box{width:100%;margin:8px 0;display:flex;gap:5px}
.search-inp{flex:1;background:rgba(0,0,0,0.3);border-radius:30px;padding:10px 15px;color:white;outline:none}
.post-form{background:rgba(0,0,0,0.2);border-radius:20px;padding:10px;margin:10px 0}
.btn-follow{background:#5a7cff;border:none;padding:6px 14px;border-radius:20px;color:white;font-size:11px;text-decoration:none}
.btn-unfollow{background:rgba(255,255,255,0.2);border:1px solid rgba(255,255,255,0.3);padding:6px 14px;border-radius:20px;color:white;font-size:11px;text-decoration:none}
"""
PYcat >> app.py << 'PY'
@app.route('/static/uploads/<path:f>')
def up(f): return send_from_directory('static/uploads',f)
@app.route('/', methods=['GET','POST'])
def home():
 user=session.get('user')
 if not user: return redirect('/login')
 conn=sqlite3.connect('users.db');cur=conn.cursor()
 if request.method=='POST':
  txt=request.form.get('content','').strip()
  mf=request.files.get('media');mn=None;mt=None
  if mf and mf.filename:
   ext=mf.filename.rsplit('.',1)[-1].lower()
   mt='video' if ext in ['mp4','mov','webm'] else 'photo'
   mn=f"post_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{user}.{ext}"
   mf.save(os.path.join('static/uploads',mn))
  if txt or mn:
   cur.execute('INSERT INTO posts (username,content,time,likes,media,mtype) VALUES (?,?,?,?,?,?)',(user,txt,ist_now(),0,mn,mt));conn.commit()
 cur.execute('SELECT photo,bio FROM users WHERE username=?',(user,));r=cur.fetchone();photo=r[0] if r and r[0] else None;bio=r[1] if r and r[1] else "No bio yet. Click Edit ✏️"
 cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(user,));followers=cur.fetchone()[0]
 cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(user,));following=cur.fetchone()[0]
 cur.execute('SELECT COUNT(*) FROM posts WHERE username=?',(user,));pc=cur.fetchone()[0]
 cur.execute('SELECT id,username,content,time,likes,media,mtype FROM posts ORDER BY id DESC');posts=cur.fetchall()
 html=""
 for pid,uname,cont,tm,likes,media,mtype in posts:
  fb=""
  if uname!=user:
   cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(user,uname))
   fb=f"<a href='/unfollow/{uname}' class='btn-unfollow' style='float:right;margin-left:5px'>Following ✓</a>" if cur.fetchone() else f"<a href='/follow/{uname}' class='btn-follow' style='float:right;margin-left:5px'>+ Follow</a>"
  mh=""
  if media:
   if mtype=='video': mh=f"<video class='post-media' controls src='/static/uploads/{media}'></video>"
   else: mh=f"<img class='post-media' src='/static/uploads/{media}'>"
  html+=f"<div class='chat-pill'><div style='display:flex;justify-content:space-between'><b style='font-size:10px;opacity:0.7'>@{uname} • {tm}</b><span>{fb}</span></div><div style='margin-top:6px'>{cont}</div>{mh}<div style='margin-top:8px'><a href='/like/{pid}' style='color:#00e5ff;text-decoration:none'>❤️{likes}</a> <a href='/profile/{uname}' style='color:#ffaa77;text-decoration:none;font-size:10px;margin-left:10px'>View @{uname}</a></div></div>"
 conn.close()
 if not html: html="<div class='chat-pill' style='opacity:0.5;text-align:center'>No posts yet</div>"
 ph=f"<img src='/static/uploads/{photo}'>" if photo else "<div style='font-size:40px'>👤</div>"
 admin=f"<a class='icon-btn' href='/admin' style='background:#ffaa00'>👑</a>" if user==ADMIN_USER else ""
 return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><div style='display:flex;gap:6px;align-items:center'><div style='font-weight:bold'>@{user}</div></div><div style='display:flex;gap:6px'>{admin}<a class='icon-btn' href='/edit_profile'>✏️</a><a class='icon-btn' href='/logout'>⎋</a></div></div><div class='user-photo-box'>{ph}<div style='font-weight:bold;margin-top:8px'>@{user}</div><div style='font-size:11px;opacity:0.8;margin:5px;text-align:center'>{bio}</div><div class='follow-stats'><div><b>{pc}</b> Posts</div><div><b>{followers}</b> Followers</div><div><b>{following}</b> Following</div></div><div style='display:flex;gap:6px'><a href='/edit_profile' class='btn-follow'>✏️ Edit Profile</a><form action='/upload_photo' method='POST' enctype='multipart/form-data'><label style='background:rgba(255,255,255,0.2);padding:6px 12px;border-radius:20px;font-size:11px'>📷 Photo<input type='file' name='photo' accept='image/*' hidden onchange='this.form.submit()'></label></form></div></div><form class='post-form' method='POST' enctype='multipart/form-data'><div style='display:flex;gap:5px'><input name='content' placeholder='What is happening?!' style='flex:1;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:10px 15px;color:white;outline:none'><button style='background:#5a7cff;border:none;border-radius:50%;width:38px;height:38px;color:white'>↑</button></div><label style='background:rgba(255,255,255,0.15);padding:6px 12px;border-radius:20px;font-size:11px;margin-top:8px;display:inline-block'>📷 Photo/Video<input type='file' name='media' accept='image/*,video/*' hidden></label></form><div style='max-height:320px;overflow-y:auto'>{html}</div></div></body></html>"

@app.route('/follow/<u>')
def follow(u):
 me=session.get('user')
 if not me or me==u: return redirect('/')
 conn=sqlite3.connect('users.db')
 try: conn.execute('INSERT INTO follows VALUES (?,?)',(me,u));conn.commit()
 except: pass
 conn.close();return redirect(request.referrer or '/')
@app.route('/unfollow/<u>')
def unfollow(u):
 me=session.get('user')
 conn=sqlite3.connect('users.db');conn.execute('DELETE FROM follows WHERE follower=? AND following=?',(me,u));conn.commit();conn.close();return redirect(request.referrer or '/')
@app.route('/profile/<u>')
def profile(u):
 me=session.get('user')
 if not me: return redirect('/login')
 conn=sqlite3.connect('users.db');cur=conn.cursor()
 cur.execute('SELECT photo,bio FROM users WHERE username=?',(u,));r=cur.fetchone()
 if not r: return "User not found <a href='/'>Back</a>"
 photo,bio=r;bio=bio or "No bio"
 cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u,));followers=cur.fetchone()[0]
 cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(u,));following=cur.fetchone()[0]
 cur.execute('SELECT id,content,time,likes,media,mtype FROM posts WHERE username=? ORDER BY id DESC',(u,));posts=cur.fetchall()
 cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(me,u));is_f=cur.fetchone()
 conn.close()
 ph_html=""
 for pid,c,t,lk,m,mt in posts:
  mh=""
  if m:
   if mt=='video': mh=f"<video class='post-media' controls src='/static/uploads/{m}'></video>"
   else: mh=f"<img class='post-media' src='/static/uploads/{m}'>"
  ph_html+=f"<div class='chat-pill'>{c}<br><small>{t} ❤️{lk}</small>{mh}</div>"
 if not ph_html: ph_html="<div class='chat-pill' style='opacity:0.5'>No posts</div>"
 fb=""
 if u!=me:
  fb=f"<a href='/unfollow/{u}' class='btn-unfollow'>Following ✓</a>" if is_f else f"<a href='/follow/{u}' class='btn-follow'>+ Follow</a>"
 img=f"<img src='/static/uploads/{photo}'>" if photo else "<div style='font-size:40px'>👤</div>"
 return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><a class='icon-btn' href='/'>←</a><b>@{u}</b><div style='width:32px'></div></div><div class='user-photo-box'>{img}<div style='font-weight:bold;margin-top:8px'>@{u}</div><div style='font-size:11px;opacity:0.8'>{bio}</div><div class='follow-stats'><div><b>{len(posts)}</b> Posts</div><div><b>{followers}</b> Followers</div><div><b>{following}</b> Following</div></div>{fb}</div><div style='max-height:400px;overflow:auto'>{ph_html}</div></div></body></html>"
PYcat >> app.py << 'PY'
@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
 me=session.get('user')
 if not me: return redirect('/login')
 conn=sqlite3.connect('users.db');cur=conn.cursor()
 if request.method=='POST':
  bio=request.form.get('bio','')[:150];email=request.form.get('email','')
  cur.execute('UPDATE users SET bio=?, email=? WHERE username=?',(bio,email,me));conn.commit();conn.close();return redirect('/')
 cur.execute('SELECT email,bio FROM users WHERE username=?',(me,));r=cur.fetchone();email=r[0] if r else "";bio=r[1] if r and r[1] else "";conn.close()
 return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><a class='icon-btn' href='/'>←</a><b>✏️ Edit Profile</b></div><form method='POST' style='padding:20px 10px'><label style='font-size:11px;opacity:0.7'>Email</label><input name='email' value='{email}' style='width:100%;background:rgba(80,80,130,0.5);border-radius:20px;padding:12px;color:white;box-sizing:border-box;margin:6px 0 15px 0'><label style='font-size:11px;opacity:0.7'>Bio (150 chars)</label><textarea name='bio' maxlength='150' style='width:100%;height:80px;background:rgba(80,80,130,0.5);border-radius:20px;padding:12px;color:white;box-sizing:border-box;margin:6px 0'>{bio}</textarea><button style='width:100%;background:linear-gradient(90deg,#6a8cff,#4a5cff);border:none;padding:14px;border-radius:10px;font-weight:800;color:#0a0a2a;margin-top:15px'>Save ✅</button></form></div></body></html>"
@app.route('/admin', methods=['GET','POST'])
def admin():
 user=session.get('user')
 if user!=ADMIN_USER: return "Not Admin <a href='/'>Back</a>"
 if request.method=='POST':
  if request.form.get('admin_pass','')==ADMIN_PASS: session['is_admin']=True
  else: return "Wrong <a href='/admin'>Try</a>"
 if not session.get('is_admin'): return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone' style='text-align:center;padding:30px'><h3>Admin Password</h3><form method='POST'><input name='admin_pass' type='password' placeholder='Password' style='width:100%;padding:14px;border-radius:30px;color:black;text-align:center' required><button style='width:100%;background:#ffaa00;padding:14px;border-radius:10px;margin-top:12px'>Unlock</button></form></div></body></html>"
 conn=sqlite3.connect('users.db');cur=conn.cursor();cur.execute('SELECT username,email FROM users');users=cur.fetchall();conn.close()
 users_html="".join([f"<div style='background:rgba(255,255,255,0.1);border-radius:15px;padding:12px;margin:8px 0'><b>@{u}</b> - {e} <a href='/admin_del_user/{u}' style='color:#ff6b6b;float:right'>Delete</a></div>" for u,e in users])
 return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><a class='icon-btn' href='/'>←</a><b>ADMIN</b><a class='icon-btn' href='/admin_logout'>🔒</a></div>{users_html}</div></body></html>"
@app.route('/admin_logout')
def admin_logout(): session.pop('is_admin',None);return redirect('/admin')
@app.route('/admin_del_user/<u>')
def admin_del_user(u):
 if session.get('user')!=ADMIN_USER or not session.get('is_admin'): return redirect('/admin')
 if u!=ADMIN_USER: conn=sqlite3.connect('users.db');conn.execute('DELETE FROM users WHERE username=?',(u,));conn.execute('DELETE FROM posts WHERE username=?',(u,));conn.execute('DELETE FROM follows WHERE follower=? OR following=?',(u,u));conn.commit();conn.close()
 return redirect('/admin')
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
 user=session.get('user');f=request.files.get('photo')
 if f and f.filename:
  ext=f.filename.rsplit('.',1)[-1].lower();fname=f"{user}.{ext}";f.save(os.path.join('static/uploads',fname))
  conn=sqlite3.connect('users.db');conn.execute('UPDATE users SET photo=? WHERE username=?',(fname,user));conn.commit();conn.close()
 return redirect('/')
@app.route('/comment/<int:pid>', methods=['POST'])
def comment(pid):
 user=session.get('user');c=request.form.get('cmt')
 if c: conn=sqlite3.connect('users.db');conn.execute('INSERT INTO comments VALUES (NULL,?,?,?,?)',(pid,user,c,ist_now()));conn.commit();conn.close()
 return redirect('/')
@app.route('/like/<int:pid>')
def like(pid): conn=sqlite3.connect('users.db');conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,));conn.commit();conn.close();return redirect('/')
@app.route('/delete/<int:pid>')
def delete(pid):
 user=session.get('user');conn=sqlite3.connect('users.db');cur=conn.cursor();cur.execute('SELECT username FROM posts WHERE id=?',(pid,));r=cur.fetchone()
 if r and r[0]==user: cur.execute('DELETE FROM posts WHERE id=?',(pid,));conn.commit()
 conn.close();return redirect('/')
@app.route('/signup', methods=['GET','POST'])
def signup():
 if request.method=='POST':
  u=request.form.get('username');e=request.form.get('email');p=request.form.get('password');conn=sqlite3.connect('users.db')
  try: conn.execute('INSERT INTO users VALUES (?,?,?,?,?)',(u,e,p,None,None));conn.commit();conn.close();return redirect('/login')
  except: conn.close();return redirect('/signup')
 return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><h2 style='text-align:center;margin-top:40px'>Create Account</h2><form method='POST'><input style='width:100%;padding:14px;margin-bottom:12px;border-radius:30px;color:black;box-sizing:border-box' name='username' placeholder='NAME' required><input style='width:100%;padding:14px;margin-bottom:12px;border-radius:30px;color:black;box-sizing:border-box' name='email' placeholder='EMAIL' type='email' required><input style='width:100%;padding:14px;margin-bottom:12px;border-radius:30px;color:black;box-sizing:border-box' name='password' type='password' placeholder='PASSWORD' required><button style='width:100%;background:#6a8cff;padding:14px;border-radius:10px;margin-top:15px'>Sign up</button></form></div></body></html>"
@app.route('/login', methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=request.form.get('username');p=request.form.get('password');conn=sqlite3.connect('users.db');cur=conn.cursor();cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p));ok=cur.fetchone();conn.close()
  if ok: session['user']=u;return redirect('/')
 return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><h2 style='text-align:center;margin-top:80px'>Login</h2><form method='POST'><input style='width:100%;padding:14px;margin-bottom:12px;border-radius:30px;color:black;box-sizing:border-box' name='username' placeholder='NAME' required><input style='width:100%;padding:14px;margin-bottom:12px;border-radius:30px;color:black;box-sizing:border-box' name='password' type='password' placeholder='PASSWORD' required><button style='width:100%;background:#6a8cff;padding:14px;border-radius:10px;margin-top:15px'>Login</button></form><a href='/signup' style='display:block;text-align:center;margin-top:15px;color:#0ff'>Signup!</a></div></body></html>"
@app.route('/logout')
def logout(): session.clear();return redirect('/login')
