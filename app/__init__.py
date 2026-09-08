import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from pathlib import Path
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# Initialize CSRF protection
csrf = CSRFProtect()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],  # No default limits, only apply to specific routes
    storage_uri="memory://"
)


def create_app():
    """Application factory for Flask app."""
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    
    # Load SECRET_KEY from environment
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set")
    if secret_key == 'your-secret-key' or secret_key == 'change-this-in-production':
        raise RuntimeError("SECRET_KEY must be changed from the default placeholder value")
    
    app.config['SECRET_KEY'] = secret_key
    
    # Session cookie hardening (Section 34a)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Set to False for local dev (no HTTPS), must be True in production
    app.config['SESSION_COOKIE_SECURE'] = False
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Initialize database connection and indexes
    from app.database import init_db
    init_db()
    
    # Register blueprints
    from app.auth import auth_bp
    from app.tasks import tasks_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    
    # Health check route
    @app.route('/health', methods=['GET'])
    def health():
        from app.database import check_connection
        mongo_status = 'connected' if check_connection() else 'disconnected'
        server_name = os.environ.get('SERVER_NAME', 'unknown')
        return jsonify({
            'status': 'healthy',
            'mongo': mongo_status,
            'server': server_name
        })
    
    # CSRF token endpoint for testing
    @app.route('/csrf-token', methods=['GET'])
    def get_csrf_token():
        """Get a CSRF token for testing purposes."""
        token = generate_csrf()
        return jsonify({'csrf_token': token}), 200
    
    # Root route - serve login page
    @app.route('/')
    def index():
        from flask import send_from_directory
        return send_from_directory('../frontend', 'login.html')
    
    return app
