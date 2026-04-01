#!/usr/bin/env python3
"""
OpenClaw Configuration Module
Centralized configuration management with validation and defaults
"""

import os
from dataclasses import dataclass
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    bot_token: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    bot_name: str = os.getenv('TELEGRAM_BOT_NAME', '@openvlawbababab_bot')
    webhook_url: str = os.getenv('TELEGRAM_WEBHOOK_URL', 'http://192.168.0.140/telegram-webhook')
    webhook_port: int = int(os.getenv('TELEGRAM_WEBHOOK_PORT', '8787'))
    webhook_host: str = os.getenv('TELEGRAM_WEBHOOK_HOST', '127.0.0.1')
    api_timeout: int = int(os.getenv('TELEGRAM_API_TIMEOUT', '500'))
    allowed_users: List[int] = None
    admin_users: List[int] = None
    
    def __post_init__(self):
        """Parse user lists from environment"""
        if not self.allowed_users:
            users_str = os.getenv('TELEGRAM_ALLOWED_USERS', '')
            self.allowed_users = [int(u) for u in users_str.split(',') if u.strip()]
        
        if not self.admin_users:
            admins_str = os.getenv('TELEGRAM_ADMIN_USERS', '')
            self.admin_users = [int(a) for a in admins_str.split(',') if a.strip()]
    
    def is_valid(self) -> bool:
        """Validate Telegram configuration"""
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not configured")
            return False
        return True


@dataclass
class APIConfig:
    """API service configuration"""
    # Primary services
    groq_key: str = os.getenv('GROQ_API_KEY', '')
    elevenlabs_key: str = os.getenv('ELEVENLABS_API_KEY', '')
    openai_key: str = os.getenv('OPENAI_API_KEY', '')
    
    # Fallback services
    deepgram_key: str = os.getenv('DEEPGRAM_API_KEY', '')
    google_key: str = os.getenv('GOOGLE_API_KEY', '')
    azure_key: str = os.getenv('AZURE_SPEECH_KEY', '')
    azure_region: str = os.getenv('AZURE_SPEECH_REGION', 'eastus')
    
    def get_stt_provider(self) -> Optional[tuple]:
        """Get available speech-to-text provider with key"""
        if self.groq_key:
            return ('groq', self.groq_key)
        if self.deepgram_key:
            return ('deepgram', self.deepgram_key)
        if self.openai_key:
            return ('openai', self.openai_key)
        return None
    
    def get_tts_provider(self) -> Optional[tuple]:
        """Get available text-to-speech provider with key"""
        if self.elevenlabs_key:
            return ('elevenlabs', self.elevenlabs_key)
        if self.google_key:
            return ('google', self.google_key)
        if self.azure_key:
            return ('azure', self.azure_key)
        if self.openai_key:
            return ('openai', self.openai_key)
        return None


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = os.getenv('OPENCLAW_HOST', '192.168.0.140')
    port: int = int(os.getenv('OPENCLAW_PORT', '5000'))
    debug: bool = os.getenv('OPENCLAW_DEBUG', 'False').lower() == 'true'
    development_mode: bool = os.getenv('DEVELOPMENT_MODE', 'False').lower() == 'true'
    enable_api_docs: bool = os.getenv('ENABLE_API_DOCS', 'True').lower() == 'true'
    
    @property
    def api_base_url(self) -> str:
        """Construct API base URL"""
        return f"http://{self.host}:{self.port}"


@dataclass
class SecurityConfig:
    """Security configuration"""
    api_key: str = os.getenv('API_KEY', 'default-key-change-in-production')
    secret_key: str = os.getenv('SECRET_KEY', 'default-secret-change-in-production')
    jwt_secret: str = os.getenv('JWT_SECRET', 'default-jwt-secret-change-in-production')
    
    def is_secure(self) -> bool:
        """Check if security configuration is production-ready"""
        return (
            self.api_key != 'default-key-change-in-production' and
            self.secret_key != 'default-secret-change-in-production' and
            self.jwt_secret != 'default-jwt-secret-change-in-production'
        )


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = os.getenv('LOG_FILE', '/home/danijel-jd/.openclaw/openclaw.log')
    max_size: int = int(os.getenv('LOG_MAX_SIZE', '10485760'))
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))


@dataclass
class HealthConfig:
    """Health monitoring configuration"""
    check_interval: int = int(os.getenv('HEALTH_CHECK_INTERVAL', '60'))
    cpu_threshold: int = int(os.getenv('SYSTEM_ALERT_CPU_THRESHOLD', '80'))
    memory_threshold: int = int(os.getenv('SYSTEM_ALERT_MEMORY_THRESHOLD', '85'))
    disk_threshold: int = int(os.getenv('SYSTEM_ALERT_DISK_THRESHOLD', '80'))


class OpenClawConfig:
    """Main configuration manager"""
    
    def __init__(self):
        self.telegram = TelegramConfig()
        self.api = APIConfig()
        self.server = ServerConfig()
        self.security = SecurityConfig()
        self.logging_config = LoggingConfig()
        self.health = HealthConfig()
    
    def validate(self) -> bool:
        """Validate all configurations"""
        errors = []
        
        if not self.telegram.is_valid():
            errors.append("Invalid Telegram configuration")
        
        if not self.server.host or not self.server.port:
            errors.append("Invalid server configuration")
        
        if not self.security.is_secure() and self.server.debug:
            logger.warning("Using default security keys in debug mode")
        
        if errors:
            logger.error(f"Configuration validation errors: {', '.join(errors)}")
            return False
        
        logger.info("Configuration validated successfully")
        return True
    
    def to_dict(self) -> dict:
        """Export configuration as dictionary (safe, no secrets)"""
        return {
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'debug': self.server.debug,
                'url': self.server.api_base_url
            },
            'telegram': {
                'bot_name': self.telegram.bot_name,
                'webhook_port': self.telegram.webhook_port,
                'configured': self.telegram.is_valid()
            },
            'api': {
                'stt_provider': self.api.get_stt_provider()[0] if self.api.get_stt_provider() else None,
                'tts_provider': self.api.get_tts_provider()[0] if self.api.get_tts_provider() else None
            },
            'logging': {
                'level': self.logging_config.level,
                'file': self.logging_config.log_file
            }
        }


# Global config instance
config = OpenClawConfig()
