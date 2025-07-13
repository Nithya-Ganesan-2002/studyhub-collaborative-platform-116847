import os

import uvicorn

def main():
    """
    Entrypoint script for running the StudyHub FastAPI backend.

    This script will start the FastAPI app using the port specified by the BACKEND_PORT
    environment variable. If BACKEND_PORT is not set or invalid, it will default to 8000.

    Usage:
        Set BACKEND_PORT in your environment to control port assignment.
        Example:
            BACKEND_PORT=9000 python src/api/run_backend.py
        Or, to use default:
            python src/api/run_backend.py
    """
    port = 8000
    env_port = os.getenv("BACKEND_PORT")
    if env_port:
        try:
            port = int(env_port)
        except ValueError:
            print(f"[WARNING] BACKEND_PORT ('{env_port}') is not a valid integer. Using default 8000.")

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        access_log=True,
    )

if __name__ == "__main__":
    main()
