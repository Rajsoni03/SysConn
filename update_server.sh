#!/bin/bash

# pull the latest changes from the repository
echo "🔄 Pulling latest changes from the repository..."
git pull origin main
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull latest changes. Please check your network connection and repository status."
    exit 1
fi

# install dependencies
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies. Please check the error messages above."
    exit 1
fi

# restart the server
echo "🔄 Restarting the server..."
# pkill -f gunicorn
# ./start_server.sh