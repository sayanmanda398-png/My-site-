from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, datetime, os
app = Flask(__name__)
app.secret_key = "babu_pro_123"
os.makedirs('static/uploads', exist_ok=True)
ADMIN_USER="Sayan"
ADMIN_PASS="Sayan@123"
def ist_now():
    return (datetime.datetime.utcnow()+datetime.timedelta(hours=5,minutes=30)).strftime("%I:%M %p - %d/%m")
def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, photo TEXT, bio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0, media TEXT, mtype TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, time TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))')
    conn.commit();conn.close()
init_db()
CSS="body{margin:0;background:#0a0a20;display:flex;justify-content:center;padding:20px 0;font-family:sans-serif}.phone{width:100%;max-width:360px;min-height:800px;background:linear-gradient(180deg,#2e40e6,#050516);border-radius:35px;padding:15px;color:white}.top-bar{display:flex;justify-content:space-between;padding:8px}.icon-btn{width:32px;height:32px;background:rgba(0,0,0,0.35);border-radius:50%;display:flex;justify-content:center;align-items:center;color:white;text-decoration:none}.chat-pill{background:#2a2fb8;border-radius:20px;padding:12px;margin:8px 0}.post-media{width:100%;border-radius:15px;margin-top:8px;max-height:220px;object-fit:cover}.btn-follow{background:#5a7cff;padding:6px 14px;border-radius:20px;color:white;text-decoration:none;font-size:11px}.btn-unfollow{background:gray;padding:6px 14px;border-radius:20px;color:white;text-decoration:none;font-size:11px}"

@app.route('/static/uploads/<path:f>')
def up(f): return send_from_directory('static/uploads',f)

@app.route('/', methods=['GET','POST'])
def home():
    user=session.get('user')
    if not user: return redirect('/login')
    conn=sqlite3.connect('users.db');cur=conn.cursor()
    if request.method=='POST':
        txt=request.form.get('content','').strip()
        mf=request.files.get('media'); mn=None; mt=None
        if mf and mf.filename:
            ext=mf.filename.rsplit('.',1)[-1].lower()
            mt='video' if ext in ['mp4','mov','webm'] else 'photo'
            mn=f"post_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{user}.{ext}"
            mf.save(os.path.join('static/uploads',mn))
        if txt or mn:
            cur.execute('INSERT INTO posts (username,content,time,likes,media,mtype) VALUES (?,?,?,?,?,?)',(user,txt,ist_now(),0,mn,mt));conn.commit()
    cur.execute('SELECT photo,bio FROM users WHERE username=?',(user,)); r=cur.fetchone(); photo=r[0] if r and r[0] else None; bio=r[1] if r and r[1] else "No bio yet"
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(user,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(user,)); following=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM posts WHERE username=?',(user,)); pc=cur.fetchone()[0]
    cur.execute('SELECT id,username,content,time,likes,media,mtype FROM posts ORDER BY id DESC'); posts=cur.fetchall()
    html=""
    for pid,uname,cont,tm,likes,media,mtype in posts:
        fb=""
        if uname!=user:
            cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(user,uname))
            fb=f"<a href='/unfollow/{uname}' class='btn-unfollow' style='float:right'>Following</a>" if cur.fetchone() else f"<a href='/follow/{uname}' class='btn-follow' style='float:right'>+ Follow</a>"
        mh=""
        if media:
            if mtype=='video': mh=f"<video class='post-media' controls src='/static/uploads/{media}'></video>"
            else: mh=f"<img class='post-media' src='/static/uploads/{media}'>"
        html+=f"<div class='chat-pill'><b>@{uname} - {tm}</b>{fb}<div>{cont}</div>{mh}<div><a href='/like/{pid}' style='color:#0ff'>❤️{likes}</a> <a href='/profile/{uname}' style='color:#fa7;font-size:10px'>View @{uname}</a></div></div>"
    conn.close()
    ph=f"<img src='/static/uploads/{photo}' style='width:90px;height:90px;border-radius:50%'>" if photo else "👤"
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><b>@{user}</b><div><a class='icon-btn' href='/edit_profile'>✏️</a> <a class='icon-btn' href='/logout'>⎋</a></div></div><div style='text-align:center;background:rgba(40,50,150,0.6);border-radius:30px;padding:15px'>{ph}<div>@{user}</div><div style='font-size:11px'>{bio}</div><div style='font-size:12px;margin:8px'>{pc} Posts | {followers} Followers | {following} Following</div><a href='/edit_profile' class='btn-follow'>Edit Bio</a></div><form method='POST' enctype='multipart/form-data' style='background:rgba(0,0,0,0.2);border-radius:20px;padding:10px;margin:10px 0'><input name='content' placeholder='What is happening?' style='flex:1;width:70%;padding:10px;border-radius:20px;color:black'><button style='background:#5a7cff;border-radius:50%;width:38px;height:38px'>↑</button><br><input type='file' name='media' accept='image/*,video/*' style='margin-top:6px;font-size:11px'></form><div style='max-height:400px;overflow:auto'>{html}</div></div></body></html>"

@app.route('/follow/<u>')
def follow(u):
    me=session.get('user')
    if not me or me==u: return redirect('/')
    conn=sqlite3.connect('users.db')
    try: conn.execute('INSERT INTO follows VALUES (?,?)',(me,u));conn.commit()
    except: pass
    conn.close(); return redirect('/')

