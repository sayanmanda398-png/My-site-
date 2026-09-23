from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, datetime, os
app = Flask(__name__)
app.secret_key = "babu_pro_123"
os.makedirs('static/uploads', exist_ok=True)
def ist_now():
    return (datetime.datetime.utcnow()+datetime.timedelta(hours=5,minutes=30)).strftime("%I:%M %p - %d/%m - %Y")
def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, bio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0)')
    conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))')
    conn.execute('CREATE TABLE IF NOT EXISTS moods (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mood TEXT, note TEXT, time TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS helps (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, category TEXT, question TEXT, time TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS focus (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mins INTEGER, task TEXT, time TEXT)')
    conn.commit(); conn.close()
init_db()
CSS = """
@keyframes flowerIntro{0%{transform:scale(0) rotate(0deg);filter:blur(20px)}50%{transform:scale(1.5) rotate(180deg);filter:blur(0)}100%{transform:scale(25) rotate(360deg);opacity:0;filter:blur(10px)}}
@keyframes gardenReveal{0%{transform:scale(2);filter:brightness(0) blur(20px)}100%{transform:scale(1);filter:brightness(1) blur(0)}}
@keyframes loginZoom{0%{transform:scale(0.3);opacity:0}60%{transform:scale(1.1);opacity:1}100%{transform:scale(1);opacity:1}}
@keyframes petals{0%{transform:translateY(-100px) rotate(0deg);opacity:1}100%{transform:translateY(900px) rotate(720deg);opacity:0}}
body{margin:0;min-height:100vh;background:#050010;display:flex;justify-content:center;padding:10px 0;font-family:system-ui,sans-serif;overflow-x:hidden}
.intro-overlay{position:fixed;inset:0;background:radial-gradient(circle,#1a0a40 0%,#050010 100%);z-index:9999;display:flex;justify-content:center;align-items:center;animation:fadeOut 0.5s ease 3.2s forwards}
.flower-center{font-size:120px;animation:flowerIntro 3s cubic-bezier(0.68,-0.55,0.27,1.55) forwards;filter:drop-shadow(0 0 40px #ff4fd8)}
.petal{position:fixed;top:-20px;font-size:18px;pointer-events:none;z-index:10;animation:petals linear infinite}
.phone{width:100%;max-width:390px;min-height:900px;background:linear-gradient(180deg,rgba(30,5,60,0.96),rgba(10,2,30,0.98));border-radius:40px;padding:14px;box-shadow:0 0 25px #ff4fd8,0 0 60px #7c4dff;color:#ffe9ff;border:2px solid #ff4fd8;box-sizing:border-box;position:relative;animation:gardenReveal 1.2s ease 2.8s both}
.login-box{animation:loginZoom 0.9s cubic-bezier(0.34,1.56,0.64,1) 3s both}
@keyframes fadeOut{to{opacity:0;pointer-events:none}}
.nav{display:flex;gap:6px;overflow-x:auto;padding:8px 0;scrollbar-width:none}
.nav a{white-space:nowrap;padding:8px 14px;border-radius:20px;text-decoration:none;font-size:11px;font-weight:bold}
.nav.active{background:linear-gradient(90deg,#ff4fd8,#7c4dff);color:white;box-shadow:0 0 12px #ff4fd8}
.nav.off{background:rgba(0,240,255,0.12);color:#aef7ff;border:1px solid #00f0ff}
.pill{background:rgba(40,10,80,0.6);border-radius:28px;padding:14px;margin:10px 0;border:1px solid #ff4fd8;box-shadow:0 0 15px rgba(255,79,216,0.4);backdrop-filter:blur(10px)}
.post{background:linear-gradient(135deg,rgba(80,20,120,0.7),rgba(30,10,60,0.7));border-radius:22px;padding:12px 14px;margin:10px 0;border:1px solid #00f0ff;box-shadow:0 0 12px rgba(0,240,255,0.35)}
.btn{background:linear-gradient(90deg,#ff4fd8,#7c4dff);color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:11px;border:none;display:inline-block;box-shadow:0 0 10px #ff4fd8;font-weight:bold}
.btn2{background:rgba(0,240,255,0.15);color:#aef7ff;padding:7px 14px;border-radius:20px;text-decoration:none;font-size:11px;border:1px solid #00f0ff;display:inline-block}
.inp{width:100%;padding:12px 16px;border-radius:28px;border:1px solid #ff4fd8;outline:none;box-sizing:border-box;background:rgba(20,5,40,0.8);color:#ffe9ff}
.mood-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin:10px 0}
.mood-card{padding:12px;border-radius:18px;text-align:center;font-size:22px;border:1px solid #ff4fd8;background:rgba(255,79,216,0.1);cursor:pointer;transition:0.2s}
.mood-card:hover{transform:scale(1.05);background:rgba(255,79,216,0.25)}
.timer{font-size:48px;text-align:center;font-weight:900;text-shadow:0 0 20px #00f0ff;letter-spacing:2px}
"""
INTRO = """
<div class='intro-overlay' id='intro'><div class='flower-center'>🌸</div></div>
<div class='petal' style='left:10%;animation-duration:6s;animation-delay:3s'>🌸</div>
<div class='petal' style='left:50%;animation-duration:5s;animation-delay:4s'>🌷</div>
<div class='petal' style='left:85%;animation-duration:6.5s;animation-delay:4.2s'>🌹</div>
<script>setTimeout(()=>{let e=document.getElementById('intro'); if(e) e.style.display='none'},3400)</script>
"""
def nav_bar(active):
    return f"""<div class='nav'>
    <a href='/feed' class='{"active" if active=="home" else "off"}'>🏠 Garden</a>
    <a href='/mood' class='{"active" if active=="mood" else "off"}'>🧠 Mood</a>
    <a href='/focus' class='{"active" if active=="focus" else "off"}'>⏱️ Focus</a>
    <a href='/help' class='{"active" if active=="help" else "off"}'>🆘 Help</a>
    </div>"""

