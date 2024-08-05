from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import logging
import sys
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicles.db'
db = SQLAlchemy(app)

# Basic auth credentials
USERNAME = config.USER
PASSWORD = config.PASSWORD

# Configure logging to stderr
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Database models
class VehicleAssignment(db.Model):
    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.String)
    created_at = db.Column(db.String)
    confirmation_number = db.Column(db.String)
    asset_number = db.Column(db.String)
    make = db.Column(db.String)
    model = db.Column(db.String)
    license_plate = db.Column(db.String)
    pickup_date_time = db.Column(db.String)
    return_date_time = db.Column(db.String)

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    message = {'message': "Authenticate."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/assignments', methods=['POST'])
@requires_auth
def webhook():
    if request.is_json:
        data = request.get_json()
        vehicle_data = data['data']
        
        new_vehicle = VehicleAssignment(
            id=data['id'],
            type=data['type'],
            created_at=data['createdAt'],
            confirmation_number=vehicle_data['confirmationNumber'],
            asset_number=vehicle_data['assetNumber'],
            make=vehicle_data['make'],
            model=vehicle_data['model'],
            license_plate=vehicle_data['licensePlate'],
            pickup_date_time=vehicle_data['pickupDateTime'],
            return_date_time=vehicle_data['returnDateTime']
        )
        
        db.session.add(new_vehicle)
        db.session.commit()
        
        return jsonify({"message": "Data received and saved"}), 200
    else:
        return jsonify({"message": "Request must be JSON"}), 400

@app.route('/assignments', methods=['GET'])
@requires_auth
def get_assignments():
    assignments = VehicleAssignment.query.all()
    result = [
        {
            "id": assignment.id,
            "type": assignment.type,
            "created_at": assignment.created_at,
            "confirmation_number": assignment.confirmation_number,
            "asset_number": assignment.asset_number,
            "make": assignment.make,
            "model": assignment.model,
            "license_plate": assignment.license_plate,
            "pickup_date_time": assignment.pickup_date_time,
            "return_date_time": assignment.return_date_time
        }
        for assignment in assignments
    ]
    return jsonify(result), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
