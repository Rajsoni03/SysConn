#!/bin/bash


# Check if python3.10 is available
if ! command -v python3.10 &> /dev/null; then
    echo "❌ Error: python3.10 is not installed or not in PATH."
    echo "   Please install Python 3.10 before running this script."
    exit 1
fi

# Check if lsof is available
if ! command -v lsof &> /dev/null; then
    OS=$(uname -s)
    if [ "$OS" = "Linux" ]; then
        # Check for Ubuntu
        if [ -f /etc/os-release ] && grep -qi 'ubuntu' /etc/os-release; then
            echo "🔍 'lsof' not found. Installing lsof (Ubuntu only)..."
            sudo apt update && sudo apt install -y lsof
        else
            echo "❌ Error: 'lsof' is required but not found. Please install it manually."
            exit 1
        fi
    elif [ "$OS" = "Darwin" ]; then
        echo "❌ Error: 'lsof' is required but not found. Please install it manually on macOS."
        exit 1
    else
        echo "❌ Error: 'lsof' is required but not found. Unsupported OS."
        exit 1
    fi
fi

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root is not recommended"
    echo "   Consider creating a dedicated user for the application"
fi

echo "🚀 Starting SysConn Server with Gunicorn"

# Check if port 5500 is already in use
PID=$(lsof -ti :5500)
if [ ! -z "$PID" ]; then
    echo "❌ Error: Port 5500 is already in use by process ID $PID."
    read -p "Do you want to stop this process? [y/N]: " choice
    case "$choice" in
        y|Y )
            kill -9 $PID
            echo "✅ Process $PID killed."
            ;;
        * )
            echo "⏹️  Please stop the process manually or choose another port."
            exit 1
            ;;
    esac
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
else
    echo "⚠️  Virtual environment 'venv' not found."
    read -p "Do you want to create it now? [y/N]: " create_venv
    case "$create_venv" in
        y|Y )
            python3.10 -m venv venv
            echo "✅ Virtual environment 'venv' created."
            source venv/bin/activate
            echo "📥 Installing dependencies..."
            pip install -r requirements.txt
            ;;
        * )
            echo "⏹️  Please create the virtual environment and install dependencies manually."
            exit 1
            ;;
    esac
fi

# Allow incoming traffic on port 5500 (Linux only)
OS=$(uname -s)
if [ "$OS" = "Linux" ]; then
    if sudo iptables -C INPUT -p tcp --dport 5500 -j ACCEPT 2>/dev/null; then
        echo "✅ Firewall rule for port 5500 already exists."
    else
        echo "🔍 Warning: Please manually allow incoming traffic on port 5500..."
    fi
fi

# Create logs directory
mkdir -p logs
echo "--------------------[ Starting Server - $(date) ]--------------------" >> logs/access.log
echo "--------------------[ Starting Server - $(date) ]--------------------" >> logs/error.log

# Start the server
echo "🌟 Starting server on http://localhost:5500 and http://0.0.0.0:5500"
echo "🔋 Health check: http://localhost:5500/health"
echo ""

# Run with Gunicorn - use the Flask app, not socketio
gunicorn \
    --worker-class eventlet \
    --workers 1 \
    --bind 0.0.0.0:5500 \
    --timeout 60 \
    --keep-alive 2 \
    --max-requests 1000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --capture-output \
    --log-level info \
    --reload \
    app:app &

echo "✅ Server Running in background..."
echo "📊 Access logs: logs/access.log"
echo "🚨 Error logs: logs/error.log"