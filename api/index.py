import sys
import os

# Add the project root to the Python path so imports work on Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

# Vercel expects the WSGI app to be exposed as 'app' or 'handler'
