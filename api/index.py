"""Vercel Serverless Function entrypoint for Chronicle FastAPI application."""

import sys
from pathlib import Path

# Add project root directory to sys.path so 'app' module can be imported anywhere
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from app.main import app
    # Export for both ASGI and serverless handler callers
    handler = app
except Exception:
    import traceback
    err_trace = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI(title="Chronicle (Diagnostic)")
    handler = app

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"])
    def error_fallback(full_path: str = ""):
        html = f"""<!DOCTYPE html>
<html>
<head><title>Chronicle Startup Diagnostic</title></head>
<body style="font-family: monospace; background: #0a0607; color: #ff5e36; padding: 2rem;">
  <h2>⚠️ Chronicle Startup Diagnostic</h2>
  <p style="color: #a89297;">A startup exception occurred when loading the application:</p>
  <pre style="background: #180d11; padding: 1.5rem; border-radius: 8px; border: 1px solid #ff334b; overflow: auto; color: #fce7eb;">{err_trace}</pre>
</body>
</html>"""
        return HTMLResponse(content=html, status_code=500)
