from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, datetime, os
app = Flask(__name__)
app.secret_key = "babu_pro_123"
os.makedirs('static/uploads', exist_ok=True)
ADMIN_USER = "Sayan"
ADMIN_PASS = "Sayan@123"

def ist_now():
    # IST = UTC + 5:30
    utc = datetime.datetime.utcnow()
    ist = utc + datetime.timedelta(hours=5, minutes=30)
    return ist.strftime("%I:%M %p - %d/%m")

def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, photo TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0, media TEXT, mtype TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, time TEXT)')
    try: conn.execute('ALTER TABLE users ADD COLUMN photo TEXT')
    except: pass
    try: conn.execute('ALTER TABLE posts ADD COLUMN media TEXT')
    except: pass
    try: conn.execute('ALTER TABLE posts ADD COLUMN mtype TEXT')
    except: pass
    conn.commit(); conn.close()
init_db()

CSS = """
body{margin:0;min-height:100vh;background:#0a0a20;display:flex;justify-content:center;align-items:flex-start;padding:20px 0;font-family:Inter,sans-serif}
.phone{width:100%;max-width:360px;min-height:850px;background:linear-gradient(180deg,#2e40e6 0%, #1a2480 40%, #050516 100%);border-radius:35px;padding:15px;box-shadow:0 0 0 6px #e5e5e5, 0 20px 60px rgba(0,0,0,0.6);position:relative;box-sizing:border-box;color:white;overflow:hidden}
.top-bar{display:flex;justify-content:space-between;align-items:center;padding:8px 5px;width:100%;box-sizing:border-box}
.top-left{display:flex;gap:6px;align-items:center}
.top-right{display:flex;gap:6px;align-items:center}
.icon-btn{width:32px;height:32px;min-width:32px;background:rgba(0,0,0,0.35);border-radius:50%;display:flex;justify-content:center;align-items:center;color:white;font-size:13px;border:none;cursor:pointer;text-decoration:none}
.user-photo-box{width:100%;height:190px;background:rgba(40,50,150,0.6);border-radius:30px;margin:10px 0;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;position:relative;border:1px solid rgba(255,255,255,0.1);box-sizing:border-box}
.user-photo-box img{width:100%;height:100%;object-fit:cover;border-radius:30px}
.chat-pill{background:#2a2fb8;border-radius:20px;padding:12px 14px;margin:8px 0;width:100%;box-sizing:border-box;font-size:13px;word-wrap:break-word}
.chat-pill img.post-media{width:100%;border-radius:15px;margin-top:8px;max-height:220px;object-fit:cover;display:block}
.chat-pill video.post-media{width:100%;border-radius:15px;margin-top:8px;max-height:280px;display:block}
.comment-box{background:rgba(0,0,0,0.25);border-radius:12px;padding:6px 10px;margin-top:6px;font-size:11px;word-wrap:break-word}
.comment-input{flex:1;background:rgba(255,255,255,0.1);border:1px dashed rgba(255,255,255,0.2);border-radius:20px;padding:6px 10px;color:white;outline:none;font-size:11px;min-width:0}
.search-box{width:100%;margin:8px 0;display:flex;gap:5px;box-sizing:border-box}
.search-inp{flex:1;min-width:0;background:rgba(0,0,0,0.3);border:1px dashed rgba(255,255,255,0.2);border-radius:30px;padding:10px 15px;color:white;outline:none;font-size:12px}
.post-form{background:rgba(0,0,0,0.2);border-radius:20px;padding:10px;margin:10px 0;width:100%;box-sizing:border-box}
.admin-card{background:rgba(255,255,255,0.1);border-radius:15px;padding:12px;margin:8px 0;font-size:12px;word-wrap:break-word}
"""
@app.route('/static/uploads/<path:f>')
def up(f): return send_from_directory('static/uploads', f)
@app.route('/', methods=['GET','POST'])
def home():
    user=session.get('user')
    if not user: return redirect('/login')
    q=request.args.get('q','').strip()
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        txt=request.form.get('content','').strip()
        media_file=request.files.get('media')
        media_name=None; mtype=None
        if media_file and media_file.filename:
            ext=media_file.filename.rsplit('.',1)[-1].lower()
            mtype='video' if ext in ['mp4','mov','avi','mkv','webm'] else 'photo'
            media_name=f"post_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{user}.{ext}"
            media_file.save(os.path.join('static/uploads',media_name))
        if txt or media_name:
            now=ist_now()
            cur.execute('INSERT INTO posts (username,content,time,likes,media,mtype) VALUES (?,?,?,?,?,?)',(user,txt,now,0,media_name,mtype))
            conn.commit()
    cur.execute('SELECT photo FROM users WHERE username=?',(user,)); pr=cur.fetchone(); photo=pr[0] if pr and pr[0] else None
    if q:
        cur.execute('SELECT id,username,content,time,likes,media,mtype FROM posts WHERE username LIKE? OR content LIKE? ORDER BY id DESC', (f'%{q}%', f'%{q}%'))
    else:
        cur.execute('SELECT id,username,content,time,likes,media,mtype FROM posts ORDER BY id DESC')
    posts=cur.fetchall()
    chat_html=""
    for pid,uname,cont,tm,likes,media,mtype in posts:
        cur.execute('SELECT username,content,time FROM comments WHERE post_id=? ORDER BY id ASC',(pid,))
        comms=cur.fetchall()
        comm_html="".join([f"<div class='comment-box'><b>@{cu}</b>: {cc} <span style='opacity:0.5;float:right'>{ct}</span></div>" for cu,cc,ct in comms])
        del_btn = f"<a href='/delete/{pid}' style='color:#ff8a8a;float:right;text-decoration:none'>✕</a>" if uname==user or user==ADMIN_USER else ""
        media_html=""
        if media:
            if mtype=='video': media_html=f"<video class='post-media' controls src='/static/uploads/{media}'></video>"
            else: media_html=f"<img class='post-media' src='/static/uploads/{media}'>"
        chat_html+=f"<div class='chat-pill'><div style='display:flex;justify-content:space-between'><b style='font-size:10px;opacity:0.7'>@{uname} • {tm} 🇮🇳</b>{del_btn}</div><div style='margin-top:6px'>{cont}</div>{media_html}<div style='margin-top:8px'><a href='/like/{pid}' style='color:#00e5ff;text-decoration:none'>❤️{likes}</a></div>{comm_html}<form action='/comment/{pid}' method='POST' style='margin-top:6px;display:flex;gap:5px'><input class='comment-input' name='cmt' placeholder='Add comment...' required><button style='background:#5a7cff;border:none;border-radius:15px;padding:5px 10px;color:white;font-size:10px;min-width:45px'>Reply</button></form></div>"
    conn.close()
    if not chat_html: chat_html="<div class='chat-pill' style='opacity:0.5;text-align:center'>No posts yet. Upload photo/video!</div>"
    photo_html = f"<img src='/static/uploads/{photo}'>" if photo else f"<div style='font-size:40px'>👤</div><div style='font-size:12px'>@{user}</div>"
    admin_link = f"<a class='icon-btn' href='/admin' style='background:#ffaa00'>👑</a>" if user==ADMIN_USER else ""
    return f"""<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'>
    <div class='top-bar'><div class='top-left'><a class='icon-btn' href='#' onclick="document.getElementById('searchArea').style.display='flex';return false">🔍</a><div style='font-weight:bold;font-size:14px'>@{user}</div></div><div class='top-right'>{admin_link}<a class='icon-btn' href='/'>🌙</a><a class='icon-btn' href='/logout'>⎋</a></div></div>
    <div id='searchArea' class='search-box' style='display:{"flex" if q else "none"}'><form method='GET' style='display:flex;gap:5px;width:100%'><input class='search-inp' name='q' value='{q}' placeholder='Search...'><button class='icon-btn' style='width:42px;min-width:42px'>Go</button><a class='icon-btn' href='/'>✕</a></form></div>
    <div class='user-photo-box'>{photo_html}<form action='/upload_photo' method='POST' enctype='multipart/form-data' style='position:absolute;bottom:8px;right:10px'><label style='background:#5a7cff;padding:5px 10px;border-radius:15px;font-size:10px;cursor:pointer'>📷 Change<input type='file' name='photo' accept='image/*' hidden onchange='this.form.submit()'></label></form></div>
    <div style='text-align:center;font-size:10px;opacity:0.6'>{len(posts)} posts • Babu Pro • @ {user}</div>
    <form class='post-form' method='POST' enctype='multipart/form-data'><div style='display:flex;gap:5px'><input name='content' placeholder='Type a message...' style='flex:1;min-width:0;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:10px 15px;color:white;outline:none'><button style='background:#5a7cff;border:none;border-radius:50%;width:38px;min-width:38px;height:38px;color:white'>↑</button></div><div style='margin-top:8px;display:flex;gap:8px;align-items:center'><label style='background:rgba(255,255,255,0.15);padding:6px 12px;border-radius:20px;font-size:11px;cursor:pointer'>📷 Photo/Video<input type='file' name='media' accept='image/*,video/*' hidden></label><span style='font-size:10px;opacity:0.6'>IST 🇮🇳</span></div></form>
    <div style='max-height:380px;overflow-y:auto;padding-right:2px'>{chat_html}</div>
    </div></body></html>"""

