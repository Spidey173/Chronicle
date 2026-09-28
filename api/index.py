"""Vercel Serverless Function entrypoint for Chronicle FastAPI application."""

import sys
from pathlib import Path

# Add project root directory to sys.path so 'app' module can be imported anywhere
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.main import app

# Export for both ASGI and WSGI/serverless handlers
handler = app
application = app
