from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os
import time

app = Flask(__name__)
app.secret_key = "secretkey123"

# Database configuration (from Kubernetes env variables)
db_host = os.getenv("DB_HOST", "mysql-service")
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "root123")
db_name = os.getenv("DB_NAME", "login_db")


def get_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )


# Wait until database is ready
def init_db():
    while True:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(50)
            )
            """)

            conn.commit()
            cursor.close()
            conn.close()

            print("Database ready")
            break

        except:
            print("Waiting for database...")
            time.sleep(3)


init_db()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/signup', methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username,password) VALUES (%s,%s)",
                (username, password)
            )
            conn.commit()

            flash("Account created successfully!", "success")
            return redirect(url_for("login"))

        except:
            flash("Username already exists", "danger")

        cursor.close()
        conn.close()

    return render_template("signup.html")


@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return render_template("home.html", username=username)

        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route('/logout')
def logout():
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
