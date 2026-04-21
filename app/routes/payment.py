from flask import Blueprint, request, jsonify, current_app, session
import razorpay
import hmac
import hashlib
from app import mongo, socketio
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

class PaymentService:
    @staticmethod
    def get_client():
        return razorpay.Client(auth=(
            current_app.config['RAZORPAY_KEY_ID'], 
            current_app.config['RAZORPAY_KEY_SECRET']
        ))

    @staticmethod
    def create_order(amount_in_inr, notes=None):
        client = PaymentService.get_client()
        data = {
            'amount': int(amount_in_inr) * 100,
            'currency': 'INR',
            'payment_capture': '1',
            'notes': notes or {}
        }
        return client.order.create(data=data)

    @staticmethod
    def verify_signature(params_dict):
        client = PaymentService.get_client()
        return client.utility.verify_payment_signature(params_dict)

@payment_bp.route('/api/payment/create-order', methods=['POST'])
def create_order():
    try:
        data = request.json
        amount = data.get('amount')
        
        if not amount or int(amount) <= 0:
            return jsonify({"status": "error", "message": "Invalid amount"}), 400
            
        order = PaymentService.create_order(amount, notes={"donor_id": session.get('user_id', 'anonymous')})
        return jsonify(order), 200
    except Exception as e:
        current_app.logger.error(f"Razorpay Order Error: {e}")
        return jsonify({"status": "error", "message": "Could not initialize payment gateway"}), 500

@payment_bp.route('/api/payment/verify', methods=['POST'])
def verify_payment():
    try:
        data = request.json
        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing verification parameters"}), 400

        PaymentService.verify_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        # Elite Impact Recording
        donation_record = {
            "order_id": data['razorpay_order_id'],
            "payment_id": data['razorpay_payment_id'],
            "amount": float(data.get('amount', 0)),
            "donor_email": data.get('email'),
            "donor_id": session.get('user_id', 'GUEST'),
            "timestamp": datetime.utcnow(),
            "status": "Success",
            "impact_score": int(data.get('amount', 0)) // 100
        }
        
        mongo.db.donations.insert_one(donation_record)
        
        # Live Pulse Notification
        socketio.emit('donation_pulse', {
            "donor": data.get('email').split('@')[0],
            "amount": data.get('amount'),
            "impact": donation_record['impact_score']
        }, broadcast=True)
        
        return jsonify({"status": "success", "message": "Impact recorded successfully"}), 200
        
    except razorpay.errors.SignatureVerificationError:
        return jsonify({"status": "error", "message": "Security verify failed"}), 400
    except Exception as e:
        current_app.logger.error(f"Payment Verification Error: {e}")
        return jsonify({"status": "error", "message": "Critical system error during verification"}), 500
