"""
Telegram Bot Code and Configuration Generator
Automatically generates Python bot code based on specifications.
"""

import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class BotTemplate(Enum):
    """Available bot templates"""
    MINIMAL = "minimal"      # Just /start, /help, /status
    STANDARD = "standard"    # Standard automation bot
    ADVANCED = "advanced"    # Full-featured bot


@dataclass
class BotFeatures:
    """Bot feature set"""
    chat: bool = True
    commands: bool = True
    inline_mode: bool = False
    payments: bool = False
    admin_panel: bool = False
    automation: bool = False
    health_check: bool = False


class BotGenerator:
    """Generator for Telegram bot code and configurations"""
    
    MINIMAL_BOT_CODE = '''"""
Auto-generated Telegram Bot - Minimal Template
Created by OpenClaw Bot Creation Agent
"""

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"Willkommen {user.mention_html()}! 👋\\n"
        f"Ich bin ein OpenClaw-Bot.\\n"
        f"Nutze /help für verfügbare Befehle.",
        parse_mode="HTML"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
/start - Bot starten
/help - Diese Nachricht
/status - Bot-Status anzeigen
"""
    await update.message.reply_text(help_text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command"""
    await update.message.reply_text("✅ Bot läuft und ist bereit!")


def main() -> None:
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    
    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
'''
    
    STANDARD_BOT_CODE = '''"""
Auto-generated Telegram Bot - Standard Template
Created by OpenClaw Bot Creation Agent
"""

import logging
import os
import json
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = json.loads(os.getenv("ADMIN_IDS", "[]"))
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

# Conversation states
MENU, WAITING_INPUT = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command - Show main menu"""
    user = update.effective_user
    keyboard = [
        ["Status", "Hilfe"],
        ["Einstellungen", "Info"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Willkommen {user.mention_html()}! 👋\\n"
        f"Wähle eine Option:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return MENU


async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle menu button clicks"""
    choice = update.message.text
    
    if choice == "Status":
        await update.message.reply_text(
            "✅ Bot Status: Online\\n"
            f"⏰ Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
            "🟢 Alle Systeme aktiv"
        )
    elif choice == "Hilfe":
        await update.message.reply_text(
            "/start - Hauptmenü\\n"
            "/help - Hilfe\\n"
            "/status - Status\\n"
            "/settings - Einstellungen"
        )
    elif choice == "Einstellungen":
        await update.message.reply_text("Einstellungen sind derzeit verfügbar.")
    elif choice == "Info":
        await update.message.reply_text("Ich bin ein OpenClaw Automation Bot.")
    
    return MENU


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
*Verfügbare Befehle:*

/start - Hauptmenü anzeigen
/help - Diese Nachricht
/status - Bot-Status
/settings - Einstellungen
/cancel - Abbrechen
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel operation"""
    await update.message.reply_text(
        "Operation abgebrochen.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    """Start the bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    
    # Run the bot
    application.run_polling()


if __name__ == '__main__':
    main()
'''
    
    @staticmethod
    def generate_python_code(
        bot_name: str,
        description: str,
        features: BotFeatures,
        template: BotTemplate = BotTemplate.STANDARD,
        commands: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate Python bot code based on template and features.
        
        Args:
            bot_name: Bot name
            description: Bot description
            features: Feature set
            template: Code template to use
            commands: List of commands with descriptions
            
        Returns:
            Generated Python code
        """
        if template == BotTemplate.MINIMAL:
            return BotGenerator.MINIMAL_BOT_CODE
        elif template == BotTemplate.STANDARD:
            return BotGenerator.STANDARD_BOT_CODE
        else:
            return BotGenerator.STANDARD_BOT_CODE
    
    @staticmethod
    def generate_config_json(
        token: str,
        bot_id: int,
        bot_name: str,
        description: str,
        webhook_url: str = "",
        webhook_secret: str = "",
        commands: List[Dict[str, str]] = None,
        admin_ids: List[int] = None
    ) -> str:
        """Generate configuration JSON for the bot"""
        config = {
            "bot": {
                "token": token,
                "bot_id": bot_id,
                "bot_name": bot_name,
                "description": description,
                "created_at": datetime.now().isoformat()
            },
            "webhook": {
                "enabled": bool(webhook_url),
                "url": webhook_url,
                "secret": webhook_secret,
                "port": 8443
            },
            "commands": commands or [
                {"command": "start", "description": "Start the bot"},
                {"command": "help", "description": "Show help"}
            ],
            "admin": {
                "ids": admin_ids or [],
                "notifications_enabled": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/bot.log"
            },
            "features": {
                "chat": True,
                "commands": True,
                "inline_mode": False,
                "payments": False
            }
        }
        return json.dumps(config, ensure_ascii=False, indent=2)
    
    @staticmethod
    def generate_requirements_txt(
        include_advanced: bool = False,
        include_payments: bool = False
    ) -> str:
        """Generate requirements.txt file"""
        requirements = [
            "python-telegram-bot>=20.0",
            "python-dotenv>=0.19.0",
            "aiohttp>=3.8.0",
        ]
        
        if include_advanced:
            requirements.extend([
                "asyncpg>=0.27.0",
                "redis>=4.0.0",
            ])
        
        if include_payments:
            requirements.append("stripe>=5.0.0")
        
        return "\\n".join(requirements)
    
    @staticmethod
    def generate_dockerfile(
        bot_name: str,
        python_version: str = "3.10"
    ) -> str:
        """Generate Dockerfile for the bot"""
        return f'''FROM python:{python_version}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run bot
CMD ["python", "{bot_name.lower().replace(' ', '_')}.py"]
'''
    
    @staticmethod
    def generate_systemd_service(
        bot_name: str,
        bot_path: str = "/opt/bots",
        user: str = "bot"
    ) -> str:
        """Generate systemd service file"""
        service_name = bot_name.lower().replace(" ", "_")
        return f'''[Unit]
Description={bot_name} Telegram Bot
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={bot_path}/{service_name}
ExecStart=/usr/bin/python3 {bot_path}/{service_name}/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
EnvironmentFile={bot_path}/{service_name}/.env

[Install]
WantedBy=multi-user.target
'''
    
    @staticmethod
    def generate_env_template(
        bot_id: int,
        webhook_url: str = "",
        admin_ids: List[int] = None
    ) -> str:
        """Generate .env template file"""
        admin_ids_str = json.dumps(admin_ids or [])
        return f'''# {bot_id} Telegram Bot Configuration
# Generated by OpenClaw Bot Creation Agent

# Telegram Bot Token (from @BotFather)
TELEGRAM_BOT_TOKEN=your_token_here

# Bot Configuration
BOT_ID={bot_id}
BOT_NAME=your_bot_name
BOT_DESCRIPTION="Your bot description"

# Webhook Configuration
WEBHOOK_ENABLED=false
WEBHOOK_URL={webhook_url}
WEBHOOK_SECRET=your_secret_key_here
WEBHOOK_PORT=8443

# Admin Configuration
ADMIN_IDS={admin_ids_str}

# Database (optional)
DATABASE_URL=

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# API Keys
GROQ_API_KEY=
OPENAI_API_KEY=

# Features
ENABLE_INLINE_MODE=false
ENABLE_PAYMENTS=false
ENABLE_HEALTH_CHECK=true
'''


def generate_bot_project(
    bot_name: str,
    description: str,
    token: str,
    bot_id: int,
    template: BotTemplate = BotTemplate.STANDARD,
    webhook_url: str = "",
    admin_ids: List[int] = None
) -> Dict[str, str]:
    """
    Generate complete bot project files.
    
    Returns:
        Dictionary with filename -> content
    """
    gen = BotGenerator()
    
    files = {
        "main.py": gen.generate_python_code(
            bot_name, description, BotFeatures(), template
        ),
        "config.json": gen.generate_config_json(
            token, bot_id, bot_name, description, webhook_url, admin_ids=admin_ids
        ),
        "requirements.txt": gen.generate_requirements_txt(),
        "Dockerfile": gen.generate_dockerfile(bot_name),
        ".env.example": gen.generate_env_template(bot_id, webhook_url, admin_ids),
        f"{bot_name.lower().replace(' ', '_')}.service": gen.generate_systemd_service(bot_name),
    }
    
    return files


if __name__ == "__main__":
    # Test generator
    files = generate_bot_project(
        bot_name="TestBot",
        description="A test bot",
        token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        bot_id=123456789,
        template=BotTemplate.STANDARD
    )
    
    for filename, content in files.items():
        print(f"\\n{'='*60}")
        print(f"FILE: {filename}")
        print(f"{'='*60}")
        print(content[:300] + "..." if len(content) > 300 else content)
    
    print(f"\\n✅ Generated {len(files)} files!")
