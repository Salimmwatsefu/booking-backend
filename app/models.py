from . import db

class TransportInside(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.String(50), nullable=False)
    route = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    scooter_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<TransportInside {self.id}>'

class TransportOutside(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(200), nullable=False)  # Different field for outside transport
    date = db.Column(db.String(50), nullable=False)
    bus_seat_count = db.Column(db.Integer, default=20, nullable=False)  # Default set to 20 seats
    booked_seats = db.Column(db.Integer, default=0, nullable=False)  # Track booked seats

    def __repr__(self):
        return f'<TransportOutside {self.id}>'

class VenueBooking(db.Model):
    __tablename__ = 'venue_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  
    school_id = db.Column(db.String(20), nullable=False) 
    reason = db.Column(db.Text, nullable=False) 
    selected_venue = db.Column(db.String(100), nullable=False)  
    sub_venue = db.Column(db.String(100), nullable=True) 
    date = db.Column(db.Date, nullable=False)  
    time = db.Column(db.Time, nullable=False) 

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "school_id": self.school_id,
            "reason": self.reason,
            "selected_venue": self.selected_venue,
            "sub_venue": self.sub_venue,
            "date": self.date.isoformat(),
            "time": self.time.isoformat(),
        }


class SportsPitchBooking(db.Model):
    __tablename__ = 'sports_pitch_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    pitch_name = db.Column(db.String(255), nullable=False)
    slot = db.Column(db.String(50), nullable=False)  # e.g., '9:00 AM - 10:00 AM'
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    school_id = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(255), nullable=False)

    def __init__(self, pitch_name, slot, date, name, school_id, reason):
        self.pitch_name = pitch_name
        self.slot = slot
        self.date = date
        self.name = name
        self.school_id = school_id
        self.reason = reason

    def __repr__(self):
        return f'<SportsPitchBooking {self.pitch_name} at {self.date} {self.slot}>'

    # Method to return the booking details in a dictionary format
    def to_dict(self):
        return {
            'id': self.id,
            'pitch_name': self.pitch_name,
            'slot': self.slot,
            'date': self.date,
            'name': self.name,
            'school_id': self.school_id,
            'reason': self.reason,
        }


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(250), nullable=False)

    # The constructor should match the attributes in the model
    def __init__(self, category, department, date, time_slot, name, school_id, reason):
        self.category = category
        self.department = department
        self.date = date
        self.time_slot = time_slot
        self.name = name
        self.school_id = school_id
        self.reason = reason

    def __repr__(self):
        return f"<Appointment {self.id} for {self.name} at {self.time_slot}>"