@app.route('/')
def home_redirect(): return redirect('/feed')
@app.route('/feed', methods=['GET','POST'])
def feed():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        t=request.form.get('content','').strip()
        if t: cur.execute('INSERT INTO posts (username,content,time,likes) VALUES (?,?,?,0)',(u,t,ist_now())); conn.commit()
    cur.execute('SELECT COUNT(*) FROM posts WHERE username=?',(u,)); pc=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u,)); followers=cur.fetchone()[0]
    cur.execute('SELECT id,username,content,time,likes FROM posts ORDER BY id DESC LIMIT 30'); posts=cur.fetchall()
    ph=""
    for pid,uname,cont,tm,lk in posts:
        ph+=f"<div class='post'><div style='font-size:10px;opacity:0.7'>@{uname} • {tm}</div><div style='margin:8px 0'>{cont}</div><a href='/like/{pid}' style='color:#00e5ff;text-decoration:none;font-size:12px'>💧 Water {lk}</a></div>"
    cur.execute('SELECT mood FROM moods WHERE username=? ORDER BY id DESC LIMIT 1',(u,)); last_mood=cur.fetchone()
    mood_str=last_mood[0] if last_mood else "Not set"
    cur.execute('SELECT SUM(mins) FROM focus WHERE username=?',(u,)); fsum=cur.fetchone()[0] or 0
    conn.close()
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body>{INTRO}<div class='phone'>{nav_bar('home')}<div class='pill' style='text-align:center'><div style='font-size:32px'>🌸 Life Garden</div><div style='font-size:11px;opacity:0.8'>@{u} • Mood: {mood_str} • Focus: {fsum}m • Posts: {pc}</div></div><form method='POST' class='pill' style='display:flex;gap:8px'><input name='content' class='inp' placeholder='What did you grow today? 🌱'><button class='btn' style='border-radius:50%;width:42px;height:42px'>↑</button></form><div>{ph}</div></div></body></html>"

