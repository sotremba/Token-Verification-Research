from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def print_id_token():
    output = request.cookies.get('g_csrf_token')
    print("Token Transfer Successful")
    return str(output)