@app.route('/admin', methods=['GET','POST'])
def admin():
    user=session.get('user')
    if user!=ADMIN_USER: return "<html><body style='background:#111;color:white;text-align:center;padding:50px'><h1>⛔ Not Admin</h1><a href='/'>Back</a></body></html>"
    if request.method=='POST':
        pw=request.form.get('admin_pass','')
        if pw==ADMIN_PASS: session['is_admin']=True
        else: return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div style='text-align:center;padding:40px'><h2>❌ Wrong Password!</h2><a href='/admin' style='color:#5a7cff'>Try Again</a></div></div></body></html>"
    if not session.get('is_admin'):
        return f"""<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'>
        <div class='top-bar'><div class='top-left'><a class='icon-btn' href='/'>←</a><b>👑 ADMIN LOCK</b></div></div>
        <div style='text-align:center;padding:30px 10px'>
        <div style='font-size:50px'>🔒</div><h3>Admin Password Required</h3><p style='font-size:12px;opacity:0.7'>Only owner can access</p>
        <form method='POST' style='margin-top:20px'><input name='admin_pass' type='password' placeholder='Enter Admin Password' style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;color:white;box-sizing:border-box;text-align:center' required><button style='width:100%;background:linear-gradient(90deg,#ffaa00,#ff6a00);border:none;padding:14px;border-radius:10px;font-weight:800;color:black;margin-top:12px;cursor:pointer'>Unlock Admin 🔓</button></form>
        </div></div></body></html>"""
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT username,email,photo FROM users'); users=cur.fetchall()
    cur.execute('SELECT COUNT(*), SUM(likes) FROM posts'); stats=cur.fetchone(); total_posts=stats[0] or 0; total_likes=stats[1] or 0
    cur.execute('SELECT id,username,content,time,media FROM posts ORDER BY id DESC'); posts=cur.fetchall()
    conn.close()
    users_html="".join([f"<div class='admin-card'><b>@{u}</b> • {e} <a href='/admin_del_user/{u}' style='color:#ff6b6b;float:right'>Delete</a></div>" for u,e,ph in users])
    posts_html="".join([f"<div class='admin-card'><b>#{pid} @{un}</b> • {tm}<br>{ct[:50]} <a href='/delete/{pid}' style='color:#ff6b6b;float:right'>✕</a></div>" for pid,un,ct,tm,md in posts[:20]])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><div class='top-left'><a class='icon-btn' href='/'>←</a><b>👑 ADMIN</b></div><div class='top-right'><a class='icon-btn' href='/admin_logout'>🔒</a></div></div><div style='background:linear-gradient(90deg,#ffaa00,#ff6a00);padding:15px;border-radius:20px;margin:10px 0;text-align:center;color:black'><div style='font-size:26px;font-weight:800'>{total_posts} Posts</div><div style='font-size:13px'>{len(users)} Users • {total_likes} Likes</div></div><h3 style='font-size:12px'>USERS ({len(users)})</h3><div style='max-height:200px;overflow:auto'>{users_html}</div><h3 style='font-size:12px;margin-top:15px'>RECENT POSTS</h3><div style='max-height:300px;overflow:auto'>{posts_html}</div></div></body></html>"

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin',None); return redirect('/admin')
@app.route('/admin_del_user/<u>')
def admin_del_user(u):
    if session.get('user')!=ADMIN_USER or not session.get('is_admin'): return redirect('/admin')
    if u!=ADMIN_USER:
        conn=sqlite3.connect('users.db'); conn.execute('DELETE FROM users WHERE username=?',(u,)); conn.execute('DELETE FROM posts WHERE username=?',(u,)); conn.commit(); conn.close()
    return redirect('/admin')
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    user=session.get('user')
    if not user: return redirect('/login')
    f=request.files.get('photo')
    if f and f.filename:
        ext=f.filename.rsplit('.',1)[-1].lower(); fname=f"{user}.{ext}"; f.save(os.path.join('static/uploads',fname))
        conn=sqlite3.connect('users.db'); conn.execute('UPDATE users SET photo=? WHERE username=?',(fname,user)); conn.commit(); conn.close()
    return redirect('/')
