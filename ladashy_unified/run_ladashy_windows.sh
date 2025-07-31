#!/bin/bash
# Windows-specific launcher that opens browser automatically

cd ladashy_unified

# Start services
./run_ladashy.sh &

# Wait for services to start
sleep 4

# Open in default Windows browser
if command -v cmd.exe > /dev/null; then
    cmd.exe /c start http://localhost:8080
else
    echo "Open http://localhost:8080 in your browser"
fi
