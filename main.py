import os
import re
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/search_result', methods=['GET', 'POST'])
def search_result():
    return render_template('search_result.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    return render_template('book.html')

if __name__ == "__main__":
    app.run(debug=True)
