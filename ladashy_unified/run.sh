#!/bin/bash
# Run LaDashy Web Interface

echo "🚀 Starting LaDashy Web Interface..."
echo ""

# Kill any existing processes on our ports
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Start API server
cd backend
python api.py &
API_PID=$!
cd ..

# Give API time to start
sleep 2

# Start web server
cd frontend
python -m http.server 8080 &
WEB_PID=$!
cd ..

echo ""
echo "✅ LaDashy is running!"
echo ""
echo "🌐 Open your browser to: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop"

# Cleanup function
cleanup() {
    echo -e "\nStopping LaDashy..."
    kill $API_PID $WEB_PID 2>/dev/null
    exit 0
}

trap cleanup INT

# Wait
wait
