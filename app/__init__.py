from flask import Flask
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from config import Config
mongo = PyMongo()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app, 
                  tlsCAFile=app.config.get('MONGO_TLSCAFILE'),
                  tlsAllowInvalidCertificates=app.config.get('MONGO_TLSALLOWINVALIDCERTIFICATES', True),
                  tlsAllowInvalidHostnames=app.config.get('MONGO_TLSALLOWINVALIDHOSTNAMES', True))
    
    # In serverless environments like Vercel, we should avoid blocking startup
    # with index creation which can timeout (especially if DB is waking up).
    # Indices should be created once in Atlas or through a separate migration.

    socketio.init_app(app, cors_allowed_origins="*")

    # Register Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.ai_features import ai_bp
    from app.routes.donor import donor_bp
    from app.routes.map_features import map_bp
    from app.routes.payment import payment_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(payment_bp)

    return app
