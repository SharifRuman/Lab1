# Project 1 and 2 

**NOTICE:** I'm using same repo to publish LAb 1 and Lab 2 project.

### ENGO 651 - Adv. Topics on Geospatial Technologies


For this Lab 1 project I built a flask web application to search book and find details about books from postgres database.

And for Lab 2 flask web application will search book and find details about books from Google book API.


##### Python Requirments: 
1. Flask
2. psycopg2
3. werkzeug
4. requests
5. flask_api

##### Tables:

Users | Books | Reviews
| :--- | ---: | :---:
id  | isbn | id
username  | title | username
email  | author | review
password  | year | isbn
 | | rating

##### Files:
 1. static
    1. search.css
    2. style.css
    3. bootstrap.min.css
    4. bootstrap.bundle.min.js
    5. books.jpg
2. templates
    1. book.html
    2. home.html
    3. index.html
    4. register.html
    5. search_result.html
    6. 404.html
    7. bookAPI.html
3. main.py
4. import.py
5. book.csv
6. requirements.txt

##### Framework

[Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/)

##### API

[GOOGLE BOOK API](https://developers.google.com/books/)