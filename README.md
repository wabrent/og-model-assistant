# 🚀 OpenGradient Model Hub Assistant

AI-powered assistant for discovering and exploring AI models on OpenGradient Model Hub.

![OpenGradient](https://img.shields.io/badge/OpenGradient-Model%20Hub-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🔍 **Smart Search** - Find AI models using natural language queries
- 💬 **AI Chat** - Conversational interface powered by OpenGradient LLM (GROK-4-Fast)
- 🎤 **Voice Input** - Speech-to-text support for hands-free operation
- 🖼️ **Vision AI** - Upload images for AI analysis
- ⭐ **Favorites** - Save your favorite models
- 🎮 **Gamification** - Level system and achievements
- 🌓 **Dark/Light Theme** - Beautiful themes
- 💎 **Free Tokens** - Auto-claim 5 tokens every 5 hours from faucet
- 📊 **Analytics** - Real-time statistics and model insights
- 📤 **Export** - Export conversations to PDF, Notion, Twitter

## 🎯 What's New

- **Automatic Token Faucet** - Get 5 free tokens every 5 hours automatically
- **No Payment Required** - Completely free to use
- **Beautiful Studio Agatho Design** - Modern, colorful interface with smooth animations
- **Persistent Chat History** - Your conversations are saved locally
- **Multi-language Support** - Interface available in 7 languages

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- OpenGradient API key (optional - works without for demo)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/og-model-assistant.git
cd og-model-assistant-pro

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional)
# PRIVATE_KEY=your_opengradient_private_key

# Start the application
python main.py
```

Open http://localhost:8000 in your browser.

## 📁 Project Structure

```
og-model-assistant-pro/
├── api/                    # API routers
│   ├── models_router.py    # Model search endpoints
│   ├── chat_router.py      # Chat endpoints
│   ├── analytics_router.py # Analytics endpoints
│   ├── sync_router.py      # Sync endpoints
│   ├── health_router.py    # Health check endpoints
│   └── tokens_router.py    # Token/faucet endpoints
├── bots/                   # Telegram & Discord bots
│   ├── telegram_bot.py
│   └── discord_bot.py
├── core/                   # Core configuration
│   ├── config.py           # Settings management
│   ├── database.py         # Database connection
│   ├── cache.py            # Redis cache
│   └── logging_config.py   # Logging setup
├── models/                 # Data models
│   ├── db_models.py        # SQLAlchemy models
│   └── schemas.py          # Pydantic schemas
├── services/               # Business logic
│   ├── opengradient_service.py
│   ├── model_service.py
│   ├── chat_service.py
│   ├── analytics_service.py
│   └── token_service.py
├── static/                 # Frontend files
│   ├── index.html          # Main UI
│   └── logos/              # Brand assets
├── tests/                  # Tests
│   ├── test_api.py
│   └── conftest.py
├── logs/                   # Application logs
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── docker-compose.yml      # Docker configuration
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - Database ORM
- **Asyncpg** - PostgreSQL async driver
- **SQLite** - Default database (no setup required)
- **Redis** - Optional caching layer

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Custom animations and gradients
- **HTML5** - Semantic markup

### AI/ML
- **OpenGradient LLM** - GROK-4-Fast for chat
- **TEE Verified** - Blockchain-verified inference

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Alembic** - Database migrations

## 🌐 API Endpoints

### Models
- `GET /api/models` - List all models
- `POST /api/models/search` - Search models
- `GET /api/models/{id}` - Get model by ID
- `GET /api/models/tasks` - Get categories
- `GET /api/models/authors` - Get authors
- `GET /api/models/tags` - Get tags

### Chat
- `POST /api/chat` - Send message
- `GET /api/chat/history/{session_id}` - Get history
- `GET /api/chat/sessions` - User sessions

### Analytics
- `GET /api/analytics/stats` - Global statistics
- `GET /api/analytics/queries/top` - Top queries
- `GET /api/analytics/models/popular` - Popular models

### Tokens (Free!)
- `GET /api/tokens/balance?user_id=xxx` - Get balance
- `POST /api/tokens/faucet/claim?user_id=xxx` - Auto-claim every 5h
- `GET /api/tokens/faucet/status?user_id=xxx` - Check status

### System
- `GET /api/health` - Health check
- `GET /api/sync/status` - Sync status
- `POST /api/sync/trigger` - Manual sync

## 💎 Token System

**Completely FREE!** No payment required.

- **10 tokens** - Welcome bonus on first visit
- **+5 tokens** - Auto-claimed every 5 hours
- **Unlimited usage** - Tokens shown but not deducted

Your wallet address: `0xfa13a15a2fb420e2313918496b5b05427ed8e31a`

## 🎨 Features Showcase

### AI Personas
Choose how the AI responds:
- 😊 **Friendly** - Warm and conversational
- 👔 **Professional** - Formal and precise
- 🎨 **Creative** - Imaginative and expressive
- ⚡ **Concise** - Brief and direct

### Quick Actions
One-click access to popular searches:
- 💎 DeFi Models
- 📝 NLP Models
- 🖼️ Vision Models
- 📊 Trading Models

### Gamification
- 🎯 Level system with XP
- 🏆 8 achievements to unlock
- 📊 Progress tracking

## 📖 Usage Examples

### Search for Models
```
"Find DeFi models for yield farming"
"Show me NLP models for text analysis"
"I need image classification models"
```

### Voice Search
Click the 🎤 button and speak:
"Show me trading prediction models"

### Upload Image
Click the 📷 button to upload an image for AI analysis.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# OpenGradient (optional)
PRIVATE_KEY=your_private_key_here

# Database (optional, uses SQLite by default)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/og_assistant

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000

# Bots (optional)
TELEGRAM_BOT_TOKEN=your_telegram_token
DISCORD_BOT_TOKEN=your_discord_token

# Sync
SYNC_INTERVAL_HOURS=24

# Logging
LOG_LEVEL=INFO
```

## 🔧 Troubleshooting

### Database Issues
```bash
# Reset database (SQLite)
rm og_assistant.db
python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001
```

### OpenGradient API Error
The app works without an API key using fallback responses. Add your key to `.env` for full functionality.

## 📄 License

MIT License - feel free to use this project for anything!

## 👨‍💻 Author

**Developed by [@graanit2](https://x.com/graanit2)**

Built with ❤️ using OpenGradient

## 🙏 Acknowledgments

- [OpenGradient](https://www.opengradient.ai/) for AI infrastructure
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [aiogram](https://docs.aiogram.dev/) for Telegram bot
- [discord.py](https://discordpy.readthedocs.io/) for Discord bot

## 📞 Support

- **Documentation**: `/docs` endpoint
- **Issues**: GitHub Issues
- **Discord**: [OpenGradient Discord](https://discord.gg/opengradient)
- **Twitter**: [@graanit2](https://x.com/graanit2)

---

**Star ⭐ this repo if you find it useful!**
