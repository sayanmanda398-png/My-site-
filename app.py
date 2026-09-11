from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, datetime, os, base64
app = Flask(__name__)
app.secret_key = "babu_pro_123"
os.makedirs('static/uploads', exist_ok=True)

def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, photo TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0)')
    conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, time TEXT)')
    # add photo column if old db
    try: conn.execute('ALTER TABLE users ADD COLUMN photo TEXT')
    except: pass
    conn.commit(); conn.close()
init_db()

CSS = """
:root{--bg1:#2e40e6;--bg2:#1a2480;--bg3:#050516;--card:#2a2fb8;--text:#fff}
.light{--bg1:#e8eaff;--bg2:#aab4ff;--bg3:#ffffff;--card:#d0d6ff;--text:#0a0a2a}
body{margin:0;min-height:100vh;background:linear-gradient(180deg,var(--bg1) 0%, var(--bg2) 40%, var(--bg3) 100%);display:flex;justify-content:center;align-items:center;font-family:Inter,sans-serif;transition:0.4s}
.phone{width:370px;min-height:850px;background:linear-gradient(180deg,var(--bg1) 0%, var(--bg2) 40%, var(--bg3) 100%);border-radius:35px;padding:20px 18px;box-shadow:0 0 0 8px #e5e5e5, 0 20px 60px rgba(0,0,0,0.6);position:relative;box-sizing:border-box;color:var(--text);transition:0.4s}
h1{color:var(--text);text-align:center;font-size:34px;margin-top:60px;font-weight:800}
.sub{color:var(--text);opacity:0.7;text-align:center;font-size:12px;margin-bottom:20px}
.inp{width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;margin-bottom:12px;color:white;box-sizing:border-box;outline:none}
.light.inp{color:black;background:rgba(255,255,255,0.8)}
.inp::placeholder{color:rgba(255,255,255,0.35)}
.btn{width:100%;background:linear-gradient(90deg,#6a8cff,#4a5cff);border:none;padding:14px;border-radius:10px;font-weight:800;cursor:pointer;box-shadow:-5px 3px 0 #00e5ff, 4px 5px 0 #ff00e5;color:#0a0a2a;margin-top:15px}
.top-bar{display:flex;justify-content:space-between;align-items:center;padding:10px 5px}
.icon-btn{width:36px;height:36px;background:rgba(0,0,0,0.3);border-radius:50%;display:flex;justify-content:center;align-items:center;color:white;font-size:16px;border:none;cursor:pointer;text-decoration:none}
.user-photo-box{width:92%;height:200px;background:rgba(40,50,150,0.6);border-radius:35px;margin:10px auto;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;position:relative;border:1px solid rgba(255,255,255,0.1)}
.user-photo-box img{width:100%;height:100%;object-fit:cover;border-radius:35px}
.chat-pill{background:var(--card);border-radius:20px;padding:12px 16px;margin:8px auto;width:88%;color:var(--text);font-size:13px;transition:0.3s}
.comment-box{background:rgba(0,0,0,0.25);border-radius:12px;padding:6px 10px;margin-top:6px;font-size:11px}
.light.comment-box{background:rgba(0,0,0,0.08)}
.comment-input{width:65%;background:rgba(255,255,255,0.1);border:1px dashed rgba(255,255,255,0.2);border-radius:20px;padding:6px 10px;color:var(--text);outline:none;font-size:11px}
.search-box{width:92%;margin:10px auto;display:flex;gap:5px}
.search-inp{flex:1;background:rgba(0,0,0,0.3);border:1px dashed rgba(255,255,255,0.2);border-radius:30px;padding:10px 15px;color:white;outline:none;font-size:12px}
"""

@app.route('/static/uploads/<path:f>')
def up(f): return send_from_directory('static/uploads', f)

