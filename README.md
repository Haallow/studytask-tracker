# StudyTask Tracker

A containerized student task management application with user authentication, MongoDB persistence, NGINX load balancing, and cloud deployment support.

## Overview

StudyTask Tracker allows students to create, manage, and track their academic tasks. The application demonstrates modern web development practices including:

- **User authentication** with secure password hashing
- **REST API** with CSRF protection and rate limiting
- **MongoDB** for persistent data storage
- **Docker & Docker Compose** for containerization
- **NGINX** reverse proxy and load balancing
- **Plain HTML/CSS/JavaScript** frontend (no frameworks)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Or: Python 3.8+, MongoDB, pip

### Running Locally (with Docker Compose)

```bash
# Clone the repository
git clone <repo-url>
cd studytask-tracker

# Start all services
docker-compose up -d

# Access the application
# Open http://localhost in your browser
```

### Running Locally (without Docker)

```bash
# Install dependencies
pip install -r app/requirements.txt

# Start MongoDB (if not running)
# MongoDB should be accessible at mongodb://localhost:27017/

# Set environment variables
export FLASK_ENV=development
export MONGO_URI=mongodb://localhost:27017/
export MONGO_DB=studytask
export SECRET_KEY=your-secret-key-here

# Run the Flask app
python app/app.py

# Access the application
# Open http://localhost:5000 in your browser
```

## Project Structure

```
studytask-tracker/
├── app/
│   ├── __init__.py          # Flask app factory, CSRF & rate limiting setup
│   ├── app.py               # Entry point, runs dev server
│   ├── auth.py              # Authentication routes (register, login, logout, me)
│   ├── tasks.py             # Task CRUD routes
│   ├── database.py          # MongoDB connection & index creation
│   ├── models.py            # Validation helpers
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── dashboard.html       # Main task management dashboard
│   ├── app.js               # API client functions
│   └── style.css            # Styling
├── nginx/
│   └── nginx.conf           # NGINX reverse proxy & load balancing config
├── mongo/
│   └── init.js              # MongoDB initialization (optional)
├── Dockerfile               # Flask application container
├── docker-compose.yaml      # Multi-container orchestration
├── .env                     # Environment variables (local, not committed)
├── .env_example             # Template for .env file
└── README.md                # This file
```

## Features

### User Authentication

- **Registration**: Create account with username, email, password
- **Login**: Authenticate with email and password
- **Password Security**: Passwords hashed with bcrypt via Werkzeug
- **Session Management**: Secure session cookies with HttpOnly and SameSite attributes
- **Rate Limiting**: 10 requests/minute on login and registration endpoints

### Task Management

- **Create**: Add tasks with title, subject, description, due date, and priority
- **Read**: View all your tasks or a specific task
- **Update**: Edit any field of your tasks
- **Delete**: Remove tasks
- **Complete**: Mark tasks as done/undone
- **Filter**: Tasks are automatically filtered by logged-in user

### Security

- **CSRF Protection**: All state-changing requests require CSRF tokens
- **NoSQL Injection Guard**: String type validation on auth inputs
- **Password Validation**: Minimum 8 characters, server-side confirmation check
- **User Isolation**: Users can only view/edit their own tasks (403 Forbidden otherwise)
- **ObjectId Validation**: Invalid task IDs return 400 Bad Request
- **Session Cookies**: HttpOnly, SameSite=Lax, Secure in production

### Load Balancing

- **Multiple Flask Instances**: Easily scale to multiple app containers
- **NGINX**: Routes traffic across Flask instances
- **Shared SECRET_KEY**: Both Flask containers read from same `.env` for session compatibility
- **Health Checks**: `/health` endpoint reports MongoDB connection status

## API Endpoints

### Public Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves login page |
| GET | `/health` | Health check (status + MongoDB connection) |
| GET | `/csrf-token` | Get CSRF token for testing |

### Authentication Routes (rate-limited: 10/min)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Authenticate user |
| POST | `/logout` | End session |
| GET | `/me` | Get current user info |

### Task Routes (requires authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tasks` | Get all user's tasks |
| POST | `/tasks` | Create new task |
| GET | `/tasks/<id>` | Get specific task |
| PUT | `/tasks/<id>` | Update task |
| DELETE | `/tasks/<id>` | Delete task |
| PATCH | `/tasks/<id>/complete` | Toggle completion status |

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# MongoDB connection
MONGO_URI=mongodb://mongodb:27017/
MONGO_DB=studytask

