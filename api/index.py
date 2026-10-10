import os
import sys

# Ensure backend folder is in Python path for Vercel
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