@app.route('/mood', methods=['GET','POST'])
def mood_page():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        m=request.form.get('mood'); n=request.form.get('note','')[:120]
        cur.execute('INSERT INTO moods (username,mood,note,time) VALUES (?,?,?,?)',(u,m,n,ist_now())); conn.commit()
    cur.execute('SELECT mood,note,time FROM moods WHERE username=? ORDER BY id DESC LIMIT 10',(u,)); rows=cur.fetchall()
    conn.close()
    history="".join([f"<div class='post' style='border-color:#ff4fd8'>{mo} • <small>{ti}</small><br><span style='font-size:11px;opacity:0.8'>{no}</span></div>" for mo,no,ti in rows])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'>{nav_bar('mood')}<div class='pill'><h3 style='margin:0'>🧠 How is your soil today?</h3><p style='font-size:11px;opacity:0.7'>Track mood daily. See pattern after 7 days.</p><form method='POST'><div class='mood-grid'><button name='mood' value='🌸 Blooming' class='mood-card'>🌸<br><span style='font-size:10px'>Blooming</span></button><button name='mood' value='🌱 Okay' class='mood-card'>🌱<br><span style='font-size:10px'>Okay</span></button><button name='mood' value='🍂 Low' class='mood-card'>🍂<br><span style='font-size:10px'>Low</span></button><button name='mood' value='⚡ Energetic' class='mood-card'>⚡<br><span style='font-size:10px'>Energy</span></button><button name='mood' value='😴 Tired' class='mood-card'>😴<br><span style='font-size:10px'>Tired</span></button><button name='mood' value='😵 Stuck' class='mood-card'>😵<br><span style='font-size:10px'>Stuck</span></button></div><input name='note' class='inp' placeholder='One line note (optional)' style='margin-top:8px'></form></div>{history}</div></body></html>"

@app.route('/focus', methods=['GET','POST'])
def focus_page():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        mins=int(request.form.get('mins',25)); task=request.form.get('task','Study')[:60]
        cur.execute('INSERT INTO focus (username,mins,task,time) VALUES (?,?,?,?)',(u,mins,task,ist_now())); conn.commit()
    cur.execute('SELECT mins,task,time FROM focus WHERE username=? ORDER BY id DESC LIMIT 10',(u,)); rows=cur.fetchall()
    total=sum([r[0] for r in rows])
    conn.close()
    hist="".join([f"<div class='post'>✅ {mi}m • {ta}<br><small>{ti}</small></div>" for mi,ta,ti in rows])
    return f"""<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'>{nav_bar('focus')}
    <div class='pill' style='text-align:center'><div class='timer' id='timer'>25:00</div><div style='font-size:11px;opacity:0.7'>Focus Garden — plant grows while you focus</div>
    <div id='plant' style='font-size:60px;margin:10px'>🌱</div>
    <div style='display:flex;gap:8px;justify-content:center'><button class='btn' onclick='startF()'>Start ▶️</button><button class='btn2' onclick='resetF()'>Reset</button></div>
    <form method='POST' style='margin-top:14px;display:flex;gap:8px'><input name='task' class='inp' placeholder='What are you doing? (Study/Coding)'><select name='mins' class='inp' style='width:90px'><option value='25'>25m</option><option value='45'>45m</option><option value='15'>15m</option></select><button class='btn'>Save</button></form>
    <div style='font-size:11px;margin-top:8px'>Today: {total} mins focused 🔥</div>
    </div>{hist}</div>
    <script>
    let t=1500, iv=null;
    function upd(){{let m=Math.floor(t/60), s=t%60; document.getElementById('timer').innerText=(m<10?'0':'')+m+':'+(s<10?'0':'')+s; let p=document.getElementById('plant'); if(t<1200) p.innerText='🌿'; if(t<600) p.innerText='🌸'; if(t<=0) p.innerText='🌳';}}
    function startF(){{if(iv) return; iv=setInterval(()=>{{t--; upd(); if(t<=0){{clearInterval(iv); alert('Plant fully grown! 🌳 Good work!');}}}},1000);}}
    function resetF(){{clearInterval(iv); iv=null; t=1500; upd(); document.getElementById('plant').innerText='🌱';}}
    upd();
    </script></body></html>"""

