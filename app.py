from flask import Flask, request, redirect, session
import sqlite3, datetime
app = Flask(__name__)
app.secret_key = "babu_pro_123"

def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0)')
    conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, time TEXT)')
    conn.commit(); conn.close()
init_db()

CANVA_CSS = """
body{margin:0;min-height:100vh;background:#020210;display:flex;justify-content:center;align-items:center;font-family:Inter,sans-serif}
.phone{width:370px;min-height:820px;background:linear-gradient(180deg,#2e40e6 0%, #1a2480 40%, #050516 100%);border-radius:35px;padding:20px 18px;box-shadow:0 0 0 8px #e5e5e5, 0 20px 60px rgba(0,0,0,0.6);position:relative;box-sizing:border-box}
h1{color:#0a0a0a;text-align:center;font-size:36px;margin-top:70px;margin-bottom:5px;font-weight:800}
.sub{color:rgba(255,255,255,0.7);text-align:center;font-size:12px;margin-bottom:30px}
.inp{width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;margin-bottom:16px;color:white;box-sizing:border-box;outline:none;font-size:12px;letter-spacing:1px}
.inp::placeholder{color:rgba(255,255,255,0.35)}
.btn{width:100%;background:linear-gradient(90deg,#6a8cff,#4a5cff);border:none;padding:14px;border-radius:10px;font-weight:800;font-size:14px;cursor:pointer;box-shadow:-5px 3px 0 #00e5ff, 4px 5px 0 #ff00e5;color:#0a0a2a;margin-top:20px}
.small-link{color:rgba(255,255,255,0.6);text-align:center;font-size:11px;margin-top:12px;display:block;text-decoration:none}
.top-bar{display:flex;justify-content:space-between;align-items:center;padding:10px 5px}
.search-icon{width:36px;height:36px;background:rgba(0,0,0,0.3);border-radius:50%;display:flex;justify-content:center;align-items:center;color:white;font-size:18px}
.user-photo-box{width:92%;height:180px;background:rgba(40,50,150,0.6);border-radius:35px;margin:15px auto;display:flex;justify-content:center;align-items:center;color:rgba(255,255,255,0.8);font-size:14px;border:1px solid rgba(255,255,255,0.05)}
.section-label{color:rgba(255,255,255,0.6);font-size:10px;text-align:center;margin-top:15px}
.chat-pill{background:#2a2fb8;border-radius:20px;padding:15px 18px;margin:10px auto;width:88%;color:white;font-size:13px}
.comment-box{background:rgba(0,0,0,0.3);border-radius:15px;padding:8px 12px;margin-top:8px;font-size:11px}
.comment-input{width:70%;background:rgba(255,255,255,0.1);border:1px dashed rgba(255,255,255,0.2);border-radius:20px;padding:6px 12px;color:white;outline:none;font-size:11px}
.bottom-profile{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);width:38px;height:38px;background:rgba(255,255,255,0.9);border-radius:50%;display:flex;justify-content:center;align-items:center}
"""

