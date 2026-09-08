import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure

_client = None
_db = None


def init_db():
    """Initialize MongoDB connection and create indexes."""
    global _client, _db
    
    mongo_uri = os.environ.get('MONGO_URI')
    mongo_db = os.environ.get('MONGO_DB')
    
    if not mongo_uri:
        raise RuntimeError("MONGO_URI environment variable is not set")
    if not mongo_db:
        raise RuntimeError("MONGO_DB environment variable is not set")
    
    _client = MongoClient(mongo_uri)
    _db = _client[mongo_db]
    
    # Verify connection
    try:
        _client.admin.command('ping')
    except ConnectionFailure:
        raise RuntimeError("Failed to connect to MongoDB")
    
    # Create indexes
    _db.users.create_index("email", unique=True)
    _db.tasks.create_index("user_id")


def get_db():
    """Get the database instance."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _db


def get_collection(name):
    """Get a specific collection from the database."""
    db = get_db()
    return db[name]


def get_users_collection():
    """Get the users collection."""
    return get_collection('users')


def get_tasks_collection():
    """Get the tasks collection."""
    return get_collection('tasks')


def check_connection():
    """Check if MongoDB is connected."""
    try:
        if _client is None:
            return False
        _client.admin.command('ping')
        return True
    except Exception:
        return False
