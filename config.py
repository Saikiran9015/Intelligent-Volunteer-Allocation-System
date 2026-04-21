import os
from dotenv import load_dotenv
import certifi

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    MONGO_URI = os.environ.get('MONGO_URI')
    # Explicitly set DB name to avoid AttributeError in some environments
    MONGO_DBNAME = 'kindheart' 
    MONGO_TLS = True
    MONGO_TLSCAFILE = certifi.where()
    MONGO_TLSALLOWINVALIDCERTIFICATES = True
    MONGO_TLSALLOWINVALIDHOSTNAMES = True
    
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # Razorpay Keys
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_placeholder')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'placeholder_secret')
    
    # Shiprocket Credentials
    SHIPROCKET_EMAIL = os.environ.get('SHIPROCKET_EMAIL', 'admin@unitysync.org')
    SHIPROCKET_PASSWORD = os.environ.get('SHIPROCKET_PASSWORD', 'placeholder_pass')
    
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
