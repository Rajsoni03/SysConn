# System Flask REST API

This project is a Flask-based REST API system for managing commands and workareas, with authentication middleware and modular service structure.


## Features:
- [x] Restful API endpoints
- [x] Token-based authentication middleware
- [x] Create Directory
- [x] Execute Commands
- [ ] Execute Commands with Sudo
- [ ] Git Operations
- [ ] Project Make Operations (make, make clean, cmake, etc.)
- [ ] WebSocket for real-time command output streaming
- [ ] Repo Sync (repo init, repo sync, repo start, repo upload)
- [ ] Handle Multiple Workareas (Each workarea corresponds to a project directory on the user's PC)
- [ ] Logging and Error Handling
- [ ] Run other scripts (like setup scripts, build scripts, etc.)
- [x] update itself when requested from Django (pull latest code from a git repository and restart the service)


## Project Structure

```
app.py                # Main Flask app entry point
api/v1/               # API endpoints (commands, workarea)
services/             # Business logic for commands and workareas
src/                  # Shared code (e.g., authentication, config)
templates/            # HTML templates
data/                 # Contains Configuration file and DB files
```


## Setup and Run

### Running with start_server.sh

  - Clone the repository
    ```sh
    git clone https://github.com/Rajsoni03/system_flask.git
    cd system_flask
    ```
  - You can use the provided `start_server.sh` script to automate environment setup and start the server with Gunicorn:

    ```sh
    ./start_server.sh
    ```

### Manual Setup (for development/testing only)

1. Clone the repository
    ```sh
    git clone https://github.com/Rajsoni03/system_flask.git
    cd system_flask
    ```
2. Create and activate a Python virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Run the application:
    ```sh
    # to run the app for testing
    python app.py
    ```


## Configuration
Web Interface:
- Open browser and navigate to [`http://localhost:5500`](http://localhost:5500) in local machine.
- Set AUTH_TOKEN and SUDO_PASSWORD from web interface. This updates the config.json file in data directory.

Manual File Update:
- Update `data/config.json` with your desired `AUTH_TOKEN` and `SUDO_PASSWORD`.
- Restart the Flask app to apply changes.


## Authentication

All `/api/`, and `/update` endpoints require an `Authorization` header with a valid token:

```sh
curl -X GET http://localhost:5500/version \
  -H "Authorization: YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json"
```

## Documentation

API documentation is available at [`http://localhost:5500/docs`](http://localhost:5500/docs).

## License

See `LICENSE` for details.
