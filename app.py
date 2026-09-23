from flask import Flask, request, redirect, session
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
    conn.execute('CREATE TABLE IF NOT EXISTS moods (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mood TEXT, note TEXT, time TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS helps (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, category TEXT, question TEXT, time TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS focus (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, mins INTEGER, task TEXT, time TEXT)')
    conn.commit(); conn.close()
init_db()
PWA='<link rel="manifest" href="/static/manifest.json"><meta name="theme-color" content="#ff4fd8"><link rel="icon" href="https://cdn-icons-png.flaticon.com/512/628/628283.png"><script>if("serviceWorker" in navigator){navigator.serviceWorker.register("/static/sw.js");}</script>'
CSS="body{margin:0;min-height:100vh;background:#050010;display:flex;justify-content:center;padding:10px 0;font-family:system-ui,sans-serif}.phone{width:100%;max-width:390px;min-height:900px;background:linear-gradient(180deg,rgba(30,5,60,0.96),rgba(10,2,30,0.98));border-radius:40px;padding:14px;box-shadow:0 0 25px #ff4fd8;color:#ffe9ff;border:2px solid #ff4fd8}.nav{display:flex;gap:6px;overflow-x:auto;padding:8px 0}.nav a{white-space:nowrap;padding:8px 14px;border-radius:20px;text-decoration:none;font-size:11px;font-weight:bold}.active{background:linear-gradient(90deg,#ff4fd8,#7c4dff);color:white}.off{background:rgba(0,240,255,0.12);color:#aef7ff;border:1px solid #00f0ff}.pill{background:rgba(40,10,80,0.6);border-radius:28px;padding:14px;margin:10px 0;border:1px solid #ff4fd8}.post{background:linear-gradient(135deg,rgba(80,20,120,0.7),rgba(30,10,60,0.7));border-radius:22px;padding:12px 14px;margin:10px 0;border:1px solid #00f0ff}.btn{background:linear-gradient(90deg,#ff4fd8,#7c4dff);color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:11px;border:none;display:inline-block;font-weight:bold}.btn2{background:rgba(0,240,255,0.15);color:#aef7ff;padding:7px 14px;border-radius:20px;text-decoration:none;font-size:11px;border:1px solid #00f0ff;display:inline-block}.inp{width:100%;padding:12px 16px;border-radius:28px;border:1px solid #ff4fd8;outline:none;background:rgba(20,5,40,0.8);color:#ffe9ff}.timer{font-size:48px;text-align:center;font-weight:900}"
def nav_bar(a): return f"<div class='nav'><a href='/feed' class='{'active' if a=='home' else 'off'}'>🏠 Garden</a><a href='/mood' class='{'active' if a=='mood' else 'off'}'>🧠 Mood</a><a href='/focus' class='{'active' if a=='focus' else 'off'}'>⏱️ Focus</a><a href='/help' class='{'active' if a=='help' else 'off'}'>🆘 Help</a><a href='/learn' class='{'active' if a=='learn' else 'off'}'>📚 Learn</a></div>"
@app.route('/')
def r(): return redirect('/feed')
@app.route('/feed', methods=['GET','POST'])
def feed():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        t=request.form.get('content','').strip()
        if t: cur.execute('INSERT INTO posts VALUES (NULL,?,?,?,0)',(u,t,ist_now())); conn.commit()
    cur.execute('SELECT id,username,content,time,likes FROM posts ORDER BY id DESC LIMIT 20'); ps=cur.fetchall(); conn.close()
    ph="".join([f"<div class='post'><div style='font-size:10px;opacity:0.7'>@{x[1]} {x[3]}</div><div>{x[2]}</div><a href='/like/{x[0]}' style='color:#00e5ff;font-size:12px;text-decoration:none'>💧 Water {x[4]}</a></div>" for x in ps])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{PWA}<style>{CSS}</style></head><body><div class='phone'>{nav_bar('home')}<div class='pill' style='text-align:center'><div style='font-size:28px'>🌸 Life Garden 🌸</div><div style='font-size:11px'>@{u} - All in One App</div></div><form method='POST' class='pill' style='display:flex;gap:8px'><input name='content' class='inp' placeholder='What did you grow today?'><button class='btn'>↑</button></form>{ph}</div></body></html>"
