from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return """
    <h1 style='text-align:center;margin-top:100px;font-family:sans-serif'>BABU's PRO Site LIVE! 🚀</h1>
    <p style='text-align:center'>Deployed from Termux + GitHub</p>
    """
