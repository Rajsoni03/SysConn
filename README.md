# System Flask REST API

This project is a Flask-based REST API system for managing commands and workareas, with authentication middleware and modular service structure.


## Features

-   RESTful API endpoints for system commands and workareas
-   Token-based authentication middleware
-   Modular code structure (services, API, config)
-   Template rendering


## Project Structure

```
app.py                # Main Flask app entry point
api/v1/               # API endpoints (commands, workarea)
services/             # Business logic for commands and workareas
src/                  # Shared code (e.g., authentication, config)
templates/            # HTML templates
config/config.json    # Configuration file
```


## Setup and Run

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

    # or to run the app in background
    nohup python app.py > app.log 2>&1 &
    ```


## Configuration
Web Interface:
- Open browser and navigate to [`http://localhost:5500`](http://localhost:5500) in local machine.
- Set AUTH_TOKEN and SUDO_PASSWORD from web interface. This updates the config.json file in config directory.

Manual File Update:
- Update `config/config.json` with your desired `AUTH_TOKEN` and `SUDO_PASSWORD`.
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
