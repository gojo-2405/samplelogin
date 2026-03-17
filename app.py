from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os
import time
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Environment variables (used in Kubernetes)
DB_HOST = os.getenv("DB_HOST", "mysql-service")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root123")
DB_NAME = os.getenv("DB_NAME", "login_db")


# ---------------------------
# Database Connection Retry
# ---------------------------
def get_connection():

    while True:
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

            return conn

        except mysql.connector.Error as err:

            print("Waiting for MySQL database...")
            time.sleep(3)


# ---------------------------
# Initialize Database
# ---------------------------
def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(255)
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()


init_db()


# ---------------------------
# Home Page
# ---------------------------
@app.route('/')
def index():
    return render_template("index.html")


# ---------------------------
# Signup
# ---------------------------
@app.route('/signup', methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users (username,password) VALUES (%s,%s)",
                (username, hashed_password)
            )

            conn.commit()

            flash("Account created successfully!", "success")
            return redirect(url_for("login"))

        except mysql.connector.Error:

            flash("Username already exists!", "danger")

        finally:

            cursor.close()
            conn.close()

    return render_template("signup.html")


# ---------------------------
# Login
# ---------------------------
@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=%s",
            (username,)
        )

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result and check_password_hash(result[0], password):

            return render_template("home.html", username=username)

        else:

            flash("Invalid username or password", "danger")

    return render_template("login.html")


# ---------------------------
# Logout
# ---------------------------
@app.route('/logout')
def logout():
    return redirect(url_for("login"))


# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
