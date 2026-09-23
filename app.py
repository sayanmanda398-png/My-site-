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
@keyframes flowerIntro{0%{transform:scale(0) rotate(0deg);filter:blur(20px)}50%{transform:scale(1.5) rotate(180deg);filter:blur(0)}100%{transform:scale(25) rotate(360deg);opacity:0;filter:blur(10px)}}
@keyframes gardenReveal{0%{transform:scale(2);filter:brightness(0) blur(20px)}100%{transform:scale(1);filter:brightness(1) blur(0)}}
@keyframes loginZoom{0%{transform:scale(0.3);opacity:0}60%{transform:scale(1.1);opacity:1}100%{transform:scale(1);opacity:1}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
@keyframes glow{0%,100%{box-shadow:0 0 20px #ff4fd8,0 0 40px #7c4dff}50%{box-shadow:0 0 35px #ff4fd8,0 0 70px #7c4dff,0 0 90px #00f0ff}}
@keyframes petals{0%{transform:translateY(-100px) rotate(0deg);opacity:1}100%{transform:translateY(900px) rotate(720deg);opacity:0}}
body{margin:0;min-height:100vh;background:#050010;display:flex;justify-content:center;padding:20px 0;font-family:system-ui,sans-serif;overflow-x:hidden}
.intro-overlay{position:fixed;inset:0;background:radial-gradient(circle,#1a0a40 0%,#050010 100%);z-index:9999;display:flex;justify-content:center;align-items:center;animation:fadeOut 0.5s ease 3.2s forwards}
.flower-center{font-size:120px;animation:flowerIntro 3s cubic-bezier(0.68,-0.55,0.27,1.55) forwards;filter:drop-shadow(0 0 40px #ff4fd8)}
.petal{position:fixed;top:-20px;font-size:18px;pointer-events:none;z-index:10;animation:petals linear infinite}
.phone{width:100%;max-width:380px;min-height:850px;background:linear-gradient(180deg,rgba(30,5,60,0.96),rgba(10,2,30,0.98));border-radius:40px;padding:16px;box-shadow:0 0 25px #ff4fd8,0 0 60px #7c4dff;color:#ffe9ff;border:2px solid #ff4fd8;box-sizing:border-box;position:relative;animation:gardenReveal 1.2s ease 2.8s both, glow 3s infinite 4s}
.phone::after{content:'🌸 🌺 🌷 🌻';position:absolute;bottom:12px;left:0;right:0;text-align:center;font-size:14px;opacity:0.3;letter-spacing:10px;animation:float 4s ease-in-out infinite}
.login-box{animation:loginZoom 0.9s cubic-bezier(0.34,1.56,0.64,1) 3s both}
@keyframes fadeOut{to{opacity:0;pointer-events:none}}
.top{display:flex;justify-content:space-between;align-items:center;padding:10px 4px;font-weight:bold;text-shadow:0 0 10px #ff4fd8}
.pill{background:rgba(40,10,80,0.6);border-radius:28px;padding:14px;margin:10px 0;border:1px solid #ff4fd8;box-shadow:0 0 15px rgba(255,79,216,0.4);backdrop-filter:blur(10px)}
.stat{display:flex;gap:18px;justify-content:center;margin:10px 0;font-size:12px;color:#ffccf5}
.post{background:linear-gradient(135deg,rgba(80,20,120,0.7),rgba(30,10,60,0.7));border-radius:22px;padding:12px 14px;margin:10px 0;border:1px solid #00f0ff;box-shadow:0 0 12px rgba(0,240,255,0.35)}
.btn{background:linear-gradient(90deg,#ff4fd8,#7c4dff);color:white;padding:7px 16px;border-radius:20px;text-decoration:none;font-size:12px;border:none;display:inline-block;box-shadow:0 0 15px #ff4fd8;font-weight:bold;transition:0.2s}
.btn:hover{transform:scale(1.07)}
.btn2{background:rgba(0,240,255,0.15);color:#aef7ff;padding:7px 16px;border-radius:20px;text-decoration:none;font-size:12px;border:1px solid #00f0ff;display:inline-block}
.inp{width:100%;padding:12px 16px;border-radius:28px;border:1px solid #ff4fd8;outline:none;box-sizing:border-box;background:rgba(20,5,40,0.8);color:#ffe9ff}
"""
INTRO_HTML = """
<div class='intro-overlay' id='intro'><div class='flower-center'>🌸</div></div>
<div class='petal' style='left:10%;animation-duration:6s;animation-delay:3s'>🌸</div>
<div class='petal' style='left:30%;animation-duration:7s;animation-delay:3.5s'>🌺</div>
<div class='petal' style='left:50%;animation-duration:5s;animation-delay:4s'>🌷</div>
<div class='petal' style='left:70%;animation-duration:8s;animation-delay:3.2s'>🌻</div>
<div class='petal' style='left:85%;animation-duration:6.5s;animation-delay:4.2s'>🌹</div>
<script>setTimeout(()=>{document.getElementById('intro').style.display='none'},3400)</script>
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
    cur.execute('SELECT bio FROM users WHERE username=?',(u,)); r=cur.fetchone(); bio=r[0] if r and r[0] else "No bio yet"
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
        else: fbtn="<span style='float:right;opacity:0.5;font-size:10px'>You</span>"
        posts_html+=f"<div class='post'><div style='display:flex;justify-content:space-between'><span style='font-size:11px;opacity:0.7'>@{uname} - {tm}</span>{fbtn}</div><div style='margin:8px 0'>{cont}</div><div style='font-size:11px'><a href='/like/{pid}' style='color:#00e5ff;text-decoration:none'>❤️ {lk}</a> <a href='/profile/{uname}' style='color:#ffb07c;text-decoration:none;margin-left:12px'>View</a></div></div>"
    conn.close()
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body>{INTRO_HTML}<div class='phone'><div class='top'><b>@{u}</b><div style='display:flex;gap:8px'><a href='/edit_profile' class='btn2'>Edit</a><a href='/logout' class='btn2'>Out</a></div></div><div class='pill' style='text-align:center'><div style='font-size:42px'>👤</div><div style='font-weight:800'>@{u}</div><div style='font-size:11px;opacity:0.8'>{bio}</div><div class='stat'><span><b>{pc}</b> Posts</span><span><b>{followers}</b> Followers</span><span><b>{following}</b> Following</span></div></div><form method='POST' class='pill' style='display:flex;gap:8px'><input name='content' class='inp' placeholder='What is happening?!'><button class='btn' style='border-radius:50%;width:42px;height:42px'>↑</button></form><div>{posts_html}</div></div></body></html>"
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
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT bio FROM users WHERE username=?',(u2,)); r=cur.fetchone()
    if not r: return "No user"
    bio=r[0] or "No bio"
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u2,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(u2,)); following=cur.fetchone()[0]
    cur.execute('SELECT content,time,likes FROM posts WHERE username=? ORDER BY id DESC',(u2,)); posts=cur.fetchall()
    conn.close()
    ph="".join([f"<div class='post'>{c}<br><small>{t}</small></div>" for c,t,l in posts])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top'><a href='/' class='btn2'>Back</a><b>@{u2}</b><span></span></div><div class='pill' style='text-align:center'><div style='font-size:42px'>👤</div><div><b>@{u2}</b></div><div style='font-size:11px'>{bio}</div><div class='stat'><span><b>{len(posts)}</b> Posts</span><span><b>{followers}</b> Followers</span><span><b>{following}</b> Following</span></div></div>{ph}</div></body></html>"
@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    me=session.get('user')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        b=request.form.get('bio','')[:150]
        cur.execute('UPDATE users SET bio=? WHERE username=?',(b,me)); conn.commit(); conn.close(); return redirect('/')
    cur.execute('SELECT bio FROM users WHERE username=?',(me,)); r=cur.fetchone(); bio=r[0] if r and r[0] else ""; conn.close()
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top'><a href='/' class='btn2'>Back</a><b>Edit Bio</b><span></span></div><div class='pill'><form method='POST'><textarea name='bio' maxlength='150' class='inp' style='height:90px'>{bio}</textarea><button class='btn' style='width:100%;margin-top:12px'>Save</button></form></div></div></body></html>"
@app.route('/like/<int:pid>')
def like(pid): conn=sqlite3.connect('users.db'); conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,)); conn.commit(); conn.close(); return redirect('/')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password'); conn=sqlite3.connect('users.db'); cur=conn.cursor(); cur.execute('SELECT 1 FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok: session['user']=u; return redirect('/')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body>{INTRO_HTML}<div class='phone'><div class='login-box'><h1 style='text-align:center;margin-top:40px;text-shadow:0 0 20px #ff4fd8'>🌸 Neon Garden 🌸</h1><h2 style='text-align:center;opacity:0.7'>Login</h2><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;color:black;background:white'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;color:black;background:white'><button class='btn' style='width:100%;padding:12px'>Login ✨</button></form><a href='/signup' style='display:block;text-align:center;color:#00f0ff;margin-top:15px'>Create Account</a></div></div></div></body></html>"
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        u=request.form.get('username'); e=request.form.get('email',''); p=request.form.get('password'); conn=sqlite3.connect('users.db')
        try: conn.execute('INSERT INTO users (username,email,password,bio) VALUES (?,?,?,?)',(u,e,p,'')); conn.commit(); conn.close(); return redirect('/login')
        except: conn.close(); return redirect('/signup')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body>{INTRO_HTML}<div class='phone'><div class='login-box'><h1 style='text-align:center;margin-top:30px;text-shadow:0 0 20px #ff4fd8'>🌸 Join Garden 🌸</h1><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;color:black;background:white'><input name='email' type='email' class='inp' placeholder='EMAIL' required style='margin-bottom:10px;color:black;background:white'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;color:black;background:white'><button class='btn' style='width:100%;padding:12px'>Sign up 🌷</button></form><a href='/login' style='display:block;text-align:center;color:#00f0ff'>Login</a></div></div></div></body></html>"
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
