# Installation Guide

This guide will help you set up OpenGradient Model Hub Assistant on your local machine.

## System Requirements

- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB free disk space
- Internet connection (for OpenGradient API)

## Quick Installation (Windows)

### Option 1: Automated Script

1. Download the project
2. Double-click `start.bat`
3. Wait for installation to complete
4. Open http://localhost:8000 in your browser

### Option 2: Manual Installation

1. **Install Python**
   - Download from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH"

2. **Clone or Download Project**
   ```bash
   git clone https://github.com/yourusername/og-model-assistant.git
   cd og-model-assistant-pro
   ```

3. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

4. **Activate Virtual Environment**
   ```bash
   venv\Scripts\activate
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Initialize Database**
   ```bash
   python init_db.py
   ```

7. **Start Server**
   ```bash
   python main.py
   ```

8. **Open Browser**
   - Go to http://localhost:8000

## Installation (Linux/Mac)

1. **Install Python**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip python3-venv

   # Mac (with Homebrew)
   brew install python
   ```

2. **Clone Project**
   ```bash
   git clone https://github.com/yourusername/og-model-assistant.git
   cd og-model-assistant-pro
   ```

3. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   ```

4. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Initialize Database**
   ```bash
   python init_db.py
   ```

7. **Start Server**
   ```bash
   python main.py
   ```

8. **Open Browser**
   - Go to http://localhost:8000

## Installation with Docker

1. **Install Docker**
   - Download from https://www.docker.com/get-started

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **View Logs**
   ```bash
   docker-compose logs -f
   ```

4. **Open Browser**
   - Go to http://localhost:8000

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and edit:

```bash
# OpenGradient API (optional - works without for demo)
PRIVATE_KEY=your_private_key_here

# Database (optional - uses SQLite by default)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/og_assistant

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:** Change the port in `.env`:
```bash
API_PORT=8001
```

### Database Errors

**Error:** `no such table`

**Solution:** Reset the database:
```bash
python init_db.py --reset
```

### Module Not Found

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### OpenGradient API Error

**Error:** `402 Payment Required`

**Solution:** The app works without an API key using fallback responses. Add your key to `.env` for full functionality.

## Verify Installation

1. Open http://localhost:8000
2. You should see the welcome screen
3. Try sending a message in chat
4. Check API docs at http://localhost:8000/docs

## Next Steps

- [Read the README](README.md) for features overview
- [Check API Documentation](http://localhost:8000/docs)
- [View Contributing Guide](CONTRIBUTING.md)

## Getting Help

- Open an issue on GitHub
- Check existing issues for solutions
- Contact @graanit2 on Twitter

---

**Happy coding! 🚀**
