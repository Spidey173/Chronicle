"""Application root entrypoint."""

import sys
from app.cli import app as cli_app
from app.main import app as fastapi_app

if __name__ == "__main__":
    # If arguments are passed, execute CLI; otherwise start web server
    if len(sys.argv) > 1:
        cli_app()
    else:
        import uvicorn
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
