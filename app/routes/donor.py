from flask import Blueprint, request, jsonify, send_file, session
from app import mongo, socketio
import requests
import json
from app.utils import generate_donation_receipt
from datetime import datetime
import uuid

donor_bp = Blueprint('donor', __name__)

@donor_bp.route('/api/donate', methods=['POST'])
def handle_donation():
    data = request.form if request.form else request.json
    name = data.get('name')
    email = data.get('email')
    amount = data.get('amount', 0)
    item_type = data.get('item_type') # For physical donations
    
    donation_id = str(uuid.uuid4())[:8].upper()
    
    if item_type:
        # Handle Physical Pickup Request
        pickup_data = {
            "donation_id": donation_id,
            "donor_name": name,
            "donor_email": email,
            "donor_id": session.get('user_id', 'GUEST'),
            "item_type": item_type,
            "address": data.get('address'),
            "status": "Pending",
            "timestamp": datetime.now()
        }
        
        # FIX: Ensure mongo.db is not None
        if mongo.db is None:
            # Fallback for misconfigured environments
            from flask import current_app
            db_name = current_app.config.get('MONGO_DBNAME', 'kindheart')
            mongo.db = mongo.cx[db_name]

        mongo.db.pickup_requests.insert_one(pickup_data)
        
        # Shiprocket Mock Integration
        try:
            shiprocket_payload = {
                "order_id": donation_id,
                "pickup_location": "Primary Warehouse",
                "delivery_address": data.get('address'),
                "customer_name": name,
                "customer_email": email,
                "items": [{"name": item_type, "qty": 1}]
            }
            # Mocking the Shiprocket API call
            print(f"SHIPROCKET MOCK: Creating shipment for {donation_id}")
            # In production: requests.post("https://apiv2.shiprocket.in/v1/external/shipments/create", json=shiprocket_payload)
        except Exception as e:
            print(f"Shiprocket log: {e}")

        # Broadcast to Volunteers
        socketio.emit('new_pickup_request', {
            "id": donation_id,
            "item": item_type,
            "location": data.get('address')
        })
        
        return jsonify({"msg": "Pickup request scheduled & shipment initialized!", "id": donation_id}), 201
    
    else:
        # Handle Monetary Donation
        donation_data = {
            "donation_id": donation_id,
            "name": name,
            "email": email,
            "amount": amount,
            "timestamp": datetime.now(),
            "status": "Success"
        }
        mongo.db.donations.insert_one(donation_data)
        
        # Simulated live counter update
        socketio.emit('donation_update', {"amount": amount})
        
        # Generate receipt
        receipt_buffer = generate_donation_receipt(name, email, amount, donation_id)
        return send_file(receipt_buffer, as_attachment=True, download_name=f"UnitySync_Receipt_{donation_id}.pdf")

@donor_bp.route('/api/nearby-ngos', methods=['GET'])
def get_nearby_ngos():
    # Simulation of geospatial search
    # In production, use MongoDB $near with coordinates
    ngos = [
        {"name": "Bright Future NGO", "distance": "1.2km", "category": "Education"},
        {"name": "Green Earth Group", "distance": "2.5km", "category": "Environment"},
        {"name": "Help Hands Foundation", "distance": "3.8km", "category": "Healthcare"}
    ]
    return jsonify(ngos)
