from flask import Flask, render_template_string, jsonify
import json

app = Flask(__name__)
DATA_FILE = "users.json"

def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

@app.route("/")
def index():
    users = load_users()
    html = "<h1>Bot Factory Admin Panel</h1>"
    for uid, data in users.items():
        html += f"<h2>User ID: {uid}</h2>"
        for bot in data.get("bots", []):
            html += f"<p>Bot Token: {bot['token']}</p>"
            html += f"<p>Theme: {bot['theme']}</p>"
            html += f"<p>Must Join Channels: {', '.join(bot['must_join_channels'])}</p>"
            html += f"<p>Participants: {bot['participants']}/{bot['max_participants']}</p>"
            html += f"<p>Balance: ₦{data.get('balance',0)}</p>"
            html += "<hr>"
    return html

@app.route("/api/users")
def api_users():
    return jsonify(load_users())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)