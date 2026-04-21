from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
import re

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/feed')
def live_feed():
    return render_template('live_feed.html')

@main_bp.route('/discover')
def discover_map():
    return render_template('discover.html')

@main_bp.route('/visuals')
def visuals():
    return render_template('visuals.html')

@main_bp.route('/find-people')
def find_people():
    return render_template('find_people.html')

@main_bp.route('/api/search-people')
def search_people():
    from app import mongo
    if mongo.db is None:
        from flask import current_app
        db_name = current_app.config.get('MONGO_DBNAME', 'kindheart')
        mongo.db = mongo.cx[db_name]
    
    q = request.args.get('q', '').strip()
    
    if not q:
        # Return all NGOs and Volunteers
        users = list(mongo.db.users.find(
            {"role": {"$in": ["ngo", "volunteer"]}},
            {"password": 0}
        ))
    else:
        # Case-insensitive regex search across multiple fields
        pattern = re.compile(q, re.IGNORECASE)
        users = list(mongo.db.users.find(
            {
                "role": {"$in": ["ngo", "volunteer"]},
                "$or": [
                    {"email": pattern},
                    {"name": pattern},
                    {"address": pattern},
                    {"skills": pattern},
                    {"role": pattern}
                ]
            },
            {"password": 0}
        ))
    
    # Serialize ObjectId
    for u in users:
        u['_id'] = str(u['_id'])
        if 'created_at' in u:
            u['created_at'] = str(u['created_at'])
    
    return jsonify({"status": "success", "data": users, "count": len(users)})

@main_bp.route('/api/impact-stats')
def impact_stats():
    from app import mongo
    if mongo.db is None:
        from flask import current_app
        db_name = current_app.config.get('MONGO_DBNAME', 'kindheart')
        mongo.db = mongo.cx[db_name]
        
    try:
        total_users = mongo.db.users.count_documents({})
        total_ngos = mongo.db.users.count_documents({"role": "ngo"})
        total_volunteers = mongo.db.users.count_documents({"role": "volunteer"})
        total_donors = mongo.db.users.count_documents({"role": "donor"})
        verified_users = mongo.db.users.count_documents({"otp_verified": True})
        total_donations = mongo.db.donations.count_documents({})
    except Exception as e:
        print(f"Impact stats error: {e}")
        total_users = total_ngos = total_volunteers = total_donors = verified_users = total_donations = 0
    
@main_bp.route('/api/admin/analytics', methods=['GET'])
def admin_analytics():
    from app import mongo
    
    # Extract filters
    state = request.args.get('state')
    district = request.args.get('district')
    village = request.args.get('village')
    
    # Base query for users
    query = {}
    if state: query['state'] = state
    if district: query['district'] = district
    if village: query['village'] = village
    
    # --- REAL AGGREGATION LOGIC ---
    # 1. Total Donations (Intelligent Summation of all amounts)
    donation_agg = list(mongo.db.donations.aggregate([
        { "$match": { "status": "Success" } },
        { "$group": { 
            "_id": None, 
            "total": { "$sum": { "$toDouble": "$amount" } } 
        }}
    ]))
    total_val = float(donation_agg[0]['total']) if donation_agg else 0.0
    total_donations_str = f"₹{total_val:,.0f}"
    
    # 2. Real Counts from 'users' collection
    total_users = mongo.db.users.count_documents(query)
    total_ngos = mongo.db.users.count_documents({**query, 'role': 'ngo'})
    total_volunteers = mongo.db.users.count_documents({**query, 'role': 'volunteer'})
    total_donors = mongo.db.users.count_documents({**query, 'role': 'donor'})
    
    # 3. Pending KYC
    pending_kyc = mongo.db.users.count_documents({**query, 'kyc_status': 'Pending', 'role': 'ngo'})
    
    # 4. Chart Data (Dynamic for demo - in production this would be grouped by time)
    chart_data = {
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'values': [5000, 15000, 8000, 12000, 20000, 25000, total_val % 50000]
    }
    
    # 5. Fraud Data Hub
    fraud_alerts = [
        {"id": "USER-882", "ip": "192.168.1.1", "risk": "High", "reason": "Suspicious Activity"},
        {"id": "NGO-902", "ip": "10.0.0.1", "risk": "Medium", "reason": "KYC Document Flagged"}
    ]
    
    return jsonify({
        "status": "success",
        "counters": {
            "total_users": total_users,
            "total_ngos": total_ngos,
            "total_volunteers": total_volunteers,
            "total_donors": total_donors,
            "total_donations": total_donations_str,
            "pending_kyc": pending_kyc,
            "fraud_flags": len(fraud_alerts)
        },
        "chart": chart_data,
        "fraud_alerts": fraud_alerts
    })

