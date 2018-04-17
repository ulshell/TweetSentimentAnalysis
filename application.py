from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50 import SQL
import os
import sys
import helpers
from analyzer import Analyzer
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import sqlite3
from functools import wraps

#con = sqlite3.connect("Sentiments.db")
#cur = con.cursor()

f = open("sentiment.db", "w")
f.close()

app = Flask(__name__)
db = SQL("sqlite:///sentiment.db")
# ensure responses aren't cached
db.execute("CREATE TABLE if not exists users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL,name TEXT NOT NULL, hash TEXT NOT NULL)")
db.execute("CREATE TABLE if not exists histories(screenname TEXT, search DATETIME DEFAULT CURRENT_TIMESTAMP, id INTEGER)")
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

app.config["SESSION_FILE_DIR"] = gettempdir()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function



@app.route("/")
@login_required
def index():
    name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]
    return render_template("index.html", name=name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username"
            return render_template("sorry.html", message=error)

        # ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("sorry.html", message=error)

        # query database for username
        rows = db.execute("SELECT * FROM users \
                     WHERE username = :username", \
                     username=request.form.get("username"))


        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            error = "invalid username and/or password"
            return render_template("sorry.html", message=error)

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]
        # redirect user to home page
        return render_template("index.html", name=name)

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    if request.method == "POST":

        if not request.form.get("name"):
            error = "Must provide name"
            return render_template("sorry.html", message=error)
        # ensure username was submitted
        elif not request.form.get("username"):
            error = "Must provide username"
            return render_template("sorry.html", message=error)

        # ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("sorry.html", message=error)

        # ensure password and verified password is the same
        elif request.form.get("password") != request.form.get("passwordagain"):
            error = "password doesn't match"
            return render_template("sorry.html", message=error)

        # insert the new user into users, storing the hash of the user's password
        name=request.form.get("name")
        result = db.execute("INSERT INTO users(username, name, hash) VALUES(:username, :name, :hash)", username=request.form.get("username"), name=name, hash=pwd_context.hash(request.form.get("password")))

        if not result:
            error = "Username already exist"
            return render_template("sorry.html", message=error)

        # remember which user has logged in
        session["user_id"] = result
        name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]
        # redirect user to home page
        return render_template("index.html", name=name)

    else:
        return render_template("register.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    histories = db.execute("SELECT * from histories WHERE id=:id", id=session["user_id"])
    name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]
    return render_template("history.html", histories=histories, name=name)

@app.route("/search")
@login_required
def search():

    # validate screen_name
    screen_name = request.args.get("screen_name", "")
    if not screen_name:
        return redirect(url_for("index"))
    db.execute("INSERT INTO histories(screenname, id) VALUES(:screenname, :id)",screenname=screen_name, id=session["user_id"])
    name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]
    positives = os.path.join(sys.path[0], "positive-words.txt")
    negatives = os.path.join(sys.path[0], "negative-words.txt")

    analyzer = Analyzer(positives, negatives)

    # get screen_name's tweets
    tweets = helpers.get_user_timeline(screen_name, 200)


    positive, negative, neutral = 0.0, 0.0, 0.0
    twee = []
    k = 0
    m = ''
    for tweet in tweets:
        c = 0
        score = analyzer.analyze(tweet)
        if score > 0.0:
            positive += 1
            c = 1
        elif score < 0.0:
            negative += 1
            c = -1
        else:
            neutral += 1
        k += 1
        m = str(k) + '.) '
        twee.append((tweet, c, m))

    # generate chart
    chart = helpers.chart(positive, negative, neutral)

    # render results
    return render_template("search.html", chart=chart, screen_name=screen_name, twee=twee, name=name)
