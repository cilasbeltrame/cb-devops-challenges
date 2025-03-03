#!/bin/bash

# Start the backend API
echo "Starting the backend API..."
cd backend
python api.py &
BACKEND_PID=$!

# Wait for the backend to start
echo "Waiting for the backend to start..."
sleep 3

# Start the frontend development server
echo "Starting the frontend development server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

# Keep the script running
echo "Both servers are running. Press Ctrl+C to stop."
wait 