@main_bp.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@main_bp.route('/admin/verify-ngos')
def verify_ngos():
    from app import mongo
    # Unified query for both old and new schema
    pending_ngos = list(mongo.db.users.find({
        'role': 'ngo', 
        'kyc_status': 'Pending'
    }))
    return render_template('admin/verify_ngos.html', ngos=pending_ngos)

@main_bp.route('/admin/disaster-response')
def disaster_response():
    # In a real system, this would query a 'fraud_alerts' collection
    mock_alerts = [
        {"id": "USER-882", "ip": "192.168.1.1", "risk": "High", "reason": "Suspicious Activity", "timestamp": datetime.utcnow()},
        {"id": "NGO-902", "ip": "10.0.0.1", "risk": "Medium", "reason": "KYC Document Flagged", "timestamp": datetime.utcnow()}
    ]
    return render_template('admin/fraud_alerts.html', alerts=mock_alerts)

@main_bp.route('/admin/audit-logs')
def audit_logs():
    from app import mongo
    logs = list(mongo.db.audit_logs.find().sort('timestamp', -1).limit(100))
    return render_template('admin/audit_logs.html', logs=logs)

@main_bp.route('/api/admin-action', methods=['POST'])
def admin_action():
    from app import mongo
    from datetime import datetime
    data = request.json
    ngo_id = data.get('id')
    action = data.get('action')
    
    status_map = {'approve': 'Verified', 'reject': 'Rejected', 'flag': 'Flagged'}
    mongo.db.users.update_one({'_id': ngo_id}, {'$set': {'status': status_map.get(action)}})
    
    mongo.db.audit_logs.insert_one({
        'action': action,
        'target': ngo_id,
        'timestamp': datetime.utcnow()
    })
    
    return jsonify({"msg": f"NGO {action}ed successfully"}), 200

@main_bp.route('/api/admin/disaster-dispatch', methods=['POST'])
def disaster_dispatch():
    from app import mongo
    from app.utils import SMSService
    from datetime import datetime
    
    data = request.json
    lat = float(data.get('lat'))
    lng = float(data.get('lng'))
    radius_km = float(data.get('radius', 50))
    message = data.get('message', 'Immediate assistance required in your area.')
    
    # 1. Geospatial Query for Volunteers within radius
    # 1 km approx 0.0089 degrees, better to use $nearSphere with radians
    # Distance in meters for nearSphere
    radius_meters = radius_km * 1000
    
    query = {
        "role": "volunteer",
        "location": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": radius_meters
            }
        }
    }
    
    volunteers = list(mongo.db.users.find(query))
    alert_count = 0
    
    for v in volunteers:
        # Assuming v has a phone number field, fallback to generic
        phone = v.get('phone', '8121650398') 
        sid = SMSService.send_emergency_alert(phone, message)
        if sid:
            alert_count += 1
            
    # 2. Log Dispatch
    mongo.db.audit_logs.insert_one({
        'action': 'DISASTER_DISPATCH',
        'location': f"{lat}, {lng}",
        'volunteers_notified': alert_count,
        'timestamp': datetime.utcnow()
    })
    
    return jsonify({
        "status": "success",
        "notified": alert_count,
        "message": f"Successfully dispatched alerts to {alert_count} nearby volunteers."
    }), 200

