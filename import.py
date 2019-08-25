import csv, os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

try:
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))
except RuntimeError:
    print("DATABASE_URL is not set")

count = 0
with open('books.csv', newline='') as csvfile:
    books = csv.reader(csvfile)
    next (books)
    for book in books:
        print(f" Inserting {book[1]}....")
        db.execute('INSERT INTO books (title, author, yr, isbn) VALUES (:title, :author, :yr, :isbn)', 
            {'title': book[1], 'author': book[2], 'yr': int(book[3]), 'isbn': book[0]})
        db.commit()
        count += 1

print(f"Import completed! {count} titles imported!")