@app.route('/mood', methods=['GET','POST'])
def mood():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST': cur.execute('INSERT INTO moods VALUES (NULL,?,?,?,?)',(u,request.form.get('mood'),request.form.get('note','')[:80],ist_now())); conn.commit()
    cur.execute('SELECT mood,note,time FROM moods WHERE username=? ORDER BY id DESC LIMIT 10',(u,)); rs=cur.fetchall(); conn.close()
    h="".join([f"<div class='post'>{m} <small>{t}</small><br><span style='font-size:11px'>{n}</span></div>" for m,n,t in rs])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{PWA}<style>{CSS}</style></head><body><div class='phone'>{nav_bar('mood')}<div class='pill'><h3>🧠 How is soil today?</h3><form method='POST'><div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px'><button name='mood' value='🌸 Blooming' class='pill' style='text-align:center'>🌸<br>Blooming</button><button name='mood' value='🌱 Okay' class='pill' style='text-align:center'>🌱<br>Okay</button><button name='mood' value='🍂 Low' class='pill' style='text-align:center'>🍂<br>Low</button><button name='mood' value='⚡ Energy' class='pill' style='text-align:center'>⚡<br>Energy</button><button name='mood' value='😴 Tired' class='pill' style='text-align:center'>😴<br>Tired</button><button name='mood' value='😵 Stuck' class='pill' style='text-align:center'>😵<br>Stuck</button></div><input name='note' class='inp' placeholder='note (optional)' style='margin-top:8px'></form></div>{h}</div></body></html>"
@app.route('/focus', methods=['GET','POST'])
def focus():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST': cur.execute('INSERT INTO focus VALUES (NULL,?,?,?,?)',(u,int(request.form.get('mins',25)),request.form.get('task','Study'),ist_now())); conn.commit()
    cur.execute('SELECT mins,task,time FROM focus WHERE username=? ORDER BY id DESC LIMIT 10',(u,)); rs=cur.fetchall(); tot=sum([r[0] for r in rs]); conn.close()
    hist="".join([f"<div class='post'>✅ {m}m {t} <small>{ti}</small></div>" for m,t,ti in rs])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{PWA}<style>{CSS}</style></head><body><div class='phone'>{nav_bar('focus')}<div class='pill' style='text-align:center'><div class='timer' id='tm'>25:00</div><div id='pl' style='font-size:60px'>🌱</div><button class='btn' onclick='startF()'>Start ▶️</button> <button class='btn2' onclick='location.reload()'>Reset</button><form method='POST' style='display:flex;gap:8px;margin-top:12px'><input name='task' class='inp' placeholder='Study/Coding'><select name='mins' class='inp' style='width:80px'><option value='25'>25m</option><option value='45'>45m</option><option value='15'>15m</option></select><button class='btn'>Save</button></form><div style='margin-top:8px;font-size:11px'>Total: {tot}m 🔥</div></div>{hist}</div><script>let t=1500,iv=null;function up(){{let m=Math.floor(t/60),s=t%60;document.getElementById('tm').innerText=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;let p=document.getElementById('pl');if(t<1200)p.innerText='🌿';if(t<600)p.innerText='🌸';if(t<=0)p.innerText='🌳'}};function startF(){{if(iv)return;iv=setInterval(()=>{{t--;up();if(t<=0){{clearInterval(iv);alert('Grown! 🌳')}}}},1000)}};up();</script></body></html>"
