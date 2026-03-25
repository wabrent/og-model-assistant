@echo off
REM Quick Start Script for OpenGradient Model Assistant (Windows)

echo 🚀 OpenGradient Model Hub Assistant - Quick Start
echo ==================================================
echo.

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ .env file created.
    echo.
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo 🗄️  Initializing database...
python init_db.py

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Starting server at http://localhost:8000
echo 📖 API Docs at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

REM Start server
python main.py
