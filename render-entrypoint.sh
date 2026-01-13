#!/bin/bash
set -e

echo "🏥 Starting Dhanvantri on Render..."

# Set up environment
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
export NODE_ENV=production
export PORT=${PORT:-8000}

# Create necessary directories
mkdir -p /tmp/logs

# Function to start service in background
start_service() {
    local name=$1
    local command=$2
    local port=$3
    
    echo "Starting $name on port $port..."
    $command &
    local pid=$!
    echo $pid > "/tmp/${name,,}_pid"
    
    # Wait for service to be ready (shorter timeout for Render)
    for i in {1..15}; do
        if curl -f "http://localhost:$port/health" >/dev/null 2>&1 || \
           curl -f "http://localhost:$port/api/health" >/dev/null 2>&1; then
            echo "✅ $name is ready"
            return 0
        fi
        echo "Waiting for $name to be ready... ($i/15)"
        sleep 2
    done
    
    echo "⚠️ $name may not be fully ready, continuing..."
    return 0
}

# Start Backend API (main service)
echo "2. Starting Backend API..."
cd /opt/render/project/src/backend

# Use gunicorn for better production performance on Render
if command -v gunicorn &> /dev/null; then
    echo "Using Gunicorn for production..."
    start_service "Backend" "gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 30" $PORT
else
    echo "Using Uvicorn..."
    start_service "Backend" "python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1" $PORT
fi

echo "🎉 Dhanvantri started successfully!"
echo ""
echo "📋 Service Info:"
echo "   Application: https://${RENDER_EXTERNAL_HOSTNAME:-localhost:$PORT}"
echo "   Health Check: https://${RENDER_EXTERNAL_HOSTNAME:-localhost:$PORT}/api/health"
echo "   API Docs: https://${RENDER_EXTERNAL_HOSTNAME:-localhost:$PORT}/docs"

# Function to handle shutdown
shutdown() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill background processes
    for pid_file in /tmp/*_pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                echo "Stopping process $pid..."
                kill "$pid"
            fi
            rm -f "$pid_file"
        fi
    done
    
    echo "✅ Shutdown complete"
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Keep container running and forward signals
wait