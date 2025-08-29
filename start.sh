#!/bin/bash

# Start the Financial Review Application
echo "🚀 Starting Financial Review Application..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Start backend in background
echo "📡 Starting FastAPI backend..."
source .venv/bin/activate
python api/main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
echo "✅ Services started!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait
