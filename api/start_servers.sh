#!/bin/bash

# Start both API and CDN servers for PecanTV
# Usage: ./start_servers.sh

echo "🚀 Starting PecanTV Servers..."

# Kill any existing processes
echo "🔄 Stopping existing servers..."
pkill -f "python3 main.py" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null

# Wait a moment for processes to stop
sleep 2

# Start API server on port 8000
echo "📡 Starting API server on port 8000..."
nohup python3 main.py --port 8000 > api_server.log 2>&1 &
API_PID=$!

# Start CDN server on port 8001
echo "🌐 Starting CDN server on port 8001..."
nohup python3 main.py --port 8001 > cdn_server.log 2>&1 &
CDN_PID=$!

# Wait for servers to start
echo "⏳ Waiting for servers to start..."
sleep 5

# Test both servers
echo "🧪 Testing servers..."

# Test API server
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API server (port 8000) is running"
else
    echo "❌ API server (port 8000) failed to start"
fi

# Test CDN server
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ CDN server (port 8001) is running"
else
    echo "❌ CDN server (port 8001) failed to start"
fi

echo ""
echo "📊 Server Status:"
echo "   API Server:  http://localhost:8000"
echo "   CDN Server:  http://localhost:8001"
echo "   API Health:  http://localhost:8000/health"
echo "   CDN Health:  http://localhost:8001/health"
echo ""
echo "📝 Logs:"
echo "   API Log:     api_server.log"
echo "   CDN Log:     cdn_server.log"
echo ""
echo "🛑 To stop servers: pkill -f 'python3 main.py'" 