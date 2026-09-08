import os
from flask import Flask, jsonify
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / '.env')


def create_app():
    """Application factory for Flask app."""
    app = Flask(__name__)
    
    # Load SECRET_KEY from environment
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")
    if secret_key == 'your-secret-key' or secret_key == 'change-this-in-production':
        raise RuntimeError("SECRET_KEY must be changed from the default placeholder value")
    
    app.config['SECRET_KEY'] = secret_key
    
    # Initialize database connection and indexes
    from app.database import init_db
    init_db()
    
    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Health check route
    @app.route('/health', methods=['GET'])
    def health():
        from app.database import check_connection
        mongo_status = 'connected' if check_connection() else 'disconnected'
        return jsonify({
            'status': 'healthy',
            'mongo': mongo_status
        })
    
    return app
