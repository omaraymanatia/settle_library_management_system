#!/bin/bash

# Library Management System Frontend Launcher

echo "🚀 Starting Library Management System Frontend..."
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "📁 Frontend directory: $DIR"
echo "🐍 Using Python: $PYTHON_CMD"
echo ""

# Start the HTTP server
echo "🌐 Starting HTTP server on http://localhost:3000"
echo "📖 Access the Library Management System at: http://localhost:3000"
echo ""
echo "💡 Make sure the backend server is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$DIR"
$PYTHON_CMD -m http.server 3000