@app.route('/help', methods=['GET','POST'])
def help_page():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        cat=request.form.get('category','General'); q=request.form.get('question','').strip()[:200]
        if q: cur.execute('INSERT INTO helps (username,category,question,time) VALUES (?,?,?,?)',(u,cat,q,ist_now())); conn.commit()
    cur.execute('SELECT username,category,question,time FROM helps ORDER BY id DESC LIMIT 20'); rows=cur.fetchall()
    conn.close()
    cards="".join([f"<div class='post'><span class='btn2' style='font-size:9px'>{ca}</span> <small style='opacity:0.6'>@{un} • {ti}</small><div style='margin-top:6px'>{qu}</div><div style='margin-top:6px'><a href='/feed' class='btn' style='font-size:10px'>💬 Help them</a></div></div>" for un,ca,qu,ti in rows])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'>{nav_bar('help')}<div class='pill'><h3 style='margin:0'>🆘 Help Garden</h3><p style='font-size:11px;opacity:0.7'>Ask anonymously. Get real help, not likes.</p><form method='POST'><select name='category' class='inp' style='margin-bottom:8px'><option>📚 Study</option><option>🧠 Mental</option><option>💼 Work</option><option>💪 Health</option><option>🌱 Life Stuck</option></select><input name='question' class='inp' placeholder='I need help with...' required><button class='btn' style='width:100%;margin-top:10px'>Ask Garden 🌸</button></form></div>{cards}</div></body></html>"

@app.route('/like/<int:pid>')
def like(pid): conn=sqlite3.connect('users.db'); conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,)); conn.commit(); conn.close(); return redirect('/feed')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password'); conn=sqlite3.connect('users.db'); cur=conn.cursor(); cur.execute('SELECT 1 FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok: session['user']=u; return redirect('/feed')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body>{INTRO}<div class='phone'><div class='login-box'><h1 style='text-align:center;margin-top:40px;text-shadow:0 0 20px #ff4fd8'>🌸 Life Garden 🌸</h1><h2 style='text-align:center;opacity:0.7;font-size:14px'>All-in-One: Social + Mood + Focus + Help</h2><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;color:black;background:white'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;color:black;background:white'><button class='btn' style='width:100%;padding:12px'>Login ✨</button></form><a href='/signup' style='display:block;text-align:center;color:#00f0ff;margin-top:15px'>Create Account</a></div></div></div></body></html>"
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        u=request.form.get('username'); e=request.form.get('email',''); p=request.form.get('password'); conn=sqlite3.connect('users.db')
        try: conn.execute('INSERT INTO users (username,email,password,bio) VALUES (?,?,?,?)',(u,e,p,'')); conn.commit(); conn.close(); return redirect('/login')
        except: conn.close(); return redirect('/signup')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body>{INTRO}<div class='phone'><div class='login-box'><h1 style='text-align:center;margin-top:30px;text-shadow:0 0 20px #ff4fd8'>🌸 Join Garden 🌸</h1><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;color:black;background:white'><input name='email' type='email' class='inp' placeholder='EMAIL' required style='margin-bottom:10px;color:black;background:white'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;color:black;background:white'><button class='btn' style='width:100%;padding:12px'>Sign up 🌷</button></form><a href='/login' style='display:block;text-align:center;color:#00f0ff'>Login</a></div></div></div></body></html>"
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
