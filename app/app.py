import sys
import os

# Add parent directory to path to import app package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True)
