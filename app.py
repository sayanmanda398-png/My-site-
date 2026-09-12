from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, datetime, os
app = Flask(__name__)
app.secret_key = "babu_pro_123"
os.makedirs('static/uploads', exist_ok=True)
ADMIN_USER = "Sayan"
ADMIN_PASS = "Sayan@123"

def ist_now():
    utc = datetime.datetime.utcnow()
    ist = utc + datetime.timedelta(hours=5, minutes=30)
    return ist.strftime("%I:%M %p - %d/%m")

def init_db():
    conn=sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, photo TEXT, bio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, time TEXT, likes INTEGER DEFAULT 0, media TEXT, mtype TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, content TEXT, time TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))')
    try: conn.execute('ALTER TABLE users ADD COLUMN photo TEXT')
    except: pass
    try: conn.execute('ALTER TABLE users ADD COLUMN bio TEXT')
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
.user-photo-box{width:100%;background:rgba(40,50,150,0.6);border-radius:30px;margin:10px 0;display:flex;flex-direction:column;justify-content:center;align-items:center;overflow:hidden;position:relative;border:1px solid rgba(255,255,255,0.1);box-sizing:border-box;padding:15px 10px}
.user-photo-box img{width:90px;height:90px;object-fit:cover;border-radius:50%;border:3px solid #5a7cff}
.follow-stats{display:flex;gap:15px;margin:10px 0;font-size:12px}
.follow-stats b{font-size:14px}
.chat-pill{background:#2a2fb8;border-radius:20px;padding:12px 14px;margin:8px 0;width:100%;box-sizing:border-box;font-size:13px;word-wrap:break-word}
.chat-pill img.post-media{width:100%;border-radius:15px;margin-top:8px;max-height:220px;object-fit:cover;display:block}
.chat-pill video.post-media{width:100%;border-radius:15px;margin-top:8px;max-height:280px;display:block}
.comment-box{background:rgba(0,0,0,0.25);border-radius:12px;padding:6px 10px;margin-top:6px;font-size:11px;word-wrap:break-word}
.comment-input{flex:1;background:rgba(255,255,255,0.1);border:1px dashed rgba(255,255,255,0.2);border-radius:20px;padding:6px 10px;color:white;outline:none;font-size:11px;min-width:0}
.search-box{width:100%;margin:8px 0;display:flex;gap:5px;box-sizing:border-box}
.search-inp{flex:1;min-width:0;background:rgba(0,0,0,0.3);border:1px dashed rgba(255,255,255,0.2);border-radius:30px;padding:10px 15px;color:white;outline:none;font-size:12px}
.post-form{background:rgba(0,0,0,0.2);border-radius:20px;padding:10px;margin:10px 0;width:100%;box-sizing:border-box}
.admin-card{background:rgba(255,255,255,0.1);border-radius:15px;padding:12px;margin:8px 0;font-size:12px;word-wrap:break-word}
.btn-follow{background:#5a7cff;border:none;padding:6px 14px;border-radius:20px;color:white;font-size:11px;font-weight:700;cursor:pointer}
.btn-unfollow{background:rgba(255,255,255,0.2);border:1px solid rgba(255,255,255,0.3);padding:6px 14px;border-radius:20px;color:white;font-size:11px;cursor:pointer}
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
    cur.execute('SELECT photo,bio FROM users WHERE username=?',(user,)); pr=cur.fetchone(); photo=pr[0] if pr and pr[0] else None; bio=pr[1] if pr and pr[1] else "No bio yet. Click Edit Profile ✏️"
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(user,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(user,)); following=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM posts WHERE username=?',(user,)); post_count=cur.fetchone()[0]
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
        # follow button for other users
        follow_btn=""
        if uname!=user:
            cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(user,uname))
            is_f = cur.fetchone()
            if is_f: follow_btn = f"<a href='/unfollow/{uname}' class='btn-unfollow' style='text-decoration:none;float:right;margin-left:5px'>Following ✓</a>"
            else: follow_btn = f"<a href='/follow/{uname}' class='btn-follow' style='text-decoration:none;float:right;margin-left:5px'>+ Follow</a>"
        media_html=""
        if media:
            if mtype=='video': media_html=f"<video class='post-media' controls src='/static/uploads/{media}'></video>"
            else: media_html=f"<img class='post-media' src='/static/uploads/{media}'>"
        chat_html+=f"<div class='chat-pill'><div style='display:flex;justify-content:space-between;align-items:center'><b style='font-size:10px;opacity:0.7'>@{uname} • {tm} 🇮🇳</b><div>{follow_btn}{del_btn}</div></div><div style='margin-top:6px'>{cont}</div>{media_html}<div style='margin-top:8px'><a href='/like/{pid}' style='color:#00e5ff;text-decoration:none'>❤️{likes}</a> <a href='/profile/{uname}' style='color:#ffaa77;text-decoration:none;font-size:10px;margin-left:10px'>View @{uname}</a></div>{comm_html}<form action='/comment/{pid}' method='POST' style='margin-top:6px;display:flex;gap:5px'><input class='comment-input' name='cmt' placeholder='Add comment...' required><button style='background:#5a7cff;border:none;border-radius:15px;padding:5px 10px;color:white;font-size:10px;min-width:45px'>Reply</button></form></div>"
    conn.close()
    if not chat_html: chat_html="<div class='chat-pill' style='opacity:0.5;text-align:center'>No posts yet. Upload photo/video!</div>"
    photo_html = f"<img src='/static/uploads/{photo}'>" if photo else f"<div style='font-size:40px'>👤</div>"
    admin_link = f"<a class='icon-btn' href='/admin' style='background:#ffaa00'>👑</a>" if user==ADMIN_USER else ""
    return f"""<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'>
    <div class='top-bar'><div class='top-left'><a class='icon-btn' href='#' onclick="document.getElementById('searchArea').style.display='flex';return false">🔍</a><div style='font-weight:bold;font-size:14px'>@{user}</div></div><div class='top-right'>{admin_link}<a class='icon-btn' href='/edit_profile'>✏️</a><a class='icon-btn' href='/logout'>⎋</a></div></div>
    <div id='searchArea' class='search-box' style='display:{"flex" if q else "none"}'><form method='GET' style='display:flex;gap:5px;width:100%'><input class='search-inp' name='q' value='{q}' placeholder='Search users or posts...'><button class='icon-btn' style='width:42px;min-width:42px'>Go</button><a class='icon-btn' href='/'>✕</a></form></div>
    <div class='user-photo-box'>{photo_html}<div style='margin-top:8px;font-weight:bold'>@{user}</div><div style='font-size:11px;opacity:0.8;text-align:center;margin:5px 0;max-width:250px;word-wrap:break-word'>{bio}</div><div class='follow-stats'><div><b>{post_count}</b> Posts</div><div><b>{followers}</b> Followers</div><div><b>{following}</b> Following</div></div><div style='display:flex;gap:6px'><a href='/edit_profile' class='btn-follow' style='text-decoration:none'>✏️ Edit Profile</a><form action='/upload_photo' method='POST' enctype='multipart/form-data'><label style='background:rgba(255,255,255,0.2);padding:6px 12px;border-radius:20px;font-size:11px;cursor:pointer'>📷 Photo<input type='file' name='photo' accept='image/*' hidden onchange='this.form.submit()'></label></form></div></div>
    <form class='post-form' method='POST' enctype='multipart/form-data'><div style='display:flex;gap:5px'><input name='content' placeholder='What is happening?!' style='flex:1;min-width:0;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:10px 15px;color:white;outline:none'><button style='background:#5a7cff;border:none;border-radius:50%;width:38px;min-width:38px;height:38px;color:white'>↑</button></div><div style='margin-top:8px;display:flex;gap:8px;align-items:center'><label style='background:rgba(255,255,255,0.15);padding:6px 12px;border-radius:20px;font-size:11px;cursor:pointer'>📷 Photo/Video<input type='file' name='media' accept='image/*,video/*' hidden></label><span style='font-size:10px;opacity:0.6'>IST 🇮🇳</span></div></form>
    <div style='max-height:320px;overflow-y:auto;padding-right:2px'>{chat_html}</div>
    </div></body></html>"""

@app.route('/follow/<u>')
def follow(u):
    me=session.get('user')
    if not me or me==u: return redirect('/')
    conn=sqlite3.connect('users.db');
    try: conn.execute('INSERT INTO follows VALUES (?,?)',(me,u)); conn.commit()
    except: pass
    conn.close(); return redirect(request.referrer or '/')

@app.route('/unfollow/<u>')
def unfollow(u):
    me=session.get('user')
    if not me: return redirect('/')
    conn=sqlite3.connect('users.db'); conn.execute('DELETE FROM follows WHERE follower=? AND following=?',(me,u)); conn.commit(); conn.close(); return redirect(request.referrer or '/')

@app.route('/profile/<u>')
def profile(u):
    me=session.get('user')
    if not me: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT photo,bio FROM users WHERE username=?',(u,)); row=cur.fetchone()
    if not row: conn.close(); return "<h1>User not found</h1><a href='/'>Back</a>"
    photo,bio=row; bio=bio or "No bio"
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(u,)); following=cur.fetchone()[0]
    cur.execute('SELECT id,content,time,likes,media,mtype FROM posts WHERE username=? ORDER BY id DESC',(u,)); posts=cur.fetchall()
    cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(me,u)); is_f=cur.fetchone()
    conn.close()
    posts_html="".join([f"<div class='chat-pill'>{c}<br><span style='font-size:10px;opacity:0.6'>{t} • ❤️{lk}</span>{'<br><img class=post-media src=/static/uploads/'+str(m)+'>' if m and mt!='video' else ''}{'<br><video class=post-media controls src=/static/uploads/'+str(m)+'></video>' if m and mt=='video' else ''}</div>" for _,c,t,lk,m,mt in posts]) or "<div class='chat-pill' style='opacity:0.5;text-align:center'>No posts</div>"
    photo_html = f"<img src='/static/uploads/{photo}'>" if photo else "<div style='font-size:40px'>👤</div>"
    fb = f"<a href='/unfollow/{u}' class='btn-unfollow' style='text-decoration:none'>Following ✓</a>" if is_f else f"<a href='/follow/{u}' class='btn-follow' style='text-decoration:none'>+ Follow</a>"
    fb = "" if u==me else fb
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><a class='icon-btn' href='/'>←</a><b>@{u}</b><div style='width:32px'></div></div><div class='user-photo-box'>{photo_html}<div style='font-weight:bold;margin-top:8px'>@{u}</div><div style='font-size:11px;opacity:0.8;text-align:center;margin:5px'>{bio}</div><div class='follow-stats'><div><b>{len(posts)}</b> Posts</div><div><b>{followers}</b> Followers</div><div><b>{following}</b> Following</div></div>{fb}</div><div style='max-height:400px;overflow:auto'>{posts_html}</div></div></body></html>"

