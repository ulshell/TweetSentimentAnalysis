from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50 import SQL
import os
import sys
import Tweethelp
from TweetAnalysis import TweetAnalyzer
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import gettempdir
import sqlite3
from functools import wraps


app = Flask(__name__)
db = SQL("sqlite:///TweetSentimentAnalysis.db")

#creating table users to store user's information in database
db.execute("CREATE TABLE if not exists users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL,name TEXT NOT NULL, hash TEXT NOT NULL)")
#creating table histories to store user's search history
db.execute("CREATE TABLE if not exists histories(screenname TEXT, search DATETIME DEFAULT CURRENT_TIMESTAMP, id INTEGER)")

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

'''configuring app'''
#directory where sessions files will be stored
app.config["SESSION_FILE_DIR"] = gettempdir()
#no permanent session
app.config["SESSION_PERMANENT"] = False
#use filesystem interface
app.config["SESSION_TYPE"] = "filesystem"

#for adding support of server-side sessions
Session(app)

def login_required(f):
    """
    Decorate routes to require login.
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
    """ Home page """
    #fetching name of current user logged in
    name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]
    return render_template("index.html", name=name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST method
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

        #fetch name of current user
        name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]

        # redirect user to home page
        return render_template("index.html", name=name)

    # else if user reached route via GET request
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login page
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    # if user reached route via POST method
    if request.method == "POST":

        #ensure name was submitted
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

        #fetching name from form page
        name=request.form.get("name")
        # insert the new user into users, storing the hash of the user's password
        result = db.execute("INSERT INTO users(username, name, hash) VALUES(:username, :name, :hash)", username=request.form.get("username"), name=name, hash=pwd_context.hash(request.form.get("password")))

        #check for username is unique or not
        if not result:
            error = "Username already exist"
            return render_template("sorry.html", message=error)

        # remember which user has logged in
        session["user_id"] = result

        # redirect user to home page
        return render_template("index.html", name=name)

    # else if user reached route via GET request
    else:
        return render_template("register.html")



@app.route("/history")
@login_required
def history():
    """Show history searched for further references."""
    #selecting all information of user's search history
    histories = db.execute("SELECT * from histories WHERE id=:id", id=session["user_id"])

    #fetch name of cureent user logged in
    name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]

    #render history template
    return render_template("history.html", histories=histories, name=name)

@app.route("/search")
@login_required
def search():

    #fetch screen_name from page
    screen_name = request.args.get("screen_name", "")
    # validate screen_name
    if not screen_name:
        return redirect(url_for("index"))

    #insert into searched @screen_name into history table
    db.execute("INSERT INTO histories(screenname, id) VALUES(:screenname, :id)",screenname=screen_name, id=session["user_id"])

    #fetch name of user currently logged in
    name = db.execute("SELECT name from users WHERE id=:id", id=session["user_id"])[0]["name"]

    #fetch the path of file positive-words.txt
    positives = os.path.join(sys.path[0], "positive-words.txt")

    #fetch the path of file negative-words.txt
    negatives = os.path.join(sys.path[0], "negative-words.txt")

    #passing bot files for analyzing
    analyzer = TweetAnalyzer(positives, negatives)

    # get screen_name's tweets
    tweets = Tweethelp.get_user_timeline(screen_name, 200)

    #Initializing variable for storing positive, negative and neutral
    positive, negative, neutral = 0.0, 0.0, 0.0

    #array to store tweets, variable to see type of tweet, and number
    twee = []

    k = 0
    m = ''

    #loop through all tweets fetched from twitter
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

    # generate pie chart
    chart = Tweethelp.chart(positive, negative, neutral)

    # render template to show analysis
    return render_template("search.html", chart=chart, screen_name=screen_name, twee=twee, name=name)
