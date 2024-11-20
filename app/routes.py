from flask import request, jsonify, Blueprint
from datetime import datetime, timedelta
from . import db
from .models import TransportInside, TransportOutside, VenueBooking, SportsPitchBooking, Appointment, User
import jwt

booking_blueprint = Blueprint('booking', __name__)

SECRET_KEY = "sj12345"  # Replace with a secure secret key

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),  # Token expiry time
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@booking_blueprint.route('/api/signup', methods=['POST'])
def sign_up():
    data = request.get_json()

    # Extract data
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    # Check for required fields
    if not all([email, phone, password]):
        return jsonify({"error": "All fields are required"}), 400

    # Check if the email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email is already registered"}), 400

    # Create and save the new user
    new_user = User(email=email, phone=phone, password=password)
    db.session.add(new_user)
    db.session.commit()

    # Generate a token for the new user
    token = create_token(new_user.id)

    return jsonify({
        "message": "Account created successfully",
        "user_id": new_user.id,
        "token": token
    }), 201


# Login Route
@booking_blueprint.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # Extract data
    email = data.get('email')
    password = data.get('password')

    # Validate inputs
    if not all([email, password]):
        return jsonify({"error": "Email and password are required"}), 400

    # Check if the user exists
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Generate a token for the user
    token = create_token(user.id)  # Assuming create_token generates a JWT

    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "token": token
    }), 200


# Routes for Transport Inside School
@booking_blueprint.route('/api/transport/inside', methods=['POST'])
def create_transport_inside_booking():
    data = request.json
    booking = TransportInside(
        name=data['name'],
        school_id=data['school_id'],
        route=data['route'],
        date=data['date'],
        time=data['time'],
        scooter_count=data['scooter_count']
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify({'id': booking.id}), 201

@booking_blueprint.route('/api/transport/inside', methods=['GET'])
def get_transport_inside_bookings():
    bookings = TransportInside.query.all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'school_id': b.school_id,
        'route': b.route,
        'date': b.date,
        'time': b.time,
        'scooter_count': b.scooter_count
    } for b in bookings]), 200

@booking_blueprint.route('/api/transport/inside/<int:booking_id>', methods=['DELETE'])
def delete_transport_inside_booking(booking_id):
    booking = TransportInside.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'message': 'Inside booking deleted'}), 200

@booking_blueprint.route('/api/transport/inside/availability', methods=['GET'])
def get_scooter_availability():
    # Replace `TOTAL_SCOOTERS` with the actual total number of scooters you have
    TOTAL_SCOOTERS = 20
    
    # Get the date from the query parameter
    date = request.args.get('date')

    # We will compare only the date part (remove time portion)
    if date:
        # Remove the time portion by splitting the string at the first space (assuming the format you are sending is valid)
        date = date.split('T')[0]  # This takes only the date part in format "MM/DD/YYYY"
    
    # Sum the number of scooters booked on the given date
    booked_count = db.session.query(
        db.func.sum(TransportInside.scooter_count)
    ).filter(db.func.date(TransportInside.date) == date).scalar() or 0  # Default to 0 if None

    # Calculate remaining scooters
    remaining_scooters = TOTAL_SCOOTERS - booked_count
    
    return jsonify({'remaining_scooters': remaining_scooters}), 200



# Routes for Transport Outside School
@booking_blueprint.route('/api/transport/outside', methods=['POST'])
def create_transport_outside_booking():
    data = request.json
    booked_seats = int(data.get('bookedSeats', 0))  # The number of seats being booked

    # Set the total bus seat count (you can modify this to be dynamic if needed)
    bus_seat_count = 30  

    # Check if there are enough seats available for the booking
    transport = TransportOutside.query.filter_by(date=data['date']).first()

    # If no booking exists for this date, create a new entry
    if transport:
        total_booked_seats = transport.booked_seats + booked_seats
        if total_booked_seats > bus_seat_count:
            return jsonify({'error': 'Not enough seats available'}), 400
        transport.booked_seats += booked_seats  # Update booked seats
    else:
        # If no transport entry for that date, create a new one
        transport = TransportOutside(
            name=data['name'],
            school_id=data['school_id'],
            destination=data['destination'],
            date=data['date'],
            bus_seat_count=bus_seat_count,  # Set seat count (fixed or dynamic)
            booked_seats=booked_seats,  # Set booked seats to the value received
        )
        db.session.add(transport)

    db.session.commit()  # Save the changes to the database
    return jsonify({'id': transport.id}), 201


@booking_blueprint.route('/api/transport/outside', methods=['GET'])
def get_transport_outside_bookings():
    bookings = TransportOutside.query.all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'school_id': b.school_id,
        'destination': b.destination,
        'date': b.date,
        'booked_seats': b.booked_seats,
        'bus_seat_count': b.bus_seat_count
    } for b in bookings]), 200

@booking_blueprint.route('/api/transport/outside/<int:booking_id>', methods=['DELETE'])
def delete_transport_outside_booking(booking_id):
    booking = TransportOutside.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'message': 'Outside booking deleted'}), 200

