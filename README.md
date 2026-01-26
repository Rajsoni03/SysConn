# SysConn (System Connection) REST API

This project is a Flask-based REST API system for connecting to and managing system resources, running tests, with authentication middleware and modular service structure.

## Features:
- [x] Restful API endpoints
- [x] Token-based authentication middleware with web interface for configuration
- [x] Create Directory
- [x] Execute Commands
- [ ] Execute Commands with Sudo
- [ ] Execute Tests
- [ ] Multiple test flow support
- [ ] Plugin system for extensibility
- [ ] WebSocket for real-time command output streaming
- [ ] Logging and Error Handling
- [x] update itself when requested from Django (pull latest code from a git repository and restart the service)


## Project Structure

```
SysConn/
├── app.py.                           # Main Flask app entry point
├── requirements.txt                  # Python dependencies
├── start_server.sh                   # Script to set up environment and start the server
├── LICENSE                           # License file
├── README.md                         # Project documentation
├── api/
│   ├── common/                       # Shared API logic (core_api.py)
│   └── v1/                           # API v1 endpoints (command.py, workarea.py, run_test.py)
├── data/
│   ├── config.json                   # Configuration file (AUTH_TOKEN, SUDO_PASSWORD, etc.)
│   └── db/                           # Local Json Database files
├── logs/                             # Log files and log documentation
├── src/
│   ├── app/                          # App-level logic (auth, config_loader, db_client, settings)
│   ├── core/                         # Core utilities (plugin_engine, session_manager)
│   ├── modules/                      # Hardware modules (relay, uart)
│   ├── plugins/                      # Plugin system (base_plugin, plugin_engine, result_plugin)
│   ├── services/                     # Business logic (command_service, test_executor_service, workarea_service)
│   ├── test_flow/                    # Test flow logic (base_flow, command_line, flow_list)
│   └── utils/                        # Utility functions (exception, ip_utils, singleton)
└── templates/                        # HTML templates for web interface
```


## Setup and Run

### Prerequisites
- Python 3.10 or higher

### Open application port for incoming connections

- Ensure port `5500` is open on your firewall to allow incoming connections to the Flask application.
```
sudo iptables -A INPUT -p tcp --dport 5500 -j ACCEPT
```

### Running with start_server.sh

  - Clone the repository
    ```sh
    git clone https://github.com/Rajsoni03/SysConn.git
    cd SysConn
    ```
  - You can use the provided `start_server.sh` script to automate environment setup and start the server with Gunicorn:

    ```sh
    ./start_server.sh
    ```

### Manual Setup (for development/testing only)

1. Clone the repository
    ```sh
    git clone https://github.com/Rajsoni03/SysConn.git
    cd SysConn
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
