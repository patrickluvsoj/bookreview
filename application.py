import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

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
def index():
    # check if POST
    if request.method == 'POST':
        username = request.form.get("username")
        entered_password = request.form.get("password")

        # check if password matches
        stored_password = db.execute("SELECT password FROM users WHERE username = :username", {"username": username}).fetchone()

        print(f'SQL query return value is: {stored_password}')
        
        # check if username exists
        if not stored_password:
            return "No user with that username"

        # add to session["user_id"] = username
        if stored_password == entered_password:
            session['user_id'] = username
            return "Login success!"
        
        # navigate to book list page

        # TODO
            # ensure login happens
            # check what value returns when SELECT doesn't return anything
            # check return type of SELECT

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
            return f"Fields are empty: {username}, {password}, {confirmation}"
        
        # check username is unique
        if db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchall():
            return "Username already exists"
        
        # hash password
        if confirmation == password:
            pass_hash = generate_password_hash(password)
        else:
            return "password does not match!"

        # store into database
        db.execute("INSERT INTO users (username, password) VALUES (:username, :hash)", {"username": username, "hash": pass_hash})
        db.commit()

        # route to login page
        return render_template("login.html")

    return render_template("register.html")

