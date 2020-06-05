from flask import Flask, request, render_template
from google.oauth2 import id_token
from google.auth.transport import requests
import sqlite3

app = Flask(__name__)
DB = './database.db'
CLIENT_ID = "443130310905-s9hq5vg9nbjctal1dlm2pf8ljb9vlbm3.apps.googleusercontent.com"


def open_db():
    """Opens a database connection for editing"""
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    return (conn, c)


def close_db(conn):
    """Closes the database connection"""
    conn.commit()
    conn.close()


def create_user_table():
    """Creates a 'users' table in our database IF ONE DOES NOT ALREADY EXIST"""
    conn, c = open_db()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id text, given_name text, family_name text, email text);''')
    close_db(conn)


def insert_user(user_id, given_name, family_name, email):
    """Inserts a user into the 'users' table of the database"""
    conn, c = open_db()
    c.execute('''INSERT INTO users VALUES (?,?,?,?);''', (user_id, given_name, family_name, email))
    close_db(conn)


def is_user_registered(user_id):
    """Determines if a given user id is already registered in our database"""
    conn, c = open_db()
    user = c.execute('''SELECT * FROM users WHERE user_id=?;''', (user_id,)).fetchone()
    close_db(conn)
    return user != None


@app.route('/button', methods=['GET', 'POST'])
def button_home_page():
    """Display the home page of the site that uses a traditional sign-in button"""
    print("Button Home Page")
    return render_template('button_home.html')


@app.route('/onetap', methods=['GET', 'POST'])
def onetap_home_page():
    """Display the home page of the site that uses OneTap sign-in"""
    print("OneTap Home Page")
    return render_template('onetap_home.html')


@app.route('/button-token', methods=['GET', 'POST'])
def handle_user():
    """Handle a user request by signing them in if they are an existing user or registering them otherwise"""
    print('Handling User Request')
    token = request.values.get('id_token')
    user_info = verify_id_token(token, CLIENT_ID)

    if user_info == "INVALID TOKEN":
        print(user_info)
        return render_template('invalid_id.html')

    create_user_table()
    registered = is_user_registered(user_info['sub'])
    if registered:
        return render_template('returning_user.html', name=user_info['given_name'])
    else:
        user_id = user_info['sub']
        given_name = user_info['given_name']
        family_name = user_info['family_name']
        email = user_info['email']
        insert_user(user_id, given_name, family_name, email) 
        return render_template('new_user.html', name=given_name)


@app.route('/onetap-token', methods=['GET', 'POST'])
def handle_onetap():
    """Handle signing in when Google sends the token to our server directly"""
    print('Handling User Request from OneTap')
    #Verify CSRF doubel submit cookie
    csrf_token_cookie = request.cookies.get('g_csrf_token')
    if not csrf_token_cookie:
        return "No CSRF token in Cookie"
    csrf_token_body = request.cookies.get('g_csrf_token')
    if not csrf_token_body:
        return "No CSRF token in post body"
    if csrf_token_body != csrf_token_cookie:
        return "Failed to verify double submit cookie"

    token = request.values.get('credential')
    user_info = verify_id_token(token, CLIENT_ID)

    if user_info == "INVALID TOKEN":
        print(user_info)
        return render_template('invalid_id.html')

    create_user_table()
    registered = is_user_registered(user_info['sub'])
    if registered:
        return render_template('returning_user.html', name=user_info['given_name'])
    else:
        user_id = user_info['sub']
        given_name = user_info['given_name']
        family_name = user_info['family_name']
        email = user_info['email']
        insert_user(user_id, given_name, family_name, email) 
        return render_template('new_user.html', name=given_name)


def verify_id_token(token, client_id):
    """Verify that a given id_token is valid and return the decoded user information if it is valid"""
    print("Begin Token Verification")
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError("Wrong Issuer")

        return idinfo

    except ValueError:
        return "INVALID TOKEN"