@app.route('/', methods=['GET','POST'])
def home():
    user=session.get('user')
    if not user: return redirect('/login')
    q=request.args.get('q','').strip()
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST' and user:
        c=request.form.get('content')
        if c:
            now=datetime.datetime.now().strftime("%I:%M %p")
            cur.execute('INSERT INTO posts VALUES (NULL,?,?,?,0)',(user,c,now)); conn.commit()
    cur.execute('SELECT photo FROM users WHERE username=?',(user,)); prow=cur.fetchone(); photo=prow[0] if prow and prow[0] else None
    if q:
        cur.execute('SELECT id,username,content,time,likes FROM posts WHERE username LIKE? OR content LIKE? ORDER BY id DESC', (f'%{q}%', f'%{q}%'))
    else:
        cur.execute('SELECT id,username,content,time,likes FROM posts ORDER BY id DESC')
    posts=cur.fetchall()

    chat_html=""
    for pid,uname,cont,tm,likes in posts:
        cur.execute('SELECT username,content,time FROM comments WHERE post_id=? ORDER BY id ASC',(pid,))
        comms=cur.fetchall()
        comm_html="".join([f"<div class='comment-box'><b>@{cu}</b>: {cc} <span style='opacity:0.5;float:right'>{ct}</span></div>" for cu,cc,ct in comms])
        del_btn = f"<a href='/delete/{pid}' style='color:#ff8a8a;float:right;text-decoration:none;font-size:11px'>✕</a>" if uname==user else ""
        chat_html+=f"<div class='chat-pill'><div style='display:flex;justify-content:space-between'><b style='font-size:10px;opacity:0.7'>@{uname} • {tm}</b>{del_btn}</div><div style='margin-top:6px'>{cont} <a href='/like/{pid}' style='color:#00e5ff;text-decoration:none;float:right'>❤️{likes}</a></div>{comm_html}<form action='/comment/{pid}' method='POST' style='margin-top:6px;display:flex;gap:5px'><input class='comment-input' name='cmt' placeholder='Add comment...' required><button style='background:#5a7cff;border:none;border-radius:15px;padding:5px 10px;color:white;font-size:10px'>Reply</button></form></div>"
    conn.close()
    if not chat_html: chat_html="<div class='chat-pill' style='opacity:0.5;text-align:center'>No chats yet. Try search or post!</div>"

    photo_html = f"<img src='/static/uploads/{photo}'>" if photo else f"<div style='font-size:40px'>👤</div><div>@{user}</div>"

    return f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head>
    <body id='body'><div class='phone' id='phone'>
    <div class='top-bar'>
        <a class='icon-btn' href='#' onclick="document.getElementById('searchArea').style.display='flex';return false">🔍</a>
        <div style='font-weight:bold'>@{user}</div>
        <div style='display:flex;gap:5px'><button class='icon-btn' onclick="toggleTheme()">🌙</button><a class='icon-btn' href='/logout'>⎋</a></div>
    </div>
    <div id='searchArea' class='search-box' style='display:{"flex" if q else "none"}'>
        <form method='GET' style='display:flex;gap:5px;width:100%'><input class='search-inp' name='q' value='{q}' placeholder='Search users or posts...'><button class='icon-btn' style='width:45px'>Go</button><a class='icon-btn' href='/'>✕</a></form>
    </div>
    <div class='user-photo-box'>
        {photo_html}
        <form action='/upload_photo' method='POST' enctype='multipart/form-data' style='position:absolute;bottom:8px;right:10px'><label style='background:#5a7cff;padding:5px 10px;border-radius:15px;font-size:10px;cursor:pointer'>📷 Change<input type='file' name='photo' accept='image/*' hidden onchange='this.form.submit()'></label></form>
    </div>
    <div style='text-align:center;font-size:10px;opacity:0.6;margin-top:5px'>{len(posts)} posts • Babu Pro • @ {user}</div>
    <form method='POST' style='width:92%;margin:10px auto;display:flex;gap:5px'><input name='content' placeholder='Type a message...' required style='flex:1;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:12px 18px;color:white;outline:none'><button style='background:#5a7cff;border:none;border-radius:50%;width:42px;height:42px;color:white'>↑</button></form>
    <div style='max-height:350px;overflow-y:auto'>{chat_html}</div>
    </div>
    <script>
    function toggleTheme(){{ let b=document.getElementById('body'); let p=document.getElementById('phone'); b.classList.toggle('light'); p.classList.toggle('light'); localStorage.setItem('theme', b.classList.contains('light')?'light':'dark'); }}
    if(localStorage.getItem('theme')=='light'){{ document.getElementById('body').classList.add('light'); document.getElementById('phone').classList.add('light'); }}
    </script>
    </body></html>
    """

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    user=session.get('user')
    if not user: return redirect('/login')
    f=request.files.get('photo')
    if f and f.filename:
        ext=f.filename.rsplit('.',1)[-1].lower(); fname=f"{user}.{ext}"; path=os.path.join('static/uploads',fname); f.save(path)
        conn=sqlite3.connect('users.db'); conn.execute('UPDATE users SET photo=? WHERE username=?',(fname,user)); conn.commit(); conn.close()
    return redirect('/')

@app.route('/comment/<int:pid>', methods=['POST'])
def comment(pid):
    user=session.get('user')
    if not user: return redirect('/login')
    c=request.form.get('cmt')
    if c:
        now=datetime.datetime.now().strftime("%I:%M %p")
        conn=sqlite3.connect('users.db'); conn.execute('INSERT INTO comments (post_id,username,content,time) VALUES (?,?,?,?)',(pid,user,c,now)); conn.commit(); conn.close()
    return redirect('/')
@app.route('/like/<int:pid>')
def like(pid):
    if not session.get('user'): return redirect('/login')
    conn=sqlite3.connect('users.db'); conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,)); conn.commit(); conn.close(); return redirect('/')
@app.route('/delete/<int:pid>')
def delete(pid):
    user=session.get('user'); conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT username FROM posts WHERE id=?',(pid,)); row=cur.fetchone()
    if row and row[0]==user:
        cur.execute('DELETE FROM posts WHERE id=?',(pid,)); cur.execute('DELETE FROM comments WHERE post_id=?',(pid,)); conn.commit()
    conn.close(); return redirect('/')
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        u=request.form.get('username'); e=request.form.get('email'); p=request.form.get('password')
        conn=sqlite3.connect('users.db')
        try: conn.execute('INSERT INTO users VALUES (?,?,?,NULL)',(u,e,p)); conn.commit(); conn.close(); return redirect('/login')
        except: conn.close(); return redirect('/signup')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body id='body'><div class='phone' id='phone'><div class='top-bar'><a class='icon-btn' href='/login'>←</a><button class='icon-btn' onclick=\"document.getElementById('body').classList.toggle('light');document.getElementById('phone').classList.toggle('light')\">🌙</button></div><p class='sub' style='margin-top:40px'>Already Registered? <a href='/login' style='color:#8ab4ff'>Log in here.</a></p><p class='sub'>Create new Account</p><form method='POST' style='margin-top:20px'><input class='inp' name='username' placeholder='NAME' required><input class='inp' name='email' placeholder='EMAIL' type='email' required><input class='inp' name='password' type='password' placeholder='PASSWORD' required><button class='btn'>Sign up</button></form></div></body></html>"
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password')
        conn=sqlite3.connect('users.db'); cur=conn.cursor(); cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok: session['user']=u; return redirect('/')
        else: return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><h1>Login</h1><p class='sub' style='color:#ff6b6b'>Wrong! Try again</p><form method='POST'><input class='inp' name='username' placeholder='NAME' required><input class='inp' name='password' type='password' placeholder='PASSWORD' required><button class='btn'>Login</button></form></div></body></html>"
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body id='body'><div class='phone' id='phone'><h1 style='margin-top:80px'>Login</h1><p class='sub'>Sign in to continue.</p><form method='POST'><input class='inp' name='username' placeholder='NAME' required><input class='inp' name='password' type='password' placeholder='PASSWORD' required><button class='btn'>Login</button></form><a style='color:rgba(255,255,255,0.6);text-align:center;display:block;margin-top:15px;font-size:11px;text-decoration:none'>Forgot Password?</a><a href='/signup' style='position:absolute;right:-5px;top:52%;transform:rotate(90deg);color:#00aaff;font-weight:800;text-decoration:none'>Signup!</a><button onclick=\"document.getElementById('body').classList.toggle('light');document.getElementById('phone').classList.toggle('light')\" class='icon-btn' style='position:absolute;bottom:20px;left:20px'>🌙/☀️</button></div></body></html>"
@app.route('/logout')
def logout():
    session.pop('user',None); return redirect('/login')
