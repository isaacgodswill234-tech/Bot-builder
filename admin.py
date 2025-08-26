from flask import Flask, render_template_string
import json, os

DATA_FILE = "users.json"
app = Flask(__name__)

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

@app.route("/")
def home():
    users = load_users()
    return render_template_string("""
        <h1>Bot Builder Admin</h1>
        <table border="1" cellpadding="5">
            <tr><th>User ID</th><th>Bot Token</th><th>Status</th></tr>
            {% for uid, data in users.items() %}
            <tr>
                <td>{{ uid }}</td>
                <td>{{ data['token'] }}</td>
                <td>{{ "Premium" if data['premium'] else "Free" }}</td>
            </tr>
            {% endfor %}
        </table>
    """, users=users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)