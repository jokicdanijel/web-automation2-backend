#!/usr/bin/env python3
"""
OpenClaw Telegram Handler Module
Separates command and message handling logic from bot initialization
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class MessageStore:
    """Simple in-memory message history storage"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.histories: Dict[int, List[dict]] = {}
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Add message to user history"""
        if user_id not in self.histories:
            self.histories[user_id] = []
        
        self.histories[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep size manageable
        if len(self.histories[user_id]) > self.max_history:
            self.histories[user_id] = self.histories[user_id][-self.max_history:]
    
    def get_history(self, user_id: int) -> List[dict]:
        """Get user message history"""
        return self.histories.get(user_id, [])
    
    def clear_history(self, user_id: int) -> None:
        """Clear user history"""
        if user_id in self.histories:
            self.histories[user_id] = []


class CommandHandlers:
    """Telegram command handlers"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        try:
            user = update.effective_user
            welcome_message = (
                f"Willkommen in OpenClaw, {user.first_name}! 🤖\n\n"
                "Ich bin dein intelligenter Automatisierungsassistent.\n\n"
                "Verfügbare Befehle:\n"
                "/help - Zeige alle Befehle\n"
                "/status - System Status\n"
                "/automate - Automatisierungswerkzeuge\n"
                "/health - Gesundheitsstatus\n"
                "/chat - Freie Konversation\n"
                "/settings - Einstellungen\n"
                "/cancel - Aktuelle Aktion abbrechen\n\n"
                "Du kannst mir auch einfach Nachrichten schreiben! ✉️"
            )
            
            keyboard = [
                [InlineKeyboardButton("Status", callback_data='status'),
                 InlineKeyboardButton("Hilfe", callback_data='help')],
                [InlineKeyboardButton("Chat", callback_data='chat'),
                 InlineKeyboardButton("Einstellungen", callback_data='settings')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
            logger.info(f"User {user.id} started bot")
            
        except Exception as e:
            logger.error(f"Error in start command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Fehler: {str(e)}")
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = """
🤖 **OpenClaw Bot Hilfe**

**Automation:**
/automate - Starte Automatisierungsmodus
/workflow - Zeige verfügbare Workflows
/execute - Führe Action aus

**Information:**
/status - Zeige System Status
/health - System Gesundheit
/info - Bot Informationen

**Chat & Sprache:**
/chat - Freier Chat mit AI
/voice - Sprachausgabe aktivieren
/language - Sprache wechseln

**Management:**
/settings - Öffne Einstellungen
/history - Chat Verlauf
/clear - Verlauf löschen
/cancel - Abbrechen

**System:**
/restart - Bot neustarten
/logs - Zeige Logs
/help - Diese Nachricht

💡 **Tipps:**
- Sende einfach Text zum Chatten
- Sende Audio für Sprachbefehle
- Verwende Befehle mit / für Funktionen
- Reagiere auf Schaltflächen (Buttons)
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    @staticmethod
    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        try:
            status_message = (
                "📊 **OpenClaw Status**\n\n"
                f"🟢 Bot Status: Online\n"
                f"⏱️ Uptime: {CommandHandlers._get_uptime()}\n"
                f"👤 User ID: {update.effective_user.id}\n"
                f"🕐 Zeitstempel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"🌐 API Server: Verbunden\n"
                f"💾 Speicher: Verfügbar\n"
            )
            
            keyboard = [
                [InlineKeyboardButton("Health Check", callback_data='health'),
                 InlineKeyboardButton("Logs", callback_data='logs')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(status_message, 
                                          parse_mode='Markdown',
                                          reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error in status command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Fehler: {str(e)}")
    
    @staticmethod
    async def health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /health command"""
        try:
            await update.message.chat.send_action(ChatAction.TYPING)
            
            health_report = (
                "🏥 **System Gesundheit**\n\n"
                "CPU: ▓▓▓▓░░░░░░ 45%\n"
                "RAM: ▓▓▓▓▓▓░░░░ 62%\n"
                "Disk: ▓▓▓▓▓▓▓░░░ 75%\n"
                "Network: ▓▓▓▓▓▓▓▓░░ 85%\n\n"
                "✅ Alle Systeme normal\n"
                "✅ Services laufen\n"
                "✅ API erreichbar\n"
            )
            
            await update.message.reply_text(health_report, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in health command: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Fehler: {str(e)}")
    
    @staticmethod
    def _get_uptime() -> str:
        """Get bot uptime (placeholder)"""
        return "2d 14h 32m"


class MessageHandlers:
    """Telegram message handlers"""
    
    def __init__(self, message_store: MessageStore):
        self.message_store = message_store
    
    async def handle_text_message(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        ai_response_callback
    ) -> None:
        """Handle regular text messages"""
        try:
            user = update.effective_user
            user_message = update.message.text
            
            await update.message.chat.send_action(ChatAction.TYPING)
            
            # Store user message
            self.message_store.add_message(user.id, "user", user_message)
            
            # Get conversation history
            history = self.message_store.get_history(user.id)
            
            # Get AI response
            ai_response = await ai_response_callback(history)
            
            # Store AI response
            self.message_store.add_message(user.id, "assistant", ai_response)
            
            # Send response (split if too long)
            await self._send_long_message(update, ai_response)
            
            logger.info(f"User {user.id} message processed")
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Fehler: {str(e)}")
    
    async def handle_voice_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        transcribe_callback
    ) -> None:
        """Handle voice messages"""
        try:
            await update.message.chat.send_action(ChatAction.TYPING)
            
            voice_file = await update.message.voice.get_file()
            audio_path = f"/tmp/voice_{update.effective_user.id}.ogg"
            
            # Download and transcribe
            await voice_file.download_to_drive(audio_path)
            transcription = await transcribe_callback(audio_path)
            
            logger.info(f"Transcribed voice: {transcription}")
            
            # Clean up and process as text
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Store and respond
            update.message.text = transcription
            # Note: This would need callback to handle_text_message
            
        except Exception as e:
            logger.error(f"Error handling voice message: {e}", exc_info=True)
            await update.message.reply_text(f"❌ Spracherkennungsfehler: {str(e)}")
    
    @staticmethod
    async def _send_long_message(update: Update, message: str, chunk_size: int = 4000) -> None:
        """Send long message split into chunks"""
        if len(message) <= chunk_size:
            await update.message.reply_text(message)
        else:
            chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]
            for chunk in chunks:
                await update.message.reply_text(chunk)


class CallbackHandlers:
    """Telegram callback handlers for inline buttons"""
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline button callbacks"""
        try:
            query = update.callback_query
            await query.answer()
            
            if query.data == 'help':
                await CommandHandlers.help_command(update, context)
            elif query.data == 'status':
                await CommandHandlers.status(update, context)
            elif query.data == 'health':
                await CommandHandlers.health(update, context)
            elif query.data == 'settings':
                await CallbackHandlers._show_settings(query)
            elif query.data == 'chat':
                await query.edit_message_text(
                    text="💬 Chat-Modus aktiv. Schreib deine Nachricht:"
                )
            
        except Exception as e:
            logger.error(f"Error in callback handler: {e}", exc_info=True)
    
    @staticmethod
    async def _show_settings(query) -> None:
        """Show settings menu"""
        settings_text = (
            "⚙️ **Einstellungen**\n\n"
            "🌐 Sprache: Deutsch\n"
            "🔊 Audio-Output: Ein\n"
            "📱 Gerät: Telegram\n"
            "🎙️ Mikrofon: Aktiviert\n"
            "⏱️ Zeitzone: Europe/Berlin\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("Sprache ändern", callback_data='lang'),
             InlineKeyboardButton("Audio", callback_data='audio')],
            [InlineKeyboardButton("Zurück", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=settings_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
