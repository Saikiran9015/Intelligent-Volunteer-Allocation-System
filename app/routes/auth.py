from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    role = request.args.get('role', 'donor')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        try:
            users = mongo.db.users
            existing_user = users.find_one({'email': email})
        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Database connection failure: {e}")
            flash('Strategic connection error. Our intelligence servers are under heavy load. Please try again in 60 seconds.', 'error')
            return redirect(url_for('auth.register'))
        
        if existing_user:
            flash('This identity is already registered in the UnitySync network.', 'error')
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password)
        
        # Base Data Structure
        user_data = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'phone': request.form.get('phone'),
            'is_verified': False,
            'otp_verified': False,
            'profile_complete': True,
            'kyc_status': 'Pending',
            'created_at': datetime.utcnow()
        }
        
        # Role Specific Data Mapping
        if role == 'ngo':
            user_data['ngo_details'] = {
                'name': request.form.get('ngo_name'),
                'type': request.form.get('ngo_type'),
                'establishment_year': request.form.get('est_year'),
                'website': request.form.get('website'),
                'registration_number': request.form.get('reg_no'),
                'tax_id': request.form.get('tax_id'),
                'license_number': request.form.get('license_no'),
                'address': request.form.get('address'),
                'city': request.form.get('city'),
                'state': request.form.get('state'),
                'vision': request.form.get('vision'),
                'mission': request.form.get('mission'),
                'causes': request.form.getlist('causes'),
                'bank_details': {
                    'bank_name': request.form.get('bank_name'),
                    'account_holder': request.form.get('acc_holder'),
                    'account_number': request.form.get('acc_no'),
                    'ifsc': request.form.get('ifsc')
                },
                'social': {
                    'facebook': request.form.get('fb_url'),
                    'linkedin': request.form.get('li_url'),
                    'twitter': request.form.get('tw_handle')
                }
            }
            # Mock file upload tracking
            user_data['documents'] = ['cert_reg', 'cert_pan', 'audit_report']
            
        elif role == 'donor':
            user_data['donor_details'] = {
                'full_name': request.form.get('donor_name'),
                'gender': request.form.get('gender'),
                'dob': request.form.get('dob'),
                'donation_cycle': request.form.get('don_cycle'),
                'interests': request.form.getlist('interests'),
                'tax_id': request.form.get('donor_tax_id'),
                'receipt_required': request.form.get('need_receipt') == 'Yes'
            }
            
        elif role == 'volunteer':
            user_data['volunteer_details'] = {
                'skills': request.form.get('skills', '').split(','),
                'languages': request.form.get('languages'),
                'experience_years': request.form.get('exp_years'),
                'availability': request.form.get('avail_type'),
                'deployment_zone': request.form.get('deployment_zone'),
                'health': {
                    'blood_group': request.form.get('blood_group')
                },
                'gov_id': request.form.get('gov_id'),
                'background_consent': request.form.get('background_check') == 'on'
            }

        try:
            users.insert_one(user_data)
        except Exception as e:
            current_app.logger.error(f"Persistence failure: {e}")
            flash('Strategic deployment failed. Please verify your connection status and coordinates.', 'error')
            return redirect(url_for('auth.register'))
        
        # Setup session for OTP verification
        session['pending_email'] = email
        flash(f'Strategic onboarding initiated! Please verify your deployment via OTP (Simulation: 12345)', 'success')
        return redirect(url_for('auth.verify_otp'))
        
    return render_template('auth/register.html', role=role)


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form.get('otp')
        if otp == '12345': # Simulated OTP
            email = session.get('pending_email')
            mongo.db.users.update_one({'email': email}, {'$set': {'otp_verified': True}})
            flash('Email verified! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        flash('Invalid OTP', 'error')
    return render_template('auth/verify_otp.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Special Admin Check
        if email == 'admin@unitysync.org' and password == 'UnitySyncAdmin@2026':
            session['user_id'] = 'admin'
            session['role'] = 'admin'
            return redirect(url_for('main.admin_dashboard'))

        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            return redirect(url_for('dashboard.index'))
        
        flash('Invalid credentials', 'error')
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