@app.route('/comment/<int:pid>', methods=['POST'])
def comment(pid):
    user=session.get('user')
    if not user: return redirect('/login')
    c=request.form.get('cmt')
    if c:
        now=ist_now()
        conn=sqlite3.connect('users.db'); conn.execute('INSERT INTO comments VALUES (NULL,?,?,?,?)',(pid,user,c,now)); conn.commit(); conn.close()
    return redirect('/')
@app.route('/like/<int:pid>')
def like(pid):
    if not session.get('user'): return redirect('/login')
    conn=sqlite3.connect('users.db'); conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,)); conn.commit(); conn.close(); return redirect('/')
@app.route('/delete/<int:pid>')
def delete(pid):
    user=session.get('user'); conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT username FROM posts WHERE id=?',(pid,)); row=cur.fetchone()
    if row and (row[0]==user or (user==ADMIN_USER and session.get('is_admin'))):
        cur.execute('DELETE FROM posts WHERE id=?',(pid,)); cur.execute('DELETE FROM comments WHERE post_id=?',(pid,)); conn.commit()
    conn.close(); return redirect('/')
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        u=request.form.get('username'); e=request.form.get('email'); p=request.form.get('password')
        conn=sqlite3.connect('users.db')
        try: conn.execute('INSERT INTO users VALUES (?,?,?,NULL)',(u,e,p)); conn.commit(); conn.close(); return redirect('/login')
        except: conn.close(); return redirect('/signup')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><a class='icon-btn' href='/login'>←</a></div><h2 style='text-align:center;margin-top:40px'>Create Account</h2><form method='POST'><input style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;margin-bottom:12px;color:white;box-sizing:border-box' name='username' placeholder='NAME' required><input style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;margin-bottom:12px;color:white;box-sizing:border-box' name='email' placeholder='EMAIL' type='email' required><input style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;margin-bottom:12px;color:white;box-sizing:border-box' name='password' type='password' placeholder='PASSWORD' required><button style='width:100%;background:linear-gradient(90deg,#6a8cff,#4a5cff);border:none;padding:14px;border-radius:10px;font-weight:800;color:#0a0a2a;margin-top:15px'>Sign up</button></form></div></body></html>"
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password')
        conn=sqlite3.connect('users.db'); cur=conn.cursor(); cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok: session['user']=u; return redirect('/')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><h2 style='text-align:center;margin-top:80px;font-size:32px'>Login</h2><p style='text-align:center;opacity:0.7;font-size:12px'>Sign in to continue.</p><form method='POST'><input style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;margin-bottom:12px;color:white;box-sizing:border-box' name='username' placeholder='NAME' required><input style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;margin-bottom:12px;color:white;box-sizing:border-box' name='password' type='password' placeholder='PASSWORD' required><button style='width:100%;background:linear-gradient(90deg,#6a8cff,#4a5cff);border:none;padding:14px;border-radius:10px;font-weight:800;color:#0a0a2a;margin-top:15px'>Login</button></form><a href='/signup' style='display:block;text-align:center;margin-top:15px;color:#00aaff;text-decoration:none;font-size:12px'>Signup!</a></div></body></html>"
@app.route('/logout')
def logout():
    session.clear(); return redirect('/login')
