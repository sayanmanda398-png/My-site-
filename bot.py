def get_reply(msg):
    msg = msg.lower()
    if "hi" in msg or "hello" in msg:
        return "Hey! 👋 Welcome to my PRO site from Siuri!"
    elif "link" in msg:
        return "My site is live 24/7 with Cloudflare Tunnel!"
    elif "babu" in msg:
        return "Yes, I'm Babu's bot — built in Termux!"
    elif "help" in msg:
        return "Ask me: hi, link, babu, time, about"
    else:
        return f"You said: '{msg}'. Try typing 'help' 😊"