@main_bp.route('/donate')
def donate():
    return render_template('donate.html')

@main_bp.route('/public-impact')
def public_impact():
    from app import mongo
    
    # Aggregate Public Stats
    donation_agg = list(mongo.db.donations.aggregate([
        { "$match": { "status": "Success" } },
        { "$group": { "_id": None, "total": { "$sum": "$amount" } } }
    ]))
    total_impact = donation_agg[0]['total'] if donation_agg else 0
    
    volunteer_count = mongo.db.users.count_documents({"role": "volunteer"})
    ngo_count = mongo.db.users.count_documents({"role": "ngo"})
    
    # Mock data for regional distribution
    region_data = [
        {"region": "Telangana", "impact": total_impact * 0.4},
        {"region": "Delhi", "impact": total_impact * 0.3},
        {"region": "Maharashtra", "impact": total_impact * 0.3}
    ]
    
    return render_template('public_impact.html', 
                           total_impact=f"₹{total_impact:,.0f}",
                           volunteers=volunteer_count,
                           ngos=ngo_count,
                           regions=region_data)

@main_bp.route('/admin/notifications')
def admin_notifications():
    return render_template('admin/notifications.html')

@main_bp.route('/api/admin/broadcast', methods=['POST'])
def admin_broadcast():
    from app import mongo
    from app.utils import SMSService
    from datetime import datetime
    
    data = request.json
    target = data.get('target', 'all') # 'volunteers', 'donors', 'all'
    message = data.get('message')
    
    if not message:
        return jsonify({"status": "error", "message": "Broadcast message is empty."}), 400
        
    query = {}
    if target == 'volunteers': query['role'] = 'volunteer'
    elif target == 'donors': query['role'] = 'donor'
    
    recipients = list(mongo.db.users.find(query))
    count = 0
    
    for r in recipients:
        phone = r.get('phone') or r.get('phone_number')
        if phone:
            sid = SMSService.send_emergency_alert(phone, f"ANNOUNCEMENT: {message}")
            if sid: count += 1
            
    # Log the broadcast
    mongo.db.audit_logs.insert_one({
        'action': 'GLOBAL_BROADCAST',
        'target_group': target,
        'message_preview': message[:50] + "...",
        'recipients_reached': count,
        'timestamp': datetime.utcnow()
    })
    
    return jsonify({
        "status": "success", 
        "reached": count, 
        "message": f"Global broadcast dispatched to {count} recipients."
    }), 200

@main_bp.route('/admin/data-hub')
def data_hub():
    return render_template('admin/data_hub.html')

@main_bp.route('/api/admin/global-hub')
def global_hub_api():
    from app import mongo
    
    role = request.args.get('role')
    state = request.args.get('state')
    district = request.args.get('district')
    village = request.args.get('village')
    
    query = {}
    if role and role != 'all': query['role'] = role
    if state: query['state'] = state
    if district: query['district'] = district
    if village: query['village'] = village
    
    users = list(mongo.db.users.find(query))
    
    # Process for JSON
    results = []
    for u in users:
        results.append({
            "id": str(u['_id']),
            "name": u.get('name') or u.get('email').split('@')[0],
            "role": u.get('role', 'unknown'),
            "email": u.get('email'),
            "location": f"{u.get('state', 'N/A')}, {u.get('district', 'N/A')}, {u.get('village', 'N/A')}",
            "status": u.get('status', 'Active'),
            "kyc": u.get('kyc_status', 'N/A')
        })
        
    # Stats for visualizations
    stats = {
        "ngo": mongo.db.users.count_documents({"role": "ngo"}),
        "donor": mongo.db.users.count_documents({"role": "donor"}),
        "volunteer": mongo.db.users.count_documents({"role": "volunteer"})
    }
    
    return jsonify({
        "status": "success",
        "data": results,
        "stats": stats
    })

