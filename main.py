import re
import requests
from flask_api import status
from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'engo651'

DB_HOST = 'localhost'
DB_NAME = 'booksql'
DB_USER = 'postgres'
DB_PASS = '12345'

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

# # Check for environment variable
# if not os.getenv("postgresql://postgres:12345@localhost/booksql"):
#     raise RuntimeError("DATABASE_URL is not set")

# # Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# # Set up database
# engine = create_engine(os.getenv("postgresql://postgres:12345@localhost/booksql"))
# db = scoped_session(sessionmaker(bind=engine))

@app.route('/', methods=['GET', 'POST'])
def first():
    if 'loggedin' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
 
        if account:
            password_rs = account['password']
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('home'))
            else:
                flash('Incorrect username/password')
        else:
            flash('Incorrect username/password')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        hashed_password = generate_password_hash(password)
    
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s,%s,%s)", (username, hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        flash('Please fill out the form!')

    return render_template('register.html')

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST' and 'search' in request.form:
            search = request.form['search']
            cursor.execute('SELECT * FROM books WHERE LOWER(isbn) = LOWER(%s) OR LOWER(title) = LOWER(%s) OR LOWER(author) = LOWER(%s) OR LOWER(year) = LOWER(%s) ', (search, search, search, search,))
            books = cursor.fetchall()

        return render_template('search_result.html', books=books, search=search)
    else:
        return redirect(url_for('login'))

@app.route('/book/<book_isbn>', methods=['GET', 'POST'])
def book(book_isbn):
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
        isbn = str(book_isbn)
        cursor.execute('SELECT * FROM books WHERE isbn = %s', (isbn,))
        books = cursor.fetchone()

        cursor.execute('SELECT * FROM reviews WHERE isbn = %s', (isbn,))
        reviews = cursor.fetchall()

        cursor.execute('SELECT ROUND(AVG(rating),1) as rating FROM reviews WHERE isbn = %s', (isbn,))
        rating = cursor.fetchone()

        cursor.execute('SELECT COUNT(rating) FROM reviews WHERE isbn = %s', (isbn,))
        ratingCount = cursor.fetchone()
        print(ratingCount)

        return render_template('book.html', books=books, reviews=reviews, rating=rating, ratingCount=ratingCount)
    else:
        return redirect(url_for('login'))

@app.route('/review', methods=['GET', 'POST'])
def review():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST' and 'review' in request.form and 'isbn' in request.form:
            review = request.form['review']
            isbn = request.form['isbn']
            rating = request.form['rate']
            
            print(request.form)
            cursor.execute('SELECT username FROM users WHERE id = %s', [session['id']])
            username = cursor.fetchone()

            cursor.execute('SELECT * FROM reviews WHERE username = %s AND isbn = %s', (username[0], isbn))
            account = cursor.fetchone()

            if account:
                flash('You already submited your review for this book')
            else:
                cursor.execute("INSERT INTO reviews (username, review, isbn, rating) VALUES (%s,%s,%s,%s)", (username[0], review, isbn, rating))
                conn.commit()
                flash('Thanks for your review')

        return redirect(url_for('api', book_isbn = isbn))

    else:
        return redirect(url_for('login'))

@app.route('/api/<book_isbn>', methods=['GET', 'POST'])
def api(book_isbn):
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
        isbn = str(book_isbn)
        cursor.execute('SELECT * FROM books WHERE isbn = %s', (isbn,))
        book = cursor.fetchone()

        cursor.execute('SELECT * FROM reviews WHERE isbn = %s', (isbn,))
        reviews = cursor.fetchall()

        res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"})
        jsondata = res.json()

        if book:
            book_info = jsondata['items'][0]['volumeInfo']
            books = {
                        'title': book_info['title'], 
                        'author': book_info['authors'][0],
                        'ISBN_10': book_info['industryIdentifiers'][0]['identifier'],
                        'ISBN_13': book_info['industryIdentifiers'][1]['identifier'],
                        'average_rating': book_info['averageRating'] if book_info['averageRating'] else None,
                        'ratings_count': book_info['ratingsCount'] if book_info['ratingsCount'] else None,
                        'published_date': book_info['publishedDate'] if book_info['publishedDate'] else None
                    }

            return render_template('bookAPI.html', books=books, reviews=reviews, isbn=isbn)
        else:
            return render_template('404.html')
    else:
        return redirect(url_for('login'))

@app.route('/json', methods=['GET', 'POST'])
def json():
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
        isbn = request.form['isbn']
        cursor.execute('SELECT * FROM books WHERE isbn = %s', (isbn,))
        book = cursor.fetchone()

        res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"})
        jsondata = res.json()

        if book:
            book_info = jsondata['items'][0]['volumeInfo']
            

            return {"books" : [{
                        'title': book_info['title'], 
                        'author': book_info['authors'][0],
                        'ISBN_10': book_info['industryIdentifiers'][0]['identifier'],
                        'ISBN_13': book_info['industryIdentifiers'][1]['identifier'],
                        'average_rating': book_info['averageRating'] if book_info['averageRating'] else None,
                        'ratings_count': book_info['ratingsCount'] if book_info['ratingsCount'] else None,
                        'published_date': book_info['publishedDate'] if book_info['publishedDate'] else None
                    }]}
        else:
            return render_template('404.html')
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
