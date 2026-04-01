#!/usr/bin/env python3
"""
OpenClaw AI Service Module
Handles all AI interactions (chat, transcription)
"""

import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class AIService:
    """Main AI service for chat and transcription"""
    
    def __init__(self, openai_client=None, system_prompt_provider=None):
        """
        Initialize AI Service
        
        Args:
            openai_client: OpenAI API client
            system_prompt_provider: Callable that returns system prompt
        """
        self.openai = openai_client
        self.system_prompt_provider = system_prompt_provider
    
    async def get_chat_response(
        self, 
        conversation_history: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Get AI response for chat conversation
        
        Args:
            conversation_history: List of message dicts with role/content
            model: OpenAI model to use
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            
        Returns:
            AI response text
        """
        if not self.openai:
            return "OpenAI not configured. Please set OPENAI_API_KEY environment variable."
        
        try:
            # Get system prompt
            system_prompt = (
                self.system_prompt_provider() 
                if self.system_prompt_provider
                else "Du bist ein hilfreicher OpenClaw Automation Assistant."
            )
            
            # Build messages with system prompt
            messages = [
                {"role": "system", "content": system_prompt},
                *conversation_history
            ]
            
            # Call OpenAI API
            response = self.openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return f"❌ AI Error: {str(e)}"
    
    async def transcribe_audio(
        self,
        audio_path: str,
        language: str = "de"
    ) -> Optional[str]:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (default German)
            
        Returns:
            Transcribed text or None on error
        """
        if not self.openai:
            logger.warning("OpenAI not configured for transcription")
            return None
        
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.openai.Audio.transcribe(
                    "whisper-1",
                    audio_file,
                    language=language
                )
            
            return transcript.get('text', '')
            
        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_path}")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return None


class AIServiceFactory:
    """Factory for creating AI service instances"""
    
    @staticmethod
    def create(config) -> AIService:
        """
        Create AI service with configuration
        
        Args:
            config: OpenClawConfig instance
            
        Returns:
            Configured AIService instance
        """
        openai_client = None
        system_prompt_fn = None
        
        # Initialize OpenAI if configured
        if config.api.openai_key:
            try:
                import openai
                openai.api_key = config.api.openai_key
                openai_client = openai
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("openai package not installed")
        
        # Initialize system prompt provider
        try:
            from system_prompt import get_telegram_handler_prompt
            system_prompt_fn = get_telegram_handler_prompt
            logger.info("System prompt provider initialized")
        except ImportError:
            logger.warning("system_prompt module not found")
        
        return AIService(openai_client, system_prompt_fn)
