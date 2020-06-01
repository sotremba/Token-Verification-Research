from flask import Flask
app = Flask(__name__)

@app.route('/')
def print_id_token():
    print("Hello World")
    return "output"


