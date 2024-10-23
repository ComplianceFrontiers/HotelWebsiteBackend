from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os

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

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Get JSON data from the request
    email = data.get('email')
    full_name = data.get('full_name')
    phone = data.get('phone')

    # Check if email already exists
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Insert new user
    user = {
        "email": email,
        "full_name": full_name,
        "phone": phone
    }
    users_collection.insert_one(user)

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')

    # Basic validation
    if not email:
        return jsonify({"error": "Email and password are required"}), 400

    # Find user by email
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "Login successful", "user": {"email": user['email'], "full_name": user['full_name'],'phone':user['phone']}}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)