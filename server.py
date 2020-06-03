from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def print_id_token():
    output = request.values.get('idtoken')
    print("Token Transfer Successful")
    return str(output)


