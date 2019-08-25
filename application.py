import os, requests, json

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

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



@app.route("/logout")
def logout():
    # logout session and redirect to login
    session.clear()
    return redirect(url_for("login"))



@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search = request.form.get('search')
        results = db.execute("SELECT title FROM books WHERE author LIKE(:author) OR title LIKE(:title) OR isbn LIKE(:isbn)",
        {'author': search+'%', 'title': search+'%', 'isbn': search+'%'}).fetchall()

        return render_template('search.html', results=results)


    return render_template("search.html")



@app.route("/details=<string:title>", methods=['GET', 'POST'])
@login_required
def details(title):
    # book details
    result = db.execute("SELECT author, yr, isbn FROM books WHERE title = :title", {'title': title}).fetchone()

    # get Goodread api response
    params ={'isbns': result[2],
            'key': 'nijqZdzaC9cIsNH2X0haA'}
    json_response = requests.get('https://www.goodreads.com/book/review_counts.json', params=params).json()
    goodreads = []
    avg_rating = json_response['books'][0]['average_rating']
    review_count = json_response['books'][0]['ratings_count']
    goodreads.append(avg_rating)
    goodreads.append(review_count)


    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        # store ratings into SQL
        db.execute("INSERT INTO reviews (rating, comment, isbn) VALUES (:rating, :comment, :isbn)", {'rating': rating, 'comment': comment, 'isbn': result[2]})
        db.commit()
        
        # query ratings
        ratings = db.execute("SELECT rating, comment FROM reviews WHERE isbn = :isbn", {'isbn': result[2]}).fetchall()

        return render_template("details.html", result=result, title=title, ratings=ratings, goodreads=goodreads)

    # query ratings
    ratings = db.execute("SELECT rating, comment FROM reviews WHERE isbn = :isbn", {'isbn': result[2]}).fetchall()

    return render_template("details.html", result=result, title=title, ratings=ratings, goodreads=goodreads)


@app.route("/api=<string:isbn>")
def api(isbn):
    # get book details
    result = db.execute("SELECT title, author, yr FROM books WHERE isbn = :isbn", {'isbn': isbn}).fetchone()

    # get goodreads data
    params = {'isbns': isbn, 'key': 'nijqZdzaC9cIsNH2X0haA'}
    response = requests.get('https://www.goodreads.com/book/review_counts.json', params=params).json()

    # prepare data and convert to json string
    json_response = json.dumps({"title": result[0],
        "author": result[1],
        "year": result[2],
        "isbn": isbn,
        "review_count": response['books'][0]['ratings_count'],
        "average_count": response['books'][0]['average_rating']
    })

    # return json_response
    return json_response