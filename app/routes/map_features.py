from flask import Blueprint, jsonify, current_app
from app import mongo
import googlemaps

map_bp = Blueprint('map', __name__)

@map_bp.route('/api/map-data')
def get_map_data():
    try:
        users = mongo.db.users.find({"role": {"$in": ["ngo", "volunteer"]}})
        
        gmaps = googlemaps.Client(key=current_app.config.get('GOOGLE_MAPS_API_KEY'))
        
        map_points = []
        for user in users:
            lat, lng = None, None
            
            # If coordinates are already saved
            if 'lat' in user and 'lng' in user:
                lat, lng = user['lat'], user['lng']
            elif 'address' in user:
                # Use Google Maps Python SDK to geocode newly registered string addresses!
                try:
                    geocode_result = gmaps.geocode(user['address'])
                    if geocode_result:
                        lat = geocode_result[0]['geometry']['location']['lat']
                        lng = geocode_result[0]['geometry']['location']['lng']
                        # Cache it back into the DB to save API calls
                        mongo.db.users.update_one({'_id': user['_id']}, {'$set': {'lat': lat, 'lng': lng}})
                except Exception as e:
                    print(f"Geocoding failed for {user['address']}: {e}")
            
            # Default fallbacks if no address/coord provided during registration
            if not lat or not lng:
                if user['role'] == 'ngo':
                    lat, lng = 17.3850, 78.4867 # Default Hyderabad/Warangal general
                else:
                    lat, lng = 17.4000, 78.5000 # Volunteer default scattered
                    
            name = user.get('name') or user.get('email', '').split('@')[0].capitalize()

            map_points.append({
                "id": str(user['_id']),
                "name": name,
                "role": user['role'],
                "lat": lat,
                "lng": lng,
                "status": user.get('status', 'Unverified')
            })
            
        return jsonify({"status": "success", "data": map_points})
        
    except Exception as e:
        print(f"Map API Error: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500
