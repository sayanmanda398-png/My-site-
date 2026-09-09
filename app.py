from flask import Flask, request, jsonify
from datetime import datetime
import bot

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html style="background:#0a0a0a;color:#00ff88;font-family:monospace;padding:20px">
    <h1>🚀 PRO SITE LIVE from Siuri</h1>
    <p>Time: """+datetime.now().strftime("%H:%M:%S")+"""</p>
    <div style="border:1px solid #00ff88; padding:15px; border-radius:10px; margin-top:20px">
        <h3>Chat with my Bot:</h3>
        <input id="msg" placeholder="Type hi..." style="padding:10px;width:70%">
        <button onclick="send()" style="padding:10px;background:#00ff88;">Send</button>
        <p id="reply" style="margin-top:15px;color:white"></p>
    </div>
    <script>
    async function send(){
      let m=document.getElementById('msg').value;
      let r=await fetch('/bot?q='+m);
      let j=await r.json();
      document.getElementById('reply').innerText=j.reply;
    }
    </script>
    </html>
    """

@app.route("/bot")
def bot_chat():
    q = request.args.get("q","")
    return jsonify({"reply": bot.get_reply(q)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080)
