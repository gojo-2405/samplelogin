from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

db_host = os.getenv("DB_HOST", "mysql-service")
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "root123")
db_name = os.getenv("DB_NAME", "login_db")

def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            password VARCHAR(50)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username,password) VALUES (%s,%s)", (username,password))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/login')

    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username,password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return render_template('home.html', username=username)
        else:
            return "Invalid Username or Password"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
