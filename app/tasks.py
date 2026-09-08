"""Task CRUD routes and handlers."""
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from bson import ObjectId
from bson.errors import InvalidId

from app.database import get_tasks_collection

tasks_bp = Blueprint('tasks', __name__)

# Import limiter for potential future rate limiting
from app import limiter


def require_auth():
    """Check if user is authenticated, return user_id or None."""
    return session.get('user_id')


def is_valid_objectid(oid):
    """Check if a string is a valid ObjectId."""
    if oid is None:
        return False
    try:
        ObjectId(oid)
        return True
    except (InvalidId, TypeError):
        return False


@tasks_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks for the current user."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    tasks = get_tasks_collection()
    user_tasks = list(tasks.find({'user_id': user_id}))
    
    # Convert ObjectId to string for JSON serialization
    for task in user_tasks:
        task['_id'] = str(task['_id'])
        if 'created_at' in task:
            task['created_at'] = task['created_at'].isoformat()
    
    return jsonify({'tasks': user_tasks}), 200


@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Validate ObjectId
    if not is_valid_objectid(task_id):
        return jsonify({'error': 'Invalid task ID'}), 400
    
    tasks = get_tasks_collection()
    task = tasks.find_one({'_id': ObjectId(task_id)})
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check ownership
    if task.get('user_id') != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Convert ObjectId to string
    task['_id'] = str(task['_id'])
    if 'created_at' in task:
        task['created_at'] = task['created_at'].isoformat()
    
    return jsonify({'task': task}), 200


@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task for the current user."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    # Extract and validate fields
    title = data.get('title')
    subject = data.get('subject')
    description = data.get('description', '')
    due_date = data.get('due_date')
    priority = data.get('priority', 'Medium')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if not subject:
        return jsonify({'error': 'Subject is required'}), 400
    
    # Create task document
    task_doc = {
        'user_id': user_id,
        'title': title,
        'subject': subject,
        'description': description,
        'due_date': due_date,
        'priority': priority,
        'completed': False,
        'created_at': datetime.utcnow()
    }
    
    tasks = get_tasks_collection()
    result = tasks.insert_one(task_doc)
    
    task_doc['_id'] = str(result.inserted_id)
    task_doc['created_at'] = task_doc['created_at'].isoformat()
    
    return jsonify({
        'status': 'created',
        'task': task_doc
    }), 201


@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Validate ObjectId
    if not is_valid_objectid(task_id):
        return jsonify({'error': 'Invalid task ID'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    tasks = get_tasks_collection()
    task = tasks.find_one({'_id': ObjectId(task_id)})
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check ownership
    if task.get('user_id') != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Build update document
    update_fields = {}
    if 'title' in data:
        update_fields['title'] = data['title']
    if 'subject' in data:
        update_fields['subject'] = data['subject']
    if 'description' in data:
        update_fields['description'] = data['description']
    if 'due_date' in data:
        update_fields['due_date'] = data['due_date']
    if 'priority' in data:
        update_fields['priority'] = data['priority']
    if 'completed' in data:
        update_fields['completed'] = data['completed']
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
    
    tasks.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': update_fields}
    )
    
    # Fetch updated task
    updated_task = tasks.find_one({'_id': ObjectId(task_id)})
    updated_task['_id'] = str(updated_task['_id'])
    if 'created_at' in updated_task:
        updated_task['created_at'] = updated_task['created_at'].isoformat()
    
    return jsonify({
        'status': 'updated',
        'task': updated_task
    }), 200


@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Validate ObjectId
    if not is_valid_objectid(task_id):
        return jsonify({'error': 'Invalid task ID'}), 400
    
    tasks = get_tasks_collection()
    task = tasks.find_one({'_id': ObjectId(task_id)})
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check ownership
    if task.get('user_id') != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    tasks.delete_one({'_id': ObjectId(task_id)})
    
    return jsonify({'status': 'deleted'}), 200


@tasks_bp.route('/tasks/<task_id>/complete', methods=['PATCH'])
def toggle_complete(task_id):
    """Toggle task completion status."""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Validate ObjectId
    if not is_valid_objectid(task_id):
        return jsonify({'error': 'Invalid task ID'}), 400
    
    tasks = get_tasks_collection()
    task = tasks.find_one({'_id': ObjectId(task_id)})
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    # Check ownership
    if task.get('user_id') != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Toggle completed status
    new_status = not task.get('completed', False)
    tasks.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': {'completed': new_status}}
    )
    
    # Fetch updated task
    updated_task = tasks.find_one({'_id': ObjectId(task_id)})
    updated_task['_id'] = str(updated_task['_id'])
    if 'created_at' in updated_task:
        updated_task['created_at'] = updated_task['created_at'].isoformat()
    
    return jsonify({
        'status': 'updated',
        'task': updated_task
    }), 200