@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    me=session.get('user')
    if not me: return redirect('/login')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        bio=request.form.get('bio','')[:150]
        email=request.form.get('email','')
        cur.execute('UPDATE users SET bio=?, email=? WHERE username=?',(bio,email,me)); conn.commit()
        conn.close(); return redirect('/')
    cur.execute('SELECT email,bio FROM users WHERE username=?',(me,)); r=cur.fetchone(); email=r[0] if r else ""; bio=r[1] if r and r[1] else ""
    conn.close()
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><a class='icon-btn' href='/'>←</a><b>✏️ Edit Profile</b><div style='width:32px'></div></div><form method='POST' style='padding:20px 10px'><label style='font-size:11px;opacity:0.7'>Email</label><input name='email' value='{email}' style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:20px;padding:12px 15px;color:white;box-sizing:border-box;margin:6px 0 15px 0'><label style='font-size:11px;opacity:0.7'>Bio (150 chars)</label><textarea name='bio' maxlength='150' style='width:100%;height:80px;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:20px;padding:12px 15px;color:white;box-sizing:border-box;margin:6px 0;resize:none'>{bio}</textarea><button style='width:100%;background:linear-gradient(90deg,#6a8cff,#4a5cff);border:none;padding:14px;border-radius:10px;font-weight:800;color:#0a0a2a;margin-top:15px'>Save Profile ✅</button></form><div style='text-align:center;font-size:10px;opacity:0.5;margin-top:20px'>Tip: Add emoji to bio 😎🔥💯</div></div></body></html>"

@app.route('/admin', methods=['GET','POST'])
def admin():
    user=session.get('user')
    if user!=ADMIN_USER: return "<html><body style='background:#111;color:white;text-align:center;padding:50px'><h1>⛔ Not Admin</h1><a href='/'>Back</a></body></html>"
    if request.method=='POST':
        pw=request.form.get('admin_pass','')
        if pw==ADMIN_PASS: session['is_admin']=True
        else: return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div style='text-align:center;padding:40px'><h2>❌ Wrong Password!</h2><a href='/admin' style='color:#5a7cff'>Try Again</a></div></div></body></html>"
    if not session.get('is_admin'):
        return f"""<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><div class='top-left'><a class='icon-btn' href='/'>←</a><b>👑 ADMIN LOCK</b></div></div><div style='text-align:center;padding:30px 10px'><div style='font-size:50px'>🔒</div><h3>Admin Password Required</h3><p style='font-size:12px;opacity:0.7'>Only owner</p><form method='POST' style='margin-top:20px'><input name='admin_pass' type='password' placeholder='Enter Admin Password' style='width:100%;background:rgba(80,80,130,0.5);border:2px dashed rgba(255,255,255,0.15);border-radius:30px;padding:14px 20px;color:white;box-sizing:border-box;text-align:center' required><button style='width:100%;background:linear-gradient(90deg,#ffaa00,#ff6a00);border:none;padding:14px;border-radius:10px;font-weight:800;color:black;margin-top:12px'>Unlock 🔓</button></form></div></div></body></html>"""
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT username,email,bio FROM users'); users=cur.fetchall()
    cur.execute('SELECT COUNT(*), SUM(likes) FROM posts'); stats=cur.fetchone(); total_posts=stats[0] or 0; total_likes=stats[1] or 0
    cur.execute('SELECT id,username,content,time FROM posts ORDER BY id DESC'); posts=cur.fetchall()
    cur.execute('SELECT COUNT(*) FROM follows'); follows=cur.fetchone()[0]
    conn.close()
    users_html="".join([f"<div class='admin-card'><b>@{u}</b> • {e}<br><span style='opacity:0.6'>{b[:30]}</span><a href='/admin_del_user/{u}' style='color:#ff6b6b;float:right'>Delete</a></div>" for u,e,b in users])
    return f"<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>{CSS}</style></head><body><div class='phone'><div class='top-bar'><div class='top-left'><a class='icon-btn' href='/'>←</a><b>👑 ADMIN</b></div><div class='top-right'><a class='icon-btn' href='/admin_logout'>🔒</a></div></div><div style='background:linear-gradient(90deg,#ffaa00,#ff6a00);padding:15px;border-radius:20px;margin:10px 0;text-align:center;color:black'><div style='font-size:26px;font-weight:800'>{total_posts} Posts</div><div style='font-size:12px'>{len(users)} Users • {total_likes} Likes • {follows} Follows</div></div><h3 style='font-size:12px'>USERS ({len(users)})</h3><div style='max-height:250px;overflow:auto'>{users_html}</div></div></body></html>"

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin',None); return redirect('/admin')
@app.route('/admin_del_user/<u>')
def admin_del_user(u):
    if session.get('user')!=ADMIN_USER or not session.get('is_admin'): return redirect('/admin')
    if u!=ADMIN_USER:
        conn=sqlite3.connect('users.db'); conn.execute('DELETE FROM users WHERE username=?',(u,)); conn.execute('DELETE FROM posts WHERE username=?',(u,)); conn.execute('DELETE FROM follows WHERE follower=? OR following=?',(u,u)); conn.commit(); conn.close()
    return redirect('/admin')
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    user=session.get('user')
    if not user: return redirect('/login')
    f=request.files.get('photo')
    if f and f.filename:
        ext=f.filename.rsplit('.',1)[-1].lower(); fname=f"{user}.{ext}"; f.save(os.path.join('static/uploads',fname))
        conn=sqlite3.connect('uscat >> ~/MySite/app.py << 'PY'
ers.db'); conn.execute('UPDATE users SET photo=? WHERE username=?',(fname,user)); conn.commit(); conn.close()
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
        try: conn.execute('INSERT INTO users VALUES (?,?,?,?,?)',(u,e,p,None,None)); conn.commit(); conn.close(); return redirect('/login')
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
