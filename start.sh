#!/bin/bash

# Exit on error
set -e

# Kill any existing process on port 5001
echo "Checking for existing process on port 5001..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists, copy example if not
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file to add your OpenAI API key"
fi

# Setup database
echo "Setting up database..."
python setup_database.py

# Run the Flask application
echo "Starting BSH Customer Complaints Management System..."
echo "================================================================="
echo "🚀 Your application is starting at: http://127.0.0.1:5001"
echo "📝 View the unified complaint tickets with all details and AI analysis"
echo "================================================================="
python app.py 