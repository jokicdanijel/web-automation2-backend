#!/usr/bin/env python3
"""
OpenClaw Telegram Bot - Refactored
Simplified bot initialization with modular handler architecture
"""

import logging
import signal
import sys
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from config import OpenClawConfig, config
from handlers import CommandHandlers, MessageHandlers, CallbackHandlers, MessageStore
from ai_service import AIServiceFactory

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class OpenClawBot:
    """Refactored OpenClaw Telegram Bot"""
    
    def __init__(self, config: OpenClawConfig):
        """
        Initialize bot with configuration
        
        Args:
            config: OpenClawConfig instance
        """
        self.config = config
        self.app: Optional[Application] = None
        self.running = False
        
        # Initialize components
        self.message_store = MessageStore(max_history=10)
        self.ai_service = AIServiceFactory.create(config)
        self.message_handlers = MessageHandlers(self.message_store)
    
    def setup_handlers(self) -> None:
        """Setup all Telegram message and command handlers"""
        if not self.app:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", CommandHandlers.start))
        self.app.add_handler(CommandHandler("help", CommandHandlers.help_command))
        self.app.add_handler(CommandHandler("status", CommandHandlers.status))
        self.app.add_handler(CommandHandler("health", CommandHandlers.health))
        
        # Message handlers
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self._handle_text_wrapper
        ))
        self.app.add_handler(MessageHandler(
            filters.VOICE, 
            self._handle_voice_wrapper
        ))
        
        # Callback handler
        self.app.add_handler(CallbackQueryHandler(CallbackHandlers.handle_callback))
        
        # Error handler
        self.app.add_error_handler(self._error_handler)
        
        logger.info("All handlers registered")
    
    async def _handle_text_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Wrapper for text message handling with AI integration"""
        await self.message_handlers.handle_text_message(
            update, 
            context, 
            self.ai_service.get_chat_response
        )
    
    async def _handle_voice_wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Wrapper for voice message handling with transcription"""
        await self.message_handlers.handle_voice_message(
            update,
            context,
            self.ai_service.transcribe_audio
        )
    
    async def _error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log telegram errors"""
        logger.warning(f"Update {update} caused error {context.error}")
    
    def initialize(self) -> bool:
        """
        Initialize bot application
        
        Returns:
            True if successful, False otherwise
        """
        if not self.config.validate():
            logger.error("Configuration validation failed")
            return False
        
        if not self.config.telegram.is_valid():
            logger.error("Telegram configuration invalid")
            return False
        
        try:
            self.app = Application.builder().token(
                self.config.telegram.bot_token
            ).build()
            
            self.setup_handlers()
            logger.info("Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}", exc_info=True)
            return False
    
    async def start(self) -> None:
        """Start the bot (async)"""
        if not self.app:
            if not self.initialize():
                raise RuntimeError("Failed to initialize bot")
        
        self.running = True
        logger.info("Starting OpenClaw Telegram Bot...")
        
        try:
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            
            logger.info("Bot is running (polling)...")
            
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error during bot execution: {e}", exc_info=True)
            raise
    
    async def stop(self) -> None:
        """Stop the bot gracefully"""
        logger.info("Stopping bot...")
        self.running = False
        
        if self.app:
            try:
                await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()
                logger.info("Bot stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping bot: {e}", exc_info=True)
    
    def run_sync(self) -> None:
        """Run bot synchronously (blocking)"""
        import asyncio
        
        try:
            logger.info("Starting OpenClaw Telegram Bot (sync mode)")
            
            if not self.initialize():
                logger.error("Failed to initialize bot")
                sys.exit(1)
            
            # Run polling
            self.app.run_polling()
            
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Log configuration
    logger.info(f"Configuration: {config.to_dict()}")
    
    # Create and run bot
    bot = OpenClawBot(config)
    bot.run_sync()


if __name__ == '__main__':
    main()
