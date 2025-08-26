from flask import Flask, render_template_string, request, Response
import json, os

DATA_FILE = "users.json"
ADMIN_USER = "admin"      # change this to your username
ADMIN_PASS = "password"   # change this to a strong password

app = Flask(__name__)

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    return Response(
        'Login required.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

@app.before_request
def require_login():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

@app.route("/")
def admin_home():
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