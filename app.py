from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# temporary user database
users = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if username in users:
        return "User already exists!"
    
    users[username] = password
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form["username"]
    password = request.form["password"]

    if username in users and users[username] == password:
        return f"<h1>Welcome {username}!</h1>"
    else:
        return "Invalid Login"

if __name__ == "__main__":
    app.run(debug=True)
