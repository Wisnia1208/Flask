from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session
from flask_session import Session
import sqlite3

app = Flask("I <3 ZMITAC")
DATABASE = "database.db"
sess = Session()


@app.route("/create_database", methods=["GET"])
def create_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            isadmin INTEGER DEFAULT 0
        )
    """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            book_name TEXT NOT NULL,
            review TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        )
    """
    )@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    if request.method == "POST":
        book_title = request.form["book_title"]
        cur.execute("INSERT INTO books (title) VALUES (?)", (book_title,))
        con.commit()

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    cur.execute("SELECT * FROM users WHERE username = ?", (session["user"],))
    user = cur.fetchone()

    con.close()

    return render_template("t2.html", userdata={"login": session["user"], "isadmin": user[3]}, books=books)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (username, password, isadmin) VALUES (?, ?, ?)",
        ("admin", "password", 1),
    )
    conn.commit()
    conn.close()
    return "ok"


@app.route("/add", methods=["GET", "POST"])
def add_user():
    if "user" not in session:
        return redirect(url_for("login"))
    print(session["user"])
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (session["user"],))
    user = cur.fetchone()
    if user[3] != 1:
        return redirect(url_for("index"))
    if request.method == "GET":
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        print(users)
        return render_template("t4.html", users=users)
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        print(login, password)
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO users (username, password, isadmin) VALUES (?, ?, ?)",
            (login, password, 0),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("add_user"))


@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    if request.method == "POST":
        book_title = request.form["book_title"]
        cur.execute("INSERT INTO books (title) VALUES (?)", (book_title,))
        con.commit()

    cur.execute("SELECT * FROM books")
    books = cur.fetchall()

    cur.execute("SELECT * FROM users WHERE username = ?", (session["user"],))
    user = cur.fetchone()

    con.close()

    return render_template("t3.html", userdata={"login": session["user"], "isadmin": user[3]}, books=books)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?", (login, password)
        )
        user = cur.fetchone()
        con.close()
        if user:
            session["user"] = login
            return redirect(url_for("index"))
        else:
            return "Invalid username or password"
    elif request.method == "GET":
        if "user" in session:
            return redirect(url_for("index"))
        else:
            return render_template("t1.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("index"))

@app.route("/user/<int:user_id>", methods=["GET"])
def user_details(user_id):
    if "user" not in session:
        return redirect(url_for("login"))

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    con.close()

    if user:
        return render_template("user_details.html", user=user)
    else:
        return "User not found", 404


app.secret_key = "super secret key"
app.config["SESSION_TYPE"] = "filesystem"
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()