# Flask security key (must be changed from placeholder in production)
SECRET_KEY=your-very-secret-key-here-change-this
```

See `.env_example` for template.

### Database

MongoDB collections:

**users**
- `_id`: ObjectId (unique)
- `username`: String
- `email`: String (unique index)
- `password_hash`: String (bcrypt hash)
- `created_at`: DateTime

**tasks**
- `_id`: ObjectId (unique)
- `user_id`: ObjectId (references users._id, indexed)
- `title`: String
- `subject`: String
- `description`: String
- `due_date`: String (YYYY-MM-DD format)
- `priority`: String (Low, Medium, High)
- `completed`: Boolean
- `created_at`: DateTime

## Development

### Running Tests

```bash
# Test backend routes and validation
python verify_complete.py

# Manual API testing with CSRF token
# See CSRF_TESTING.md for examples
```

### Adding Features

The codebase follows these patterns:

1. **Blueprints**: All route modules are Flask Blueprints registered in `create_app()`
2. **Authentication**: Use `session.get('user_id')` to check authentication
3. **Database**: Use `get_collection()` functions from `app/database.py`
4. **Validation**: Import helpers from `app/models.py`
5. **CSRF**: Automatically applied to POST/PUT/DELETE/PATCH routes

### Frontend Architecture

- **Single Page Navigation**: JavaScript loads pages without full page refresh
- **CSRF Tokens**: `app.js` fetches and includes tokens on all API calls
- **Error Handling**: All API errors show user-friendly messages
- **Session Check**: Dashboard checks authentication and redirects to login if needed

## Docker Deployment

### Services

**nginx** - Reverse proxy and load balancer on port 80
**flask1** - First Flask app instance on internal port 5000
**flask2** - Second Flask app instance on internal port 5000
**mongodb** - MongoDB database with persistent volume

### Building Images

```bash
# Build all services
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Verification

```bash
# Check health of Flask instances
curl http://localhost/health
curl http://localhost/health  # May alternate between flask1 and flask2

# Check task access by starting two users
# Open http://localhost in two different browsers
# Register different users in each
# Verify user isolation (users see only their own tasks)
```

## Production Deployment

### DigitalOcean VPS Setup

1. **Create VPS** with Docker pre-installed
2. **Clone repository** to server
3. **Create `.env` file** with production values:
   ```env
   MONGO_URI=mongodb://mongodb:27017/
   MONGO_DB=studytask
   SECRET_KEY=<generate-secure-random-key>
   ```
4. **Run Docker Compose**:
   ```bash
   docker-compose up -d
   ```
5. **Configure HTTPS** with Let's Encrypt/Certbot
6. **Update NGINX config** to enable HTTPS and set `SESSION_COOKIE_SECURE=True`

### Security Checklist

- [ ] Change `SECRET_KEY` in `.env` to a secure random value
- [ ] Set `SESSION_COOKIE_SECURE=True` in production (requires HTTPS)
- [ ] Disable Flask debug mode (`FLASK_ENV=production`)
- [ ] Use HTTPS only (redirect HTTP to HTTPS)
- [ ] Keep dependencies updated (`pip freeze > app/requirements.txt`)
- [ ] Monitor application logs
- [ ] Set up database backups

## Troubleshooting

### MongoDB Connection Error

```
RuntimeError: Failed to connect to MongoDB
```

**Solution**: Ensure MongoDB is running and accessible at `MONGO_URI`

### CSRF Token Errors

```json
{"error": "The CSRF token is missing."}
```

**Solution**: Frontend must fetch CSRF token from `/csrf-token` and include as `X-CSRFToken` header

### Rate Limiting (429)

```json
{"error": "Rate limit exceeded"}
```

**Solution**: Wait 1 minute before making more login/register attempts

### Task Access Denied (403)

```json
{"error": "Access denied"}
```

**Solution**: Trying to access another user's task. Only your own tasks are accessible.

## Performance Considerations

- **MongoDB Indexes**: Created automatically on startup (email unique, user_id indexed)
- **CSRF Token Caching**: Frontend caches token and reuses it across requests
- **Session Storage**: Client-side signed cookies (no server session store needed)
- **Load Balancing**: Multiple Flask instances share nothing (stateless design)

## Future Enhancements (Out of Scope)

- [ ] Task categories/tags
- [ ] Task sharing with other users
- [ ] Task reminders/notifications
- [ ] Recurring tasks
- [ ] Mobile app
- [ ] Advanced search/filtering
- [ ] Task attachments
- [ ] Comment/collaboration on tasks

## License

This project is for educational purposes.