@app.route('/help', methods=['GET','POST'])
def help_p():
    u=session.get('user')
    if not u: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST': cur.execute('INSERT INTO helps VALUES (NULL,?,?,?,?)',(u,request.form.get('category'),request.form.get('question','')[:200],ist_now())); conn.commit()
    cur.execute('SELECT username,category,question,time FROM helps ORDER BY id DESC LIMIT 20'); rs=cur.fetchall(); conn.close()
    cs="".join([f"<div class='post'><span class='btn2' style='font-size:9px'>{c}</span> <small>@{un} {ti}</small><div style='margin-top:6px'>{q}</div></div>" for un,c,q,ti in rs])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{PWA}<style>{CSS}</style></head><body><div class='phone'>{nav_bar('help')}<div class='pill'><h3>🆘 Help Garden</h3><form method='POST'><select name='category' class='inp' style='margin-bottom:8px'><option>📚 Study</option><option>🧠 Mental</option><option>💼 Work</option><option>💪 Health</option><option>🌱 Stuck</option></select><input name='question' class='inp' placeholder='I need help with...' required><button class='btn' style='width:100%;margin-top:8px'>Ask 🌸</button></form></div>{cs}</div></body></html>"
@app.route('/learn')
def learn():
    u=session.get('user')
    if not u: return redirect('/login')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{PWA}<style>{CSS}</style></head><body><div class='phone'>{nav_bar('learn')}<div class='pill'><h3>📚 Learn Hub - Free</h3></div><div class='pill'><b>AI/Prompting</b><br><span style='font-size:11px'>freeCodeCamp, learnprompting.org, Google Gen AI, Kaggle AI</span></div><div class='pill'><b>Web Dev</b><br><span style='font-size:11px'>freeCodeCamp, Odin Project, MIT OCW, MDN Docs</span></div><div class='pill'><b>Marketing</b><br><span style='font-size:11px'>Google Garage, HubSpot, Ahrefs SEO, Wharton Audit</span></div><div class='pill'><b>Data</b><br><span style='font-size:11px'>Khan Stats, Kaggle Data, Google Analytics Audit</span></div><div class='pill'><b>Podcasts</b><br><span style='font-size:11px'>Lex Fridman, CodeNewbie, Everyone Hates Marketers</span></div></div></body></html>"
@app.route('/like/<int:pid>')
def like(pid): conn=sqlite3.connect('users.db'); conn.execute('UPDATE posts SET likes=likes+1 WHERE id=?',(pid,)); conn.commit(); conn.close(); return redirect('/feed')
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password'); conn=sqlite3.connect('users.db'); cur=conn.cursor(); cur.execute('SELECT 1 FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok: session['user']=u; return redirect('/feed')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{PWA}<style>{CSS}</style></head><body><div class='phone' style='margin-top:40px'><h1 style='text-align:center'>🌸 Life Garden 🌸</h1><p style='text-align:center;font-size:12px;opacity:0.7'>Social + Mood + Focus + Help + Learn</p><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;background:white;color:black'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;background:white;color:black'><button class='btn' style='width:100%'>Login ✨</button></form><a href='/signup' style='display:block;text-align:center;color:#00f0ff'>Create Account</a></div></body></html>"
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        u=request.form.get('username'); e=request.form.get('email',''); p=request.form.get('password'); conn=sqlite3.connect('users.db')
        try: conn.execute('INSERT INTO users VALUES (?,?,?,?)',(u,e,p,'')); conn.commit(); conn.close(); return redirect('/login')
        except: conn.close(); return redirect('/signup')
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>{PWA}<style>{CSS}</style></head><body><div class='phone' style='margin-top:30px'><h1 style='text-align:center'>🌸 Join Garden 🌸</h1><form method='POST' class='pill'><input name='username' class='inp' placeholder='NAME' required style='margin-bottom:10px;background:white;color:black'><input name='email' class='inp' placeholder='EMAIL' required style='margin-bottom:10px;background:white;color:black'><input name='password' type='password' class='inp' placeholder='PASSWORD' required style='margin-bottom:10px;background:white;color:black'><button class='btn' style='width:100%'>Sign up 🌷</button></form><a href='/login' style='display:block;text-align:center;color:#00f0ff'>Login</a></div></body></html>"
@app.route('/logout')
def logout(): session.clear(); return redirect('/login')
