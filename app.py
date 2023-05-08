from flask import Flask, render_template,jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    data = {
        'title': 'My Title',
        'description': 'This is a description'
    }
    return jsonify(data)