@app.route('/unfollow/<u>')
def unfollow(u):
    me=session.get('user')
    conn=sqlite3.connect('users.db');conn.execute('DELETE FROM follows WHERE follower=? AND following=?',(me,u));conn.commit();conn.close(); return redirect('/')

@app.route('/profile/<u>')
def profile(u):
    me=session.get('user')
    if not me: return redirect('/login')
    conn=sqlite3.connect('users.db');cur=conn.cursor()
    cur.execute('SELECT photo,bio FROM users WHERE username=?',(u,)); r=cur.fetchone()
    if not r: return "No user <a href='/'>Back</a>"
    photo,bio=r; bio=bio or "No bio"
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(u,)); following=cur.fetchone()[0]
    cur.execute('SELECT id,content,time,likes,media,mtype FROM posts WHERE username=? ORDER BY id DESC',(u,)); posts=cur.fetchall()
    cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(me,u)); is_f=cur.fetchone()
    conn.close()
    ph=""
    for pid,c,t,lk,m,mt in posts:
        mh=""
        if m:
            if mt=='video': mh=f"<video class='post-media' controls src='/static/uploads/{m}'></video>"
            else: mh=f"<img class='post-media' src='/static/uploads/{m}'>"
        ph+=f"<div class='chat-pill'>{c}<br><small>{t} ❤️{lk}</small>{mh}</div>"
    btn=""
    if u!=me:
        btn=f"<a href='/unfollow/{u}' class='btn-unfollow'>Following</a>" if is_f else f"<a href='/follow/{u}' class='btn-follow'>+ Follow</a>"
    img=f"<img src='/static/uploads/{photo}' style='width:90px;height:90px;border-radius:50%'>" if photo else "👤"
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><a href='/'>← Back</a><div style='text-align:center;background:rgba(40,50,150,0.6);border-radius:30px;padding:15px;margin:10px 0'>{img}<h3>@{u}</h3><div>{bio}</div><div>{len(posts)} Posts | {followers} Followers | {following} Following</div><div style='margin-top:8px'>{btn}</div></div>{ph}</div></body></html>"

@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    me=session.get('user')
    conn=sqlite3.connect('users.db');cur=conn.cursor()
    if request.method=='POST':
        bio=request.form.get('bio','')[:150]
        cur.execute('UPDATE users SET bio=? WHERE username=?',(bio,me));conn.commit();conn.close();return redirect('/')
    cur.execute('SELECT bio FROM users WHERE username=?',(me,)); r=cur.fetchone(); bio=r[0] if r and r[0] else ""
    conn.close()
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><a href='/'>← Back</a><h3>Edit Bio</h3><form method='POST'><textarea name='bio' maxlength='150' style='width:100%;height:80px;border-radius:20px;padding:12px;color:black'>{bio}</textarea><button style='width:100%;background:#5a7cff;padding:14px;border-radius:10px;margin-top:10px;color:white'>Save Bio ✅</button></form></div></body></html>"

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    user=session.get('user');f=request.files.get('photo')
    if f and f.filename:
        ext=f.filename.rsplit('.',1)[-1].lower();fname=f"{user}.{ext}";f.save(os.path.join('static/uploads',fname))
        conn=sqlite3.connect('users.db');conn.execute('UPDATE users SET photo=? WHERE username=?',(fname,user));conn.commit();conn.close()
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
    return "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{background:#0a0a20;color:white;display:flex;justify-content:center;padding:20px}.phone{background:linear-gradient(180deg,#2e40e6,#050516);border-radius:35px;padding:20px;width:100%;max-width:360px}</style></head><body><div class='phone'><h2>Create Account</h2><form method='POST'><input name='username' placeholder='NAME' required style='width:100%;padding:12px;margin:6px 0;border-radius:20px;color:black'><input name='email' placeholder='EMAIL' type='email' required style='width:100%;padding:12px;margin:6px 0;border-radius:20px;color:black'><input name='password' type='password' placeholder='PASSWORD' required style='width:100%;padding:12px;margin:6px 0;border-radius:20px;color:black'><button style='width:100%;padding:12px;background:#5a7cff;border-radius:10px;margin-top:10px'>Sign up</button></form></div></body></html>"
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=request.form.get('username');p=request.form.get('password');conn=sqlite3.connect('users.db');cur=conn.cursor();cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p));ok=cur.fetchone();conn.close()
        if ok: session['user']=u;return redirect('/')
    return "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{background:#0a0a20;color:white;display:flex;justify-content:center;padding:20px}.phone{background:linear-gradient(180deg,#2e40e6,#050516);border-radius:35px;padding:20px;width:100%;max-width:360px}</style></head><body><div class='phone'><h2>Login</h2><form method='POST'><input name='username' placeholder='NAME' required style='width:100%;padding:12px;margin:6px 0;border-radius:20px;color:black'><input name='password' type='password' placeholder='PASSWORD' required style='width:100%;padding:12px;margin:6px 0;border-radius:20px;color:black'><button style='width:100%;padding:12px;background:#5a7cff;border-radius:10px;margin-top:10px'>Login</button></form><a href='/signup' style='color:#0ff'>Signup</a></div></body></html>"
@app.route('/logout')
def logout(): session.clear();return redirect('/login')
