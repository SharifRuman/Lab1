import csv
import psycopg2
import psycopg2.extras

DB_HOST = 'localhost'
DB_NAME = 'booksql'
DB_USER = 'postgres'
DB_PASS = '12345'

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cursor.execute("CREATE TABLE IF NOT EXISTS public.books( id serial NOT NULL, isbn varchar(100) NOT NULL, title varchar(100) NOT NULL, author varchar(100) NOT NULL, year varchar(100) NOT NULL, CONSTRAINT book_pkey PRIMARY KEY (id))")
conn.commit()

with open('books.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # Skip the header row.
    for row in reader:
        cursor.execute(
        "INSERT INTO books (isbn, title, author, year) VALUES ( %s, %s, %s, %s)",
        row
    )
conn.commit()