@booking_blueprint.route('/api/transport/outside/availability', methods=['GET'])
def get_available_seats():
    date = request.args.get('date')  

    # Total bus seat count
    bus_seat_count = 30

    # Find all bookings for the specified date
    transport = TransportOutside.query.filter_by(date=date).all()

    # Sum up the booked seats for the specified date
    total_booked_seats = sum(t.booked_seats for t in transport)

    # Calculate remaining seats
    remaining_seats = bus_seat_count - total_booked_seats
    return jsonify({'remaining_seats': remaining_seats}), 200




# Routes for Venue Bookings
@booking_blueprint.route('/api/venue_bookings', methods=['POST'])
def create_venue_booking():
    data = request.get_json()
    
    name = data.get('name')
    school_id = data.get('schoolID')
    reason = data.get('reason')
    selected_venue = data.get('selectedVenue')
    sub_venue = data.get('subVenue')
    date_str = data.get('date')
    time_str = data.get('time')
    
    # Check for required fields
    if not all([name, school_id, reason, selected_venue, date_str, time_str]):
        return jsonify({"error": "All required fields must be provided"}), 400
    
    # Parse date and time
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400
    
    new_booking = VenueBooking(
        name=name,
        school_id=school_id,
        reason=reason,
        selected_venue=selected_venue,
        sub_venue=sub_venue,
        date=date,
        time=time
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify(new_booking.to_dict()), 201

# Route to get all venue bookings
@booking_blueprint.route('/api/venue_bookings', methods=['GET'])
def get_venue_bookings():
    bookings = VenueBooking.query.all()
    return jsonify([booking.to_dict() for booking in bookings]), 200


#Sports Pitch booking


@booking_blueprint.route('/api/book_pitch', methods=['POST'])
def book_pitch():
    data = request.get_json()

    # Extract information from the request data
    pitch_name = data.get('pitch_name')
    slot = data.get('slot')
    date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()  # Assuming date in 'YYYY-MM-DD' format
    name = data.get('name')
    school_id = data.get('school_id')
    reason = data.get('reason')

    # Check if the selected slot for the specific date is already booked
    existing_booking = SportsPitchBooking.query.filter_by(pitch_name=pitch_name, slot=slot, date=date).first()
    if existing_booking:
        return jsonify({'message': 'This time slot is already booked!'}), 400

    # Create a new booking if the slot is available
    new_booking = SportsPitchBooking(
        pitch_name=pitch_name, 
        slot=slot, 
        date=date, 
        name=name, 
        school_id=school_id, 
        reason=reason
    )
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({'message': 'Booking successful!', 'booking': new_booking.to_dict()}), 201


@booking_blueprint.route('/api/available_slots/<pitch_name>/<date>', methods=['GET'])
def get_available_slots(pitch_name, date):
    # Convert date to datetime object to compare
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date()  
    except ValueError:
        return jsonify({'message': 'Invalid date format! Use YYYY-MM-DD.'}), 400

    # Define available slots (for example)
    available_slots = ['9:00 AM - 10:00 AM', '10:00 AM - 11:00 AM', '11:00 AM - 12:00 PM', '1:00 PM - 2:00 PM']

    # Get the booked slots for the specific pitch and date
    booked_slots = SportsPitchBooking.query.filter_by(pitch_name=pitch_name, date=date).all()

    # Get the slots that are already booked
    booked_times = [booking.slot for booking in booked_slots]

    # Filter out the booked slots from the available slots
    available_slots = [slot for slot in available_slots if slot not in booked_times]

    return jsonify({'available_slots': available_slots})


#Appointments route

@booking_blueprint.route('/api/book_appointment', methods=['POST'])
def book_appointment():
    data = request.get_json()

    # Extract information from the request data
    category = data.get('category')
    department = data.get('department')
    date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()  # Assuming date in 'YYYY-MM-DD' format
    time_slot = data.get('time_slot')
    name = data.get('name')
    school_id = data.get('school_id')
    reason = data.get('reason')

    # Check if the selected time slot for the specific date is already booked
    existing_booking = Appointment.query.filter_by(date=date, time_slot=time_slot).first()
    if existing_booking:
        return jsonify({'message': 'This time slot is already booked!'}), 400

    # Create a new appointment if the slot is available
    new_appointment = Appointment(
        category=category,
        department=department,
        date=date,
        time_slot=time_slot,
        name=name,
        school_id=school_id,
        reason=reason
    )
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'Booking successful!', 'appointment': new_appointment.id}), 201


# 2. Route to get available time slots for a specific date and department
@booking_blueprint.route('/api/available_appointments/<date>/<department>', methods=['GET'])
def get_available_appointments(date, department):
    try:
        date = datetime.strptime(date, '%Y-%m-%d').date() 
    except ValueError:
        return jsonify({'message': 'Invalid date format! Use YYYY-MM-DD.'}), 400

    # Example available slots (can be department-specific in the real world)
    available_slots = ['9:00 AM - 10:00 AM', '10:00 AM - 11:00 AM', '11:00 AM - 12:00 PM', '1:00 PM - 2:00 PM']

    # Get the booked slots for the specific date and department
    booked_slots = Appointment.query.filter_by(date=date, department=department).all()

    # Get the slots that are already booked
    booked_times = [booking.time_slot for booking in booked_slots]

    # Filter out the booked slots from the available slots
    available_slots = [slot for slot in available_slots if slot not in booked_times]

    return jsonify({'available_slots': available_slots})
