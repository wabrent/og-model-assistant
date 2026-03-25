"""
Telegram bot for OpenGradient Model Assistant.
"""
import asyncio
from typing import Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from core.config import settings
from services.opengradient_service import og_service
from services.model_service import model_service
from services.chat_service import chat_service
from core.database import async_session_maker


class TelegramBot:
    """Telegram bot for OpenGradient Model Assistant."""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self._running = False
    
    async def start(self):
        """Start the Telegram bot."""
        if not settings.telegram_bot_token:
            logger.warning("Telegram bot token not set, skipping bot startup")
            return
        
        try:
            self.bot = Bot(token=settings.telegram_bot_token)
            self.dp = Dispatcher()
            
            # Register handlers
            self._register_handlers()
            
            # Start polling
            self._running = True
            logger.info(f"Telegram bot started (@{(await self.bot.get_me()).username})")
            
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            self._running = False
    
    async def stop(self):
        """Stop the Telegram bot."""
        self._running = False
        if self.bot:
            await self.bot.session.close()
            await self.bot.close()
            logger.info("Telegram bot stopped")
    
    def _register_handlers(self):
        """Register message handlers."""
        self.dp.message(CommandStart())(self.cmd_start)
        self.dp.message(Command("help"))(self.cmd_help)
        self.dp.message(Command("search"))(self.cmd_search)
        self.dp.message(Command("stats"))(self.cmd_stats)
        self.dp.message(Command("random"))(self.cmd_random)
        self.dp.message(F.text)(self.handle_message)
    
    async def cmd_start(self, message: Message):
        """Handle /start command."""
        welcome_text = """
🤖 <b>OpenGradient Model Assistant</b>

Welcome! I'm your AI assistant for the OpenGradient Model Hub.

<b>What I can do:</b>
• 🔍 Search for AI models
• 💬 Chat about OpenGradient ecosystem
• 📊 Show statistics
• 🎲 Suggest random models

<b>Commands:</b>
• /search <query> - Search for models
• /stats - Show hub statistics
• /random - Get a random model
• /help - Show this help

Just send me a message and I'll help you find the perfect model!
        """.strip()
        
        await message.answer(
            welcome_text,
            parse_mode="HTML",
        )
    
    async def cmd_help(self, message: Message):
        """Handle /help command."""
        help_text = """
<b>Available Commands:</b>

/search <query> - Search for models by name, task, or description
/stats - Show statistics about the model hub
/random - Get a random model suggestion
/help - Show this help message

<b>Examples:</b>
• /search ETH price prediction
• /search text classification
• /stats

You can also just send me a message describing what you need!
        """.strip()
        
        await message.answer(help_text, parse_mode="HTML")
    
    async def cmd_search(self, message: Message):
        """Handle /search command."""
        query = message.text.split("/search", 1)[-1].strip()
        
        if not query:
            await message.answer(
                "❌ Please provide a search query.\n\nExample: <code>/search ETH price prediction</code>",
                parse_mode="HTML",
            )
            return
        
        # Send typing indicator
        await message.answer_chat_action("typing")
        
        try:
            async with async_session_maker() as session:
                # Search for models
                from models.schemas import ModelSearchRequest
                search_request = ModelSearchRequest(query=query, limit=5)
                models, total = await model_service.search_models(session, search_request)
            
            if not models:
                await message.answer(
                    f"❌ No models found for <b>\"{query}\"</b>\n\nTry different keywords!",
                    parse_mode="HTML",
                )
                return
            
            # Build results
            results = []
            for model in models[:5]:
                desc = (model.description or "")[:150]
                if len(model.description or "") > 150:
                    desc += "..."
                
                result = f"""
🔹 <b>{model.name}</b>
<b>Task:</b> <code>{model.task_name or "N/A"}</code>
<b>Author:</b> {model.author_username or "Anonymous"}

{desc}
                """.strip()
                results.append(result)
            
            response = f"🔍 Found <b>{total}</b> models for <b>\"{query}\"</b>:\n\n"
            response += "\n\n".join(results)
            response += f"\n\n🔗 <a href='https://hub.opengradient.ai/models'>View all on OpenGradient Hub</a>"
            
            await message.answer(response, parse_mode="HTML", disable_web_page_preview=True)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            await message.answer(f"❌ Search failed: {str(e)}")
    
    async def cmd_stats(self, message: Message):
        """Handle /stats command."""
        await message.answer_chat_action("typing")
        
        try:
            async with async_session_maker() as session:
                stats = await model_service.get_model_stats(session)
            
            stats_text = f"""
📊 <b>OpenGradient Model Hub Statistics</b>

📦 <b>Total Models:</b> {stats.get('total_models', 0)}
✅ <b>Active Models:</b> {stats.get('active_models', 0)}

<b>Top Categories:</b>
            """.strip()
            
            for task, count in list(stats.get('tasks', {}).items())[:5]:
                stats_text += f"\n• {task}: <b>{count}</b>"
            
            stats_text += "\n\n🔗 <a href='https://hub.opengradient.ai/models'>OpenGradient Hub</a>"
            
            await message.answer(stats_text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await message.answer(f"❌ Failed to get stats: {str(e)}")
    
    async def cmd_random(self, message: Message):
        """Handle /random command."""
        await message.answer_chat_action("typing")
        
        try:
            async with async_session_maker() as session:
                models, _ = await model_service.get_all_models(session, limit=50)
            
            if not models:
                await message.answer("❌ No models available!")
                return
            
            import random
            model = random.choice(models)
            
            desc = (model.description or "")[:300]
            if len(model.description or "") > 300:
                desc += "..."
            
            response = f"""
🎲 <b>Random Model Suggestion</b>

🔹 <b>{model.name}</b>
<b>Task:</b> <code>{model.task_name or "N/A"}</code>
<b>Author:</b> {model.author_username or "Anonymous"}

{desc}

🔗 <a href='https://hub.opengradient.ai/models'>View on OpenGradient Hub</a>
            """.strip()
            
            await message.answer(response, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Random error: {e}")
            await message.answer(f"❌ Failed to get random model: {str(e)}")
    
    async def handle_message(self, message: Message):
        """Handle regular messages."""
        # Send typing indicator
        await message.answer_chat_action("typing")
        
        try:
            async with async_session_maker() as session:
                # Use chat service for AI response
                from models.schemas import ChatRequest
                chat_request = ChatRequest(
                    message=message.text,
                    session_id=f"tg_{message.chat.id}",
                )
                
                result = await chat_service.chat(session, chat_request)
                
                response = result["reply"]
                
                # If models were suggested, add them
                if result.get("models_suggested"):
                    response += "\n\n🔍 <b>Suggested Models:</b>\n"
                    for model_name in result["models_suggested"][:5]:
                        response += f"• <code>{model_name}</code>\n"
                    response += "\n🔗 <a href='https://hub.opengradient.ai/models'>View on Hub</a>"
                
                await message.answer(response, parse_mode="HTML")
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            await message.answer(f"❌ Failed to process message: {str(e)}")


# Global bot instance
telegram_bot = TelegramBot()


async def start_telegram_bot():
    """Start Telegram bot in background."""
    await telegram_bot.start()


async def stop_telegram_bot():
    """Stop Telegram bot."""
    await telegram_bot.stop()
