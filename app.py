
# FOLLOW SYSTEM PATCH
@app.route('/follow/<u>')
def follow(u):
    me=session.get('user')
    if not me or me==u: return redirect('/')
    conn=sqlite3.connect('users.db')
    try: conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))'); conn.execute('INSERT INTO follows VALUES (?,?)',(me,u)); conn.commit()
    except: pass
    conn.close(); return redirect('/')

@app.route('/unfollow/<u>')
def unfollow(u):
    me=session.get('user')
    conn=sqlite3.connect('users.db'); conn.execute('CREATE TABLE IF NOT EXISTS follows (follower TEXT, following TEXT, PRIMARY KEY(follower,following))'); conn.execute('DELETE FROM follows WHERE follower=? AND following=?',(me,u)); conn.commit(); conn.close(); return redirect('/')

@app.route('/profile/<u>')
def profile(u):
    me=session.get('user')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    cur.execute('SELECT photo FROM users WHERE username=?',(u,)); row=cur.fetchone()
    photo=row[0] if row else None
    cur.execute('SELECT COUNT(*) FROM follows WHERE following=?',(u,)); followers=cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM follows WHERE follower=?',(u,)); following=cur.fetchone()[0]
    cur.execute('SELECT id,content,time,likes,media,mtype FROM posts WHERE username=? ORDER BY id DESC',(u,)); posts=cur.fetchall()
    cur.execute('SELECT * FROM follows WHERE follower=? AND following=?',(me,u)); is_f=cur.fetchone()
    conn.close()
    html=""
    for pid,c,t,lk,m,mt in posts:
        media=""
        if m:
            if mt=='video': media=f"<video style='width:100%;border-radius:15px;margin-top:8px' controls src='/static/uploads/{m}'></video>"
            else: media=f"<img style='width:100%;border-radius:15px;margin-top:8px' src='/static/uploads/{m}'>"
        html+=f"<div style='background:#2a2fb8;padding:12px;border-radius:20px;margin:8px 0'>{c}<br><small>{t} ❤️{lk}</small>{media}</div>"
    btn = f"<a href='/unfollow/{u}' style='background:gray;padding:6px 14px;border-radius:20px;color:white;text-decoration:none'>Following</a>" if is_f else f"<a href='/follow/{u}' style='background:#5a7cff;padding:6px 14px;border-radius:20px;color:white;text-decoration:none'>+ Follow</a>"
    if u==me: btn=""
    return f"<div style='max-width:360px;margin:auto;background:linear-gradient(180deg,#2e40e6,#050516);min-height:100vh;padding:15px;color:white;border-radius:35px'><a href='/'>← Back</a><h2>@{u}</h2><p>{followers} Followers | {following} Following</p>{btn}<hr>{html}</div>"

@app.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    me=session.get('user')
    conn=sqlite3.connect('users.db'); cur=conn.cursor()
    if request.method=='POST':
        bio=request.form.get('bio','')[:150]
        cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, email TEXT, password TEXT, photo TEXT, bio TEXT)'); cur.execute('UPDATE users SET bio=? WHERE username=?',(bio,me)); conn.commit(); conn.close(); return redirect('/')
    cur.execute('SELECT bio FROM users WHERE username=?',(me,)); r=cur.fetchone(); bio=r[0] if r and r[0] else ""
    conn.close()
    return f"<div style='max-width:360px;margin:auto;background:linear-gradient(180deg,#2e40e6,#050516);min-height:100vh;padding:15px;color:white;border-radius:35px'><a href='/'>←</a><h2>Edit Bio</h2><form method='POST'><textarea name='bio' maxlength='150' style='width:100%;height:80px;border-radius:20px;padding:12px;color:black'>{bio}</textarea><button style='width:100%;background:#5a7cff;padding:14px;border-radius:10px;margin-top:12px;color:white'>Save Bio</button></form></div>"
