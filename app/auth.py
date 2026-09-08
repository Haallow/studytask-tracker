"""Authentication routes and handlers."""
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from app.database import get_users_collection
from app.models import is_plain_string, validate_password_length

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    # Extract fields
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    # Validate all fields exist
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    if not confirm_password:
        return jsonify({'error': 'Password confirmation is required'}), 400
    
    # Type validation (NoSQL injection guard)
    if not is_plain_string(username):
        return jsonify({'error': 'Username must be a string'}), 400
    if not is_plain_string(email):
        return jsonify({'error': 'Email must be a string'}), 400
    if not is_plain_string(password):
        return jsonify({'error': 'Password must be a string'}), 400
    if not is_plain_string(confirm_password):
        return jsonify({'error': 'Password confirmation must be a string'}), 400
    
    # Password validation
    if not validate_password_length(password):
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    # Password match validation (server-side)
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    # Hash password
    password_hash = generate_password_hash(password)
    
    # Create user document
    user_doc = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'created_at': datetime.utcnow()
    }
    
    # Insert into database
    users = get_users_collection()
    try:
        result = users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        return jsonify({
            'status': 'registered',
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        }), 201
    except DuplicateKeyError:
        # Unique index on email caught duplicate
        return jsonify({'error': 'Email already registered'}), 409


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and create a session."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    # Extract fields
    email = data.get('email')
    password = data.get('password')
    
    # Validate fields exist
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    if not password:
        return jsonify({'error': 'Password is required'}), 400
    
    # Type validation (NoSQL injection guard)
    if not is_plain_string(email):
        return jsonify({'error': 'Email must be a string'}), 400
    if not is_plain_string(password):
        return jsonify({'error': 'Password must be a string'}), 400
    
    # Find user by email
    users = get_users_collection()
    user = users.find_one({'email': email})
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password
    if not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create session
    session['user_id'] = str(user['_id'])
    session['username'] = user['username']
    
    return jsonify({
        'status': 'logged_in',
        'user': {
            'id': str(user['_id']),
            'username': user['username']
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """End the user's session."""
    session.clear()
    return jsonify({'status': 'logged_out'}), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get the current authenticated user's information."""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Fetch user from database
    users = get_users_collection()
    try:
        user = users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return jsonify({'error': 'Invalid user session'}), 401
    
    if not user:
        return jsonify({'error': 'User not found'}), 401
    
    return jsonify({
        'user': {
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email']
        }
    }), 200
