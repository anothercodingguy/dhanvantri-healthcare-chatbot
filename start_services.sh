#!/bin/bash

# Dhanvantri Services Startup Script
echo "🏥 Starting Dhanvantri Healthcare Chatbot Services..."

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to start a service in background
start_service() {
    local name=$1
    local command=$2
    local port=$3
    local dir=$4
    
    echo "Starting $name on port $port..."
    
    if [ -n "$dir" ]; then
        cd "$dir"
    fi
    
    # Start the service in background
    $command &
    local pid=$!
    
    # Wait a moment for service to start
    sleep 2
    
    # Check if service is still running
    if kill -0 $pid 2>/dev/null; then
        echo "✅ $name started successfully (PID: $pid)"
        echo $pid > "${name,,}_pid.txt"
    else
        echo "❌ Failed to start $name"
        return 1
    fi
    
    if [ -n "$dir" ]; then
        cd - > /dev/null
    fi
}

# Start Backend API (Port 8000)
echo ""
echo "1. Starting Backend API..."
if check_port 8000; then
    start_service "Backend" "python3 -m uvicorn main:app --reload --port 8000" 8000 "backend"
else
    echo "⚠️  Backend port 8000 is busy, skipping..."
fi

# Install frontend dependencies if needed
echo ""
echo "2. Checking Frontend Dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start Frontend (Port 3000)
echo ""
echo "3. Starting Frontend..."
cd ..
if check_port 3000; then
    start_service "Frontend" "npm run dev" 3000 "frontend"
else
    echo "⚠️  Frontend port 3000 is busy, skipping..."
fi

echo ""
echo "🎉 Services startup complete!"
echo ""
echo "📋 Service URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo ""
echo "📊 Health Checks:"
echo "   Backend Health: http://localhost:8000/api/health"
echo ""
echo "🛑 To stop all services, run: ./stop_services.sh"
echo ""
echo "📝 Logs are displayed in the terminal. Press Ctrl+C to stop all services."

# Wait for user input to stop services
echo "Press Ctrl+C to stop all services..."
trap 'echo ""; echo "Stopping services..."; kill $(jobs -p) 2>/dev/null; echo "All services stopped."; exit 0' INT

# Keep script running
wait