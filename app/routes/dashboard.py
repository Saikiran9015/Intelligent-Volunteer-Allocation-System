from flask import Blueprint, render_template, session, redirect, url_for, flash
from app import mongo
from bson.objectid import ObjectId

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def index():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('auth.login'))
        
    if session['user_id'] == 'admin':
        return redirect(url_for('main.admin_dashboard'))
        
    role = session.get('role')
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if role == 'ngo':
        return render_template('dashboards/ngo.html', user=user)
    elif role == 'donor':
        return render_template('dashboards/donor.html', user=user)
    elif role == 'volunteer':
        return render_template('dashboards/volunteer.html', user=user)
    
    return redirect(url_for('main.index'))

@dashboard_bp.route('/ngo/field-data')
def field_data():
    return render_template('dashboards/ngo_field_data.html')
