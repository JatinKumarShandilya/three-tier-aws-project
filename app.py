from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

load_dotenv()
app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return connection

@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def home():
    return "Welcome to our Three-Tier Application!"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        sql = """
        SELECT * FROM users
        WHERE email = %s
        """

        cursor.execute(sql, (email,))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("dashboard"))
        return "Invalid email or password!"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        cursor = connection.cursor()

        sql = """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
        """

        try:
            cursor.execute(sql, (username, email, password_hash))
            connection.commit()
        except mysql.connector.Error:
            connection.rollback()
            return "Username or email already exists!"

        cursor.close()
        connection.close()

        print("Username:", username)
        print("Email:", email)
        # print("Password:", password_hash)

        return "Registration data received!"

    return render_template("register.html")

connection = get_db_connection()
print("MySQL connection successful!")
connection.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)