# Project Repository

This is the initial README file for the project.

## Backend Dynamic Port Configuration

The StudyHub backend (FastAPI) now supports running on any available port using the `BACKEND_PORT` environment variable.  
- By default, if `BACKEND_PORT` is not set, the backend will run on port **8000**.
- To specify a different port, set the desired port number:

```sh
export BACKEND_PORT=9001
python src/api/run_backend.py
```

The FastAPI app is started via `src/api/run_backend.py`, which will detect the environment variable and start using the requested port.
If the value is not a valid integer or is unavailable, the server will fall back to 8000.