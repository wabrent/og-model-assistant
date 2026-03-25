#!/bin/bash
# Quick Start Script for OpenGradient Model Assistant

echo "🚀 OpenGradient Model Hub Assistant - Quick Start"
echo "=================================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your settings."
    echo ""
fi

# Check if virtual environment exists
if [ ! -d venv ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting server at http://localhost:8000"
echo "📖 API Docs at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start server
python main.py
