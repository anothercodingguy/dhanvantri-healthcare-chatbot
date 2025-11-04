#!/bin/bash

# Dhanvantri Services Stop Script
echo "🛑 Stopping Dhanvantri Healthcare Chatbot Services..."

# Function to stop service by PID file
stop_service_by_pid() {
    local name=$1
    local pid_file="${name,,}_pid.txt"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo "Stopping $name (PID: $pid)..."
            kill $pid
            sleep 2
            if kill -0 $pid 2>/dev/null; then
                echo "Force stopping $name..."
                kill -9 $pid
            fi
            echo "✅ $name stopped"
        else
            echo "⚠️  $name process not found"
        fi
        rm -f "$pid_file"
    else
        echo "⚠️  No PID file found for $name"
    fi
}

# Function to stop service by port
stop_service_by_port() {
    local name=$1
    local port=$2
    
    echo "Checking for $name on port $port..."
    local pid=$(lsof -ti:$port)
    
    if [ -n "$pid" ]; then
        echo "Stopping $name (PID: $pid) on port $port..."
        kill $pid 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 $pid 2>/dev/null; then
            echo "Force stopping $name..."
            kill -9 $pid 2>/dev/null
        fi
        echo "✅ $name stopped"
    else
        echo "⚠️  No process found on port $port"
    fi
}

# Stop services by PID files first
stop_service_by_pid "Whisper"
stop_service_by_pid "Backend" 
stop_service_by_pid "Frontend"

echo ""
echo "Checking ports for any remaining processes..."

# Stop services by port as backup
stop_service_by_port "Whisper Service" 5001
stop_service_by_port "Backend API" 8000
stop_service_by_port "Frontend Dev Server" 3000

# Clean up any remaining PID files
rm -f whisper_pid.txt backend_pid.txt frontend_pid.txt

echo ""
echo "🎉 All services stopped successfully!"
echo ""
echo "To restart services, run: ./start_services.sh"