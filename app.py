from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "<h1>BABU's PRO Site is LIVE! 🚀</h1><p>Day 4 - GitHub to World!</p>"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9080)
