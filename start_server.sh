#!/bin/bash

echo "🚀 Starting System Flask Server with Gunicorn"

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root is not recommended"
    echo "   Consider creating a dedicated user for the application"
fi

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
            python3 -m venv venv
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