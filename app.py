from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)
load_dotenv()

# Get the MongoDB URI from the environment variable
mongo_uri = os.getenv('MONGO_URI')
# MongoDB setup
client = MongoClient(mongo_uri)
db = client.HotelWebsite
users_collection = db.users


DISPLAY_NAME = "BCC Rentals"

def send_email(email, subject, body, is_html=False):
    admin_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Replace with a secure app-specific password

    msg = MIMEMultipart()
    msg['From'] = admin_email
    msg['To'] = email
    msg['Subject'] = subject

    if is_html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(admin_email, sender_password)
        server.sendmail(admin_email, email, msg.as_string())
        print(f"Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return False
    finally:
        server.quit()


@app.route('/send_email_to_user', methods=['POST'])
def send_email_to_user():
    try:
        data = request.json
        email = data.get('email', '')
        booking_id = data.get('booking_id', '')

        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not booking_id:
            return jsonify({"error": "Booking ID is required"}), 400

        body = (
            f"Dear User,<br><br>"
            f"We have received your booking request successfully. Your request has been sent to the admin for approval.<br><br>"
            f"<strong>Booking ID:</strong> {booking_id}<br><br>"
            f"We will get back to you once your request is approved.<br><br>"
            f"You can also check the status of your booking in "
            f"<a href='https://bcc-facility-rental.vercel.app/dashboard'>My Dashboard</a>.<br><br>"
            f"Best regards,<br>"
            f"The BCC Rentals Team"
        )
        subject = "Your Booking Request Has Been Received"
        email_sent = send_email(email, subject, body, is_html=True)

        if email_sent:
            return jsonify({"success": "Email sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send email"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def send_email_to_admin(email, booking_id):
    """
    Sends an email to the admin for approval of a booking request.
    """
    admin_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Replace with a secure app-specific password
    subject = "New Event Request From BCC Rentals"

    # Updated body to include the link and booking ID
    body = (
        f"Dear Admin,\n\n"
        f"You have received a new request from the website.\n\n"
        f"Booking ID: {booking_id}\n\n"
        f"Booking made with this email: {email}\n\n"
        f"Please visit the following link to approve or reject the request:\n"
        f"https://bcc-facility-rental.vercel.app/admin\n\n"
        f"Best regards,\n"
        f"The BCC Rentals Team"
    )

    # Email setup
    msg = MIMEMultipart()
    msg['From'] = f'{DISPLAY_NAME} <{admin_email}>'
    msg['To'] = "connect@chesschamps.us"  # This should always go to the admin's email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Send email via Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(admin_email, sender_password)
        server.sendmail(admin_email, "connect@chesschamps.us", msg.as_string())
        print(f"Email sent successfully to admin about booking ID {booking_id}")
        return True
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return False
    finally:
        server.quit()


@app.route('/send_email_to_admin_to_approve', methods=['POST'])
def send_email_to_admin_to_approve():
    try:
        # Parse the incoming JSON data
        data = request.json
        email = data.get('email', '').strip()
        booking_id = data.get('booking_id', '').strip()

        # Validate input
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not booking_id:
            return jsonify({"error": "Booking ID is required"}), 400

        # Call the function to send an email to the admin
        email_sent = send_email_to_admin(email, booking_id)

        if email_sent:
            return jsonify({"success": "Email sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send email"}), 500

    except Exception as e:
        print(f"Error in /send_email_to_admin_to_approve: {e}")
        return jsonify({"error": str(e)}), 400

 
def send_email_to_user_after_approval(email, booking_id, stripe=None):
 
    admin_email = "connect@chesschamps.us"
    sender_password = "iyln tkpp vlpo sjep"  # Replace with a secure app-specific password
    subject = "Your Booking Request Has Been Approved"

    body = (
        f"Dear User,\n\n"
        f"Your booking request has been approved successfully. We are excited to confirm your booking.\n\n"
        f"Booking ID: {booking_id}\n\n"
        f"Thank you for your patience. You can now proceed with your booking.\n\n"
    )

    # If stripe field is provided, add the payment information to the email
    if stripe:
        body += f"\n\nYou can make your payment using the following link: {stripe}\n"
    body += (
        f"\nBest regards,\n"
        f"The BCC Rentals Team"
    )
    # Email setup
    msg = MIMEMultipart()
    msg['From'] = f'{DISPLAY_NAME} <{admin_email}>'
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Send email via Gmail's SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(admin_email, sender_password)
        text = msg.as_string()
        server.sendmail(admin_email, email, text)
        print(f"Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
        return False
    finally:
        server.quit()

@app.route('/send_email_to_user_request_got_approved', methods=['POST'])
def send_email_to_user_request_got_approved_route():
   
    try:
        # Parse the incoming JSON data
        data = request.json
        email = data.get('email', '')
        booking_id = data.get('booking_id', '')
        stripe = data.get('stripe', '') # Stripe field (optional)

        # Validate input
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not booking_id:
            return jsonify({"error": "Booking ID is required"}), 400

        # Call the function to send an email to the user
        email_sent = send_email_to_user_after_approval(email, booking_id, stripe)

        if email_sent:
            return jsonify({"success": "Email sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send email"}), 500

    except Exception as e:
        print(f"Error in /send_email_to_user_request_got_approved: {e}")
        return jsonify({"error": str(e)}), 400

 
@app.route('/send_email_to_user_request_got_rejected', methods=['POST'])
def send_email_to_user_request_got_rejected_route():
   
    try:
        # Parse the incoming JSON data
        data = request.json
        email = data.get('email', '')
        booking_id = data.get('booking_id', '')
        note = data.get('note', '') 

        # Validate input
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not booking_id:
            return jsonify({"error": "Booking ID is required"}), 400

        # Call the function to send an email to the user
        email_sent = send_email_to_user_after_approval(email, booking_id, note)

        if email_sent:
            return jsonify({"success": "Email sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send email"}), 500

    except Exception as e:
        print(f"Error in /send_email_to_user_request_got_rejected: {e}")
        return jsonify({"error": str(e)}), 400



def generate_booking_id():
    while True:
        booking_id = str(random.randint(100000, 999999))  # Generate a 6-digit random number
        # Check if the booking ID already exists in the database
        if not users_collection.find_one({"booked_details.booking_id": booking_id}):
            return booking_id
@app.route('/')
def home():
    return "Hello, Flask on Vercel! "
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    entered_password = data.get('password')  # Correctly get the password

    # Basic validation
    if not email or not entered_password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find user by email
    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Check if the entered password matches the stored password
    if user["password"] != entered_password:
        return jsonify({"error": "Invalid email or password"}), 401

    # Successful login
    return jsonify({
        "message": "Login successful",
        "user_details": {
            "email": user['email'],
            "full_name": user.get('full_name', ''),
            "phone": user.get('phone', '')
        }
    }), 200

@app.route('/booking-details_wrt_email', methods=['GET'])
def get_booking_details_wrt_email():
    email = request.args.get('email')  # Get email from query parameters

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Find user by email
    user = users_collection.find_one({"email": email})

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get booking details
    booked_details = user.get("booked_details", [])

    return jsonify({
        "message": "Booking details retrieved successfully",
        "booked_details": booked_details
    }), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Get JSON data from the request
    email = data.get('email')
    full_name = data.get('full_name')
    phone = data.get('phone')
    password=data.get('password')

    # Check if email already exists
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Insert new user
    user = {
        "email": email,
        "password": password,
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

    # Generate a unique booking ID
    booking_id = generate_booking_id()  # Assumes the generate_booking_id() function exists

    # Add the booking ID to the booked_details
    booked_details['booking_id'] = booking_id

    # Check if user exists in the database
    user = users_collection.find_one({"email": email})

    if user:
        # Append the new checkout details to the user's booked_details
        users_collection.update_one(
            {"email": email},
            {"$push": {"booked_details": booked_details}}
        )
        return jsonify({
            "message": "Checkout details appended successfully",
            "booking_id": booking_id
        }), 200
    else:
        # Create a new record for the user
        checkout_data = {
            "email": email,
            "booked_details": [booked_details]  # Store in a list
        }
        users_collection.insert_one(checkout_data)
        return jsonify({
            "message": "Checkout details saved successfully",
            "booking_id": booking_id
        }), 201


@app.route('/get-booking-details', methods=['POST'])
def get_booking_details():
    data = request.json
    booking_id = data.get('booking_id')  # Get booking_id from the request

    # Basic validation
    if not booking_id:
        return jsonify({"error": "Booking ID is required"}), 400

    # Search for the booking details in the database
    user = users_collection.find_one({"booked_details.booking_id": booking_id})

    if user:
        # Find the specific booking details
        booked_details = next(
            (booking for booking in user['booked_details'] if booking['booking_id'] == booking_id),
            None
        )

        if booked_details:
            return jsonify({
                "email": user['email'],
                "name": user['full_name'],
                "phone": user['phone'],
                "booking_details": booked_details
            }), 200
        else:
            return jsonify({"error": "Booking not found"}), 404
    else:
        return jsonify({"error": "Booking ID does not exist"}), 404

@app.route('/update-booking-status', methods=['POST'])
def update_booking_status():
    data = request.json
    email = data.get('email')  # Get email from the request
    booking_id = data.get('booking_id')  # Get booking_id from the request
    paid = data.get('paid')  # Get 'paid' status from the request
    approved = data.get('approved')  # Get 'approved' status from the request
    reject = data.get('reject',False)
    # Basic validation
    if not email or not booking_id:
        return jsonify({"error": "Email and Booking ID are required"}), 400

   
    # Search for the user by email and booking_id
    user = users_collection.find_one({"email": email, "booked_details.booking_id": booking_id})

    if user:
        # Find the specific booking details
        booked_details = next(
            (booking for booking in user['booked_details'] if booking['booking_id'] == booking_id),
            None
        )

        if booked_details:
            # Update the 'paid' and 'approved' fields
            booked_details['paid'] = paid
            booked_details['approved'] = approved
            booked_details['reject'] = reject

            # Save the updated user document back to the database
            users_collection.update_one(
                {"_id": user["_id"], "booked_details.booking_id": booking_id},
                {"$set": {"booked_details.$.paid": paid, "booked_details.$.approved": approved, "booked_details.$.reject": reject}}
            )

            return jsonify({"message": "Booking status updated successfully"}), 200
        else:
            return jsonify({"error": "Booking not found"}), 404
    else:
        return jsonify({"error": "User or booking not found"}), 404

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

    # Filter out the user with email "admin@gmail.com"
    users_list = [user for user in users_list if user.get('email') != "admin@gmail.com"]

    return jsonify(users_list), 200

@app.route('/users/already_booked_dates', methods=['GET'])
def already_booked_dates():
    # Get the roomType from the request args
    room_type = request.args.get('room_type')  # Extract the roomType query parameter
    
    if not room_type:
        return jsonify({"error": "roomType is required"}), 400

    # Fetch all users from the database and filter based on room_type
    users = users_collection.find({"booked_details.room_type": room_type}, {"_id": 0, "booked_details.booked_dates": 1, "booked_details.room_type": 1})  # Fetch only relevant fields

    # Prepare a response containing the booked dates
    result = []
    for user in users:
        # Initialize a list to hold all booked dates for the specific room type
        booked_dates = []

        # Extract booked dates from booked_details
        for booked_detail in user.get("booked_details", []):
            if booked_detail.get("room_type") == room_type:  # Check if the room type matches
                for booked_date in booked_detail.get("booked_dates", []):
                    # Append only date, startTime, and endTime to the result
                    booked_dates.append({
                        "date": booked_date["date"],
                        "startTime": booked_date["startTime"],
                        "endTime": booked_date["endTime"]
                    })

        # Add the user's booked dates to the result only if there's a match for the room_type
        if booked_dates:
            result.append({"booked_dates": booked_dates})
 
    return jsonify(result), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)