#!/bin/bash
# Run LaDashy - auto-detects best method

echo "=== Starting LaDashy Unified ==="
echo ""
echo "Choose how to run LaDashy:"
echo "1) Web Interface (recommended for WSL)"
echo "2) Desktop Mode (if GUI available)"
echo "3) Docker (requires Docker)"
echo ""
echo "Auto-starting Web Interface in 3 seconds..."
echo "(Press Ctrl+C to cancel and choose manually)"

# Wait 3 seconds for user to cancel
sleep 3

# Default to web interface for WSL
echo ""
echo "Starting Web Interface..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 LaDashy Web Interface"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📡 Starting API server on port 5000..."
echo "🖥️  Starting web UI on port 8080..."
echo ""

# Start the API server in background
python backend/api.py &
API_PID=$!

# Give API time to start
sleep 2

# Start a simple HTTP server for the frontend
cd frontend
python -m http.server 8080 &
UI_PID=$!
cd ..

echo ""
echo "✅ LaDashy is running!"
echo ""
echo "🔗 Access the web interface at:"
echo "   http://localhost:8080"
echo ""
echo "📝 API endpoints available at:"
echo "   http://localhost:5000/api/"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n\nShutting down LaDashy..."
    kill $API_PID 2>/dev/null
    kill $UI_PID 2>/dev/null
    echo "✅ LaDashy stopped"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup INT

# Wait for processes
wait
