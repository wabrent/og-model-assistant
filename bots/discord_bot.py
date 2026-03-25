"""
Discord bot for OpenGradient Model Assistant.
"""
import asyncio
from typing import Optional
import discord
from discord import app_commands
from discord.ext import tasks
from loguru import logger

from core.config import settings
from services.opengradient_service import og_service
from services.model_service import model_service
from services.chat_service import chat_service
from core.database import async_session_maker
from models.schemas import ModelSearchRequest, ChatRequest


class OpenGradientBot(discord.Client):
    """Discord bot for OpenGradient Model Assistant."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self._running = False
    
    async def setup_hook(self):
        """Setup bot after login."""
        logger.info("Discord bot setup hook called")
        
        # Register commands
        self.tree.add_command(self.search_command)
        self.tree.add_command(self.stats_command)
        self.tree.add_command(self.random_command)
        self.tree.add_command(self.help_command)
        
        # Sync commands
        await self.tree.sync()
        logger.info("Discord commands synced")
    
    async def start_bot(self, token: str):
        """Start the Discord bot."""
        if not token:
            logger.warning("Discord bot token not set, skipping bot startup")
            return
        
        try:
            self._running = True
            await self.start(token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            self._running = False
    
    async def stop_bot(self):
        """Stop the Discord bot."""
        self._running = False
        await self.close()
        logger.info("Discord bot stopped")
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Discord bot logged in as {self.user.name} ({self.user.id})")
    
    # Slash Commands
    
    @app_commands.command(name="search", description="Search for AI models on OpenGradient Hub")
    @app_commands.describe(query="What are you looking for? (e.g., 'ETH price prediction')")
    async def search_command(self, interaction: discord.Interaction, query: str):
        """Search for models."""
        await interaction.response.defer()
        
        try:
            async with async_session_maker() as session:
                search_request = ModelSearchRequest(query=query, limit=5)
                models, total = await model_service.search_models(session, search_request)
            
            if not models:
                await interaction.followup.send(
                    f"❌ No models found for **{query}**\n\nTry different keywords!",
                    ephemeral=True,
                )
                return
            
            embeds = []
            for model in models[:5]:
                desc = (model.description or "")[:500]
                if len(model.description or "") > 500:
                    desc += "..."
                
                embed = discord.Embed(
                    title=f"🔹 {model.name}",
                    description=desc or "No description available",
                    color=discord.Color.green(),
                )
                embed.add_field(name="Task", value=model.task_name or "N/A", inline=True)
                embed.add_field(name="Author", value=model.author_username or "Anonymous", inline=True)
                embed.set_footer(text=f"Found {total} models total")
                
                embeds.append(embed)
            
            # Add link to hub
            view = discord.View()
            view.add_item(
                discord.ui.Button(
                    label="View on OpenGradient Hub",
                    url="https://hub.opengradient.ai/models",
                    style=discord.ButtonStyle.link,
                )
            )
            
            await interaction.followup.send(
                f"🔍 Found **{total}** models for **{query}**:",
                embeds=embeds,
                view=view,
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            await interaction.followup.send(f"❌ Search failed: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="stats", description="Show OpenGradient Model Hub statistics")
    async def stats_command(self, interaction: discord.Interaction):
        """Show hub statistics."""
        await interaction.response.defer()
        
        try:
            async with async_session_maker() as session:
                stats = await model_service.get_model_stats(session)
            
            embed = discord.Embed(
                title="📊 OpenGradient Model Hub Statistics",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="📦 Models",
                value=f"Total: {stats.get('total_models', 0)}\nActive: {stats.get('active_models', 0)}",
                inline=True,
            )
            
            # Top categories
            tasks = stats.get('tasks', {})
            if tasks:
                top_tasks = "\n".join([f"{k}: {v}" for k, v in list(tasks.items())[:5]])
                embed.add_field(name="🏷️ Top Categories", value=top_tasks, inline=False)
            
            # Top authors
            authors = stats.get('top_authors', {})
            if authors:
                top_authors = "\n".join([f"{k}: {v}" for k, v in list(authors.items())[:5]])
                embed.add_field(name="👥 Top Authors", value=top_authors, inline=False)
            
            embed.set_footer(text="OpenGradient Model Assistant")
            
            view = discord.View()
            view.add_item(
                discord.ui.Button(
                    label="OpenGradient Hub",
                    url="https://hub.opengradient.ai/models",
                    style=discord.ButtonStyle.link,
                )
            )
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Stats error: {e}")
            await interaction.followup.send(f"❌ Failed to get stats: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="random", description="Get a random model suggestion")
    async def random_command(self, interaction: discord.Interaction):
        """Get a random model."""
        await interaction.response.defer()
        
        try:
            async with async_session_maker() as session:
                models, _ = await model_service.get_all_models(session, limit=50)
            
            if not models:
                await interaction.followup.send("❌ No models available!", ephemeral=True)
                return
            
            import random
            model = random.choice(models)
            
            desc = (model.description or "")[:500]
            if len(model.description or "") > 500:
                desc += "..."
            
            embed = discord.Embed(
                title=f"🎲 Random Model: {model.name}",
                description=desc or "No description available",
                color=discord.Color.gold(),
            )
            embed.add_field(name="Task", value=model.task_name or "N/A", inline=True)
            embed.add_field(name="Author", value=model.author_username or "Anonymous", inline=True)
            
            view = discord.View()
            view.add_item(
                discord.ui.Button(
                    label="View on Hub",
                    url="https://hub.opengradient.ai/models",
                    style=discord.ButtonStyle.link,
                )
            )
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Random error: {e}")
            await interaction.followup.send(f"❌ Failed: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="help", description="Show help information")
    async def help_command(self, interaction: discord.Interaction):
        """Show help."""
        embed = discord.Embed(
            title="🤖 OpenGradient Model Assistant Help",
            description="Your AI assistant for finding models on OpenGradient Hub",
            color=discord.Color.green(),
        )
        
        embed.add_field(
            name="/search",
            value="Search for models by query\nExample: `/search ETH price prediction`",
            inline=False,
        )
        embed.add_field(
            name="/stats",
            value="Show hub statistics",
            inline=False,
        )
        embed.add_field(
            name="/random",
            value="Get a random model suggestion",
            inline=False,
        )
        
        embed.set_footer(text="OpenGradient Model Assistant")
        
        await interaction.response.send_message(embed=embed)
    
    async def on_message(self, message: discord.Message):
        """Handle regular messages (optional AI chat)."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Only respond if bot is mentioned
        if not self.user.mentioned_in(message):
            return
        
        await message.channel.typing()
        
        try:
            # Get message content without mention
            content = message.content.replace(f"<@{self.user.id}>", "").strip()
            content = content.replace(f"<@!{self.user.id}>", "").strip()
            
            if not content:
                await message.channel.send("👋 Hey! Use `/search`, `/stats`, `/random`, or `/help` to interact with me!")
                return
            
            async with async_session_maker() as session:
                chat_request = ChatRequest(
                    message=content,
                    session_id=f"discord_{message.channel.id}",
                )
                result = await chat_service.chat(session, chat_request)
            
            response = result["reply"]
            
            # Truncate if too long
            if len(response) > 2000:
                response = response[:1997] + "..."
            
            await message.channel.send(response)
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            await message.channel.send(f"❌ Failed to process message: {str(e)}")


# Global bot instance
discord_bot: Optional[OpenGradientBot] = None


async def start_discord_bot():
    """Start Discord bot in background."""
    global discord_bot
    
    if not settings.discord_bot_token:
        logger.warning("Discord bot token not set, skipping bot startup")
        return
    
    discord_bot = OpenGradientBot()
    await discord_bot.start_bot(settings.discord_bot_token)


async def stop_discord_bot():
    """Stop Discord bot."""
    global discord_bot
    if discord_bot:
        await discord_bot.stop_bot()
