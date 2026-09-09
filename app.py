from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{font-family:sans-serif;background:#0f172a;color:white;text-align:center;padding:40px}
    .card{background:white;color:#0f172a;padding:30px;border-radius:20px;max-width:400px;margin:auto;box-shadow:0 10px 30px rgba(0,0,0,.3)}
    a{ background:#0f172a;color:white;padding:12px 20px;border-radius:10px;text-decoration:none;display:inline-block;margin:10px}
    </style></head>
    <body>
    <h1>Hi, I'm BABU 🚀</h1>
    <p>Developer from Termux</p>
    <div class="card">
    <h2>My Site is LIVE</h2>
    <p>Built with Flask + GitHub + Render</p>
    <a href="https://github.com/sayanmanda398-png/My-site-">My GitHub</a>
    <a href="https://instagram.com/">Instagram</a>
    </div>
    <p style="margin-top:30px;opacity:.6">Deployed at: my-site-iqac.onrender.com</p>
    </body></html>
    """
