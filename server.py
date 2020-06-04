from flask import Flask, request, render_template
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    print("Home Page")
    return render_template('home.html')


@app.route('/token', methods=['GET', 'POST'])
def verify_id_token():
    print("Begin Token Verification")
    token = request.values.get('id_token')
    CLIENT_ID = request.values.get('client_id')
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError("Wrong Issuer")

        userid = idinfo['sub']
        return userid
    except ValueError:
        #Invalid Token
        return "INVALID TOKEN"
