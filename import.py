import csv, os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

try:
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))
except RuntimeError:
    print("DATABASEURL is not set")

count = 0
with open('books.csv', newline='') as csvfile:
    books = csv.reader(csvfile, delimeter=',')
    for book in books:
        print(f" Inserting f{book[0]}....")
        db.execute('INSERT INTO books (isbn, title, author, yr) VALUES (:isbn, :title, :author, :yr)', {'isbn': book[0], 'title': book[1], 'author': book[2], 'yr': book[3]})
        db.commit()
        count += 1

print(f"Import completed! {count} titles imported!")

