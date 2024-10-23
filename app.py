from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pytz

app = Flask(__name__)
CORS(app)
load_dotenv()

# Get the MongoDB URI from the environment variable
mongo_uri = os.getenv('MONGO_URI')
# MongoDB setup
client = MongoClient(mongo_uri)
db = client.HotelWebsite
users_collection = db.users

@app.route('/')
def home():
    return "Hello, Flask on Vercel! "


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)