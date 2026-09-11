from flask import Flask, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "babu_pro_123"
def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.execute("INSERT OR IGNORE INTO users VALUES ('babu','1234')")
    conn.commit(); conn.close()
init_db()

@app.route('/')
def home():
    user=session.get('user')
    if not user:
        return """
        <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
        body{font-family:sans-serif;background:#0f172a;color:white;text-align:center;padding:30px}
        .card{background:white;color:#0f172a;padding:30px;border-radius:20px;max-width:380px;margin:20px auto;box-shadow:0 10px 30px rgba(0,0,0,0.3)}
        .btn{display:inline-block;background:#0f172a;color:white;padding:12px 25px;border-radius:10px;margin:5px;text-decoration:none}
        .btn2{background:#38bdf8}
        </style></head><body><h1>🚀 BABU PRO</h1><p>Day 7 - Social App</p>
        <div class="card"><h2>Welcome Guest!</h2><p>Login to continue</p><a class="btn" href="/login">Login</a><a class="btn btn2" href="/signup">Signup</a></div></body></html>
        """
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
    body{{font-family:sans-serif;background:#f1f5f9;margin:0}}
    .nav{{background:#0f172a;color:white;padding:15px;display:flex;justify-content:space-between;align-items:center}}
    .nav a{{color:white;text-decoration:none;background:#38bdf8;padding:8px 15px;border-radius:20px}}
    .feed{{max-width:450px;margin:20px auto;padding:15px}}
    .post{{background:white;border-radius:20px;padding:20px;margin-bottom:15px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}}
    </style></head><body>
    <div class="nav"><b>BABU PRO</b><span>@{user} <a href="/logout">Logout</a></span></div>
    <div class="feed">
    <div class="post"><b>@{user}</b><p>Welcome to Day 7! My site is now PRO! 🔥</p><p style="color:gray">Just now • ❤️ 12 likes</p></div>
    <div class="post"><b>@babu</b><p>Built with Flask + Render + SQLite</p><p style="color:gray">2 min ago • ❤️ 45 likes</p></div>
    <div class="post"><b>@system</b><p>Day 7 Completed! Next: Add Post feature?</p><p style="color:gray">5 min ago</p></div>
    </div></body></html>
    """

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password')
        conn=sqlite3.connect('users.db')
        try:
            conn.execute('INSERT INTO users VALUES (?,?)',(u,p)); conn.commit(); conn.close(); return redirect('/login')
        except:
            conn.close(); return "<h2>User exists!</h2><a href='/signup'>Try again</a>"
    return "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{background:#0f172a;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;font-family:sans-serif}.card{background:white;padding:30px;border-radius:20px;width:320px;text-align:center}input{width:90%;padding:12px;margin:8px;border-radius:8px;border:1px solid #ccc}button{background:#0f172a;color:white;padding:12px;width:95%;border-radius:10px;border:0}</style></head><body><div class='card'><h2>Create Account</h2><form method='POST'><input name='username' placeholder='Username' required><input name='password' type='password' placeholder='Password' required><button>Signup</button></form><p><a href='/login'>Have account? Login</a></p></div></body></html>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username'); p=request.form.get('password')
        conn=sqlite3.connect('users.db'); cur=conn.cursor()
        cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p)); ok=cur.fetchone(); conn.close()
        if ok:
            session['user']=u; return redirect('/')
        else:
            return "<h2 style='text-align:center;color:red'>Wrong Password!</h2><a href='/login' style='display:block;text-align:center'>Try Again</a>"
    return "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{background:#0f172a;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;font-family:sans-serif}.card{background:white;padding:30px;border-radius:20px;width:320px;text-align:center}input{width:90%;padding:12px;margin:8px;border-radius:8px;border:1px solid #ccc}button{background:#0f172a;color:white;padding:12px;width:95%;border-radius:10px;border:0}</style></head><body><div class='card'><h2>Login</h2><form method='POST'><input name='username' placeholder='Username' required><input name='password' type='password' placeholder='Password' required><button>Login</button></form><p><a href='/signup'>New? Signup</a></p></div></body></html>"

@app.route('/logout')
def logout():
    session.pop('user',None); return redirect('/')