@app.route('/', methods=['GET','POST'])
def home():
    user=session.get('user')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST' and user:
        c=request.form.get('content')
        if c:
            now=datetime.datetime.now().strftime("%I:%M %p")
            cur.execute('INSERT INTO posts VALUES (NULL,?,?,?,0)',(user,c,now)); conn.commit()
    cur.execute('SELECT id,username,content,time,likes FROM posts ORDER BY id DESC')
    posts=cur.fetchall()
    if not user: conn.close(); return redirect('/login')

    chat_html=""
    for pid,uname,cont,tm,likes in posts:
        cur.execute('SELECT username,content,time FROM comments WHERE post_id=? ORDER BY id ASC',(pid,))
        comms=cur.fetchall()
        comm_html=""
        for cu,cc,ct in comms:
            comm_html+=f"<div class='comment-box'><b>@{cu}</b>: {cc} <span style='opacity:0.5;float:right'>{ct}</span></div>"
        del_btn = f"<a href='/delete/{pid}' style='color:#ff8a8a;float:right;text-decoration:none;font-size:11px'>✕</a>" if uname==user else ""
        chat_html+=f"""
        <div class='chat-pill'>
            <div style='display:flex;justify-content:space-between'><b style='font-size:10px;color:#8ab4ff'>@{uname} • {tm}</b>{del_btn}</div>
            <div style='margin-top:6px'>{cont} <a href='/like/{pid}' style='color:#00e5ff;text-decoration:none;float:right'>❤️{likes}</a></div>
            {comm_html}
            <form action='/comment/{pid}' method='POST' style='margin-top:8px;display:flex;gap:5px'>
                <input class='comment-input' name='cmt' placeholder='Add comment...' required>
                <button style='background:#5a7cff;border:none;border-radius:15px;padding:5px 10px;color:white;font-size:10px'>Reply</button>
            </form>
        </div>"""
    conn.close()
    if not chat_html:
        chat_html="<div class='chat-pill' style='opacity:0.5;text-align:center'>No chats yet. Be first!</div>"
    return f"""
    <html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CANVA_CSS}</style></head>
    <body><div class='phone'>
    <div class='top-bar'><div class='search-icon'>🔍</div><div style='color:white;font-weight:bold'>@{user}</div><a href='/logout' style='color:rgba(255,255,255,0.6);text-decoration:none;font-size:11px'>Logout</a></div>
    <div class='user-photo-box'><div style='text-align:center'><div style='font-size:40px'>👤</div><div>@{user}</div><div style='font-size:9px;opacity:0.6'>Babu Pro • {len(posts)} posts</div></div></div>
    <form method='POST' style='width:92%;margin:10px auto;display:flex;gap:5px'><input name='content' placeholder='Type a message...' required style='flex:1;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:12px 18px;color:white;outline:none;font-size:12px'><button style='background:#5a7cff;border:none;border-radius:50%;width:42px;height:42px;color:white'>↑</button></form>
    <div style='max-height:380px;overflow-y:auto'>{chat_html}</div>
    <div class='bottom-profile'>👤</div>
    </div></body></html>
    """

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
        try: conn.execute('INSERT INTO users VALUES (?,?,?)',(u,e,p)); conn.commit(); conn.close(); return redirect('/login')
        except: conn.close(); return redirect('/signup')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CANVA_CSS}</style></head><body><div class='phone'><div class='top-bar'><a href='/login' style='color:white;text-decoration:none;font-size:20px'>←</a></div><p class='sub' style='margin-top:60px'>Already Registered? <a href='/login' style='color:white'>Log in here.</a></p><p class='sub'>Create new Account</p><form method='POST' style='margin-top:30px'><input class='inp' name='username' placeholder='NAME' required><input class='inp' name='email' placeholder='EMAIL' type='email' required><input class='inp' name='password' type='password' placeholder='PASSWORD' required><button class='btn'>Sign up</button></form></div></body></html>"
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password')
        conn=sqlite3.connect('users.db'); cur=conn.cursor(); cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok: session['user']=u; return redirect('/')
        else: return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CANVA_CSS}</style></head><body><div class='phone'><h1>Login</h1><p class='sub' style='color:#ff6b6b'>Wrong! Try again</p><form method='POST'><input class='inp' name='username' placeholder='NAME' required><input class='inp' name='password' type='password' placeholder='PASSWORD' required><button class='btn'>Login</button></form><a class='small-link'>Forgot Password?</a><div class='bottom-profile'>👤</div></div></body></html>"
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CANVA_CSS}</style></head><body><div class='phone'><h1>Login</h1><p class='sub'>Sign in to continue.</p><form method='POST'><input class='inp' name='username' placeholder='NAME' required><input class='inp' name='password' type='password' placeholder='PASSWORD' required><button class='btn'>Login</button></form><a class='small-link'>Forgot Password?</a><a href='/signup' style='position:absolute;right:-5px;top:52%;transform:rotate(90deg);color:#00aaff;font-weight:800;text-decoration:none'>Signup!</a><div class='bottom-profile'>👤</div></div></body></html>"
@app.route('/logout')
def logout():
    session.pop('user',None); return redirect('/login')
