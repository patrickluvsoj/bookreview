import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

# TODO
    # Create a DB for book list
    # Download book list from CSV to SQL
    # app route for book search
    # app route for book detail
    # app route for review submission
    # SQL db for book review 

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return "Fields are empty"

        # check if username exists
        stored_password = db.execute("SELECT password FROM users WHERE username = :username", {"username": username}).fetchone()
        if not stored_password:
            return "No user with that username"

          # check if password matches
        if check_password_hash(stored_password[0], password):
            # add to session["user_id"] = username
            session['user_id'] = username
            return redirect(url_for("search"))

        # TODO
            # Create github repo and add remote
            # ensure login happens
            # check what value returns when SELECT doesn't return anything
            # check return type of SELECT
            # navigate to book list page

    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def regsiter():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # check fields are not empty
        if not username or not password or not confirmation:
            # error message
            return f"Fields are empty"
        
        # check username is unique
        if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchall():
            return "Username already exists"
        
        # hash password
        if confirmation == password:
            pass_hash = generate_password_hash(password)
        else:
            return "Password does not match!"

        # store into database
        db.execute("INSERT INTO users (username, password) VALUES (:username, :hash)", {"username": username, "hash": pass_hash})
        db.commit()

        # route to login page
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    # Create the SQL database table TODO
    # download csv file into SQL writing an import function DONE
    # Query db based on search term w/ LIKE matches
    # Render list based on Jinja using Jquery
    # Redicre and render book detail page
    # Submit review and render review list using Jquery and Jinja


    return render_template("search.html")