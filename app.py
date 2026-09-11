from flask import Flask, request, redirect, session, url_for
import sqlite3, os
app = Flask(__name__)
app.secret_key = "babu_pro_123"

def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.execute("INSERT OR IGNORE INTO users VALUES ('babu','1234')")
    conn.commit(); conn.close()
init_db()

@app.route('/')
def home():
    user = session.get('user')
    if user:
        return f"<h1 style='text-align:center;margin-top:50px'>Welcome {user}!</h1><p style='text-align:center'><a href='/logout'>Logout</a></p>"
    return "<html><body style='font-family:sans-serif;text-align:center;padding:40px;background:#0f172a;color:white'><h1>BABU PRO - Day 6</h1><div style='background:white;color:black;padding:20px;border-radius:15px;max-width:350px;margin:auto'><a href='/login'>Login</a> | <a href='/signup'>Signup</a></div></body></html>"

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        u=request.form.get('username'); p=request.form.get('password')
        conn=sqlite3.connect('users.db'); 
        try:
            conn.execute('INSERT INTO users VALUES (?,?)',(u,p)); conn.commit()
            conn.close(); return redirect('/login')
        except:
            conn.close(); return "<h2>User exists!</h2><a href='/signup'>Try again</a>"
    return "<html><body style='background:#0f172a;display:flex;justify-content:center;align-items:center;height:100vh'><div style='background:white;padding:30px;border-radius:20px;width:320px;text-align:center'><h2>Signup</h2><form method='POST'><input name='username' placeholder='New Username' required style='width:90%;padding:10px;margin:5px'><input name='password' type='password' placeholder='New Password' required style='width:90%;padding:10px;margin:5px'><button style='padding:10px;width:95%;background:black;color:white;border-radius:10px'>Create Account</button></form><p><a href='/login'>Already have account?</a></p></div></body></html>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u=request.form.get('username'); p=request.form.get('password')
        conn=sqlite3.connect('users.db'); cur=conn.cursor()
        cur.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p))
        ok=cur.fetchone(); conn.close()
        if ok:
            session['user']=u; return redirect('/')
        else:
            return "<h1 style='text-align:center;color:red'>Wrong!</h1><a href='/login' style='display:block;text-align:center'>Try Again</a>"
    return "<html><body style='background:#0f172a;display:flex;justify-content:center;align-items:center;height:100vh'><div style='background:white;padding:30px;border-radius:20px;width:320px;text-align:center'><h2>Login</h2><form method='POST'><input name='username' placeholder='Username' required style='width:90%;padding:10px;margin:5px'><input name='password' type='password' placeholder='Password' required style='width:90%;padding:10px;margin:5px'><button style='padding:10px;width:95%;background:black;color:white;border-radius:10px'>Login</button></form><p><a href='/signup'>Create new?</a></p></div></body></html>"

@app.route('/logout')
def logout():
    session.pop('user',None); return redirect('/')
