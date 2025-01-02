from datetime import datetime
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

    return jsonify({"message": "Login successful", "user_details": {"email": user['email'], "full_name": user['full_name'],'phone':user['phone']}}), 200

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

@app.route('/checkout', methods=['POST'])
def checkout():
    data = request.json
    email = data.get('email')  # Get email from the request
    booked_details = data.get('booked_details')  # Get checkout details

    # Basic validation
    if not email or not booked_details:
        return jsonify({"error": "Email and checkout details are required"}), 400

    # Check if user exists in the database
    user = users_collection.find_one({"email": email})

    if user:
        # If user exists, append the new checkout details
        if 'booked_details' not in user:
            user['booked_details'] = []  # Initialize if not present
        user['booked_details'].append(booked_details)
        # Update the user record in the database
        users_collection.update_one({"email": email}, {"$set": {"booked_details": user['booked_details']}})
        return jsonify({"message": "Checkout details appended successfully"}), 200
    else:
        # If user does not exist, create a new record
        checkout_data = {
            "email": email,
            "booked_details": [booked_details]  # Store in a list
        }
        users_collection.insert_one(checkout_data)
        return jsonify({"message": "Checkout details saved successfully"}), 201

@app.route('/checkout/filter', methods=['GET'])
def filter_booked_details():
    title = request.args.get('title', '').strip()  # Strip any whitespace/newlines
    check_in = request.args.get('checkIn', '').strip()  # Strip any whitespace/newlines

    if not title or not check_in:
        return jsonify({"error": "Title and check-in date are required"}), 400

    print(f"Searching for Title: {title}, Check-In Date: {check_in}")

    matching_bookings = []

    users = users_collection.find({}, {"email": 1, "booked_details": 1})  # Fetch only email and booked_details

    for user in users:
        for booking_list in user.get('booked_details', []):
            for booking in booking_list:
                print(f"Checking Booking: {booking}")  # Debugging line
                
                booking_check_in = booking.get('checkIn')
                if booking_check_in and isinstance(booking_check_in, str):
                    try:
                        booking_check_in_date = datetime.fromisoformat(booking_check_in)
                        request_check_in_date = datetime.fromisoformat(check_in)
                    except ValueError as e:
                        print(f"Invalid date format: {e}")  # Improved error logging
                        continue
                    
                    if booking.get('title') == title and booking_check_in_date == request_check_in_date:
                        matching_bookings.append({
                            "email": user['email'],
                            "booking": booking
                        })

    print(f"Matching Bookings: {matching_bookings}")  # Debugging line
    return jsonify(matching_bookings), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    # Fetch all users from the database, excluding the _id field
    users = users_collection.find({}, {"_id": 0})  # 0 to exclude _id

    # Convert MongoDB documents to a list of dictionaries
    users_list = [user for user in users]  # Convert each user document to a dictionary

    return jsonify(users_list), 200

@app.route('/users/already_booked_dates', methods=['GET'])
def already_booked_dates():
    # Fetch all users from the database and extract booked_dates
    users = users_collection.find({}, {"_id": 0, "booked_details.booked_dates": 1})  # Fetch only booked_dates fields

    # Prepare a response containing the booked dates
    result = []
    for user in users:
        # Initialize a list to hold all booked dates
        booked_dates = []
        
        # Extract booked dates from booked_details
        for booked_detail in user.get("booked_details", []):
            for booked_date in booked_detail.get("booked_dates", []):
                # Append only date, startTime, and endTime to the result
                booked_dates.append({
                    "date": booked_date["date"],
                    "startTime": booked_date["startTime"],
                    "endTime": booked_date["endTime"]
                })
        
        # Add the user's booked dates to the result
        if booked_dates:
            result.append({"booked_dates": booked_dates})

    return jsonify(result), 200

if __name__ == '__main__':
    app.run()