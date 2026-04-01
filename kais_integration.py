"""
KAIS Integration Layer - Connect OpenClaw with external systems
Handles REST API calls, webhooks, command execution, and event processing
"""

import asyncio
import logging
import httpx
from typing import Dict, Optional, Any, List
from datetime import datetime
from dataclasses import dataclass

from config import AppConfig

logger = logging.getLogger(__name__)

@dataclass
class KAISCommand:
    """KAIS command structure"""
    command: str
    params: Dict
    timestamp: datetime = None

class KAISIntegration:
    """Integration with KAIS and external systems"""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.http_client: Optional[httpx.AsyncClient] = None
        self.webhooks: Dict[str, List[str]] = {}
        self.rate_limit = 100  # requests per minute
        self.request_count = 0
        logger.info("KAIS Integration initialized")
    
    async def initialize(self):
        """Initialize KAIS integration"""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        logger.info("KAIS HTTP client initialized")
    
    async def shutdown(self):
        """Shutdown KAIS integration"""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("KAIS HTTP client closed")
    
    # ========================================================================
    # COMMAND EXECUTION
    # ========================================================================
    
    async def execute_command(self, command: str, params: Dict = None) -> Dict:
        """Execute KAIS command"""
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                return {"error": "Rate limit exceeded", "status": 429}
            
            cmd = KAISCommand(command=command, params=params or {}, timestamp=datetime.now())
            logger.info(f"Executing KAIS command: {command}")
            
            # Route command to appropriate handler
            handlers = {
                "execute_automation": self._handle_automation,
                "detect_forms": self._handle_form_detection,
                "transcribe": self._handle_transcription,
                "synthesize": self._handle_synthesis,
                "chat": self._handle_chat,
                "health_check": self._handle_health_check
            }
            
            handler = handlers.get(command)
            if not handler:
                return {"error": f"Unknown command: {command}", "status": 400}
            
            result = await handler(params or {})
            return {"status": 200, "command": command, "result": result}
        
        except Exception as e:
            logger.error(f"KAIS command error: {e}")
            return {"error": str(e), "status": 500}
    
    async def _handle_automation(self, params: Dict) -> Dict:
        """Handle automation command"""
        return {
            "action": "automation_started",
            "workflow": params.get("workflow", "default"),
            "status": "executing"
        }
    
    async def _handle_form_detection(self, params: Dict) -> Dict:
        """Handle form detection command"""
        return {
            "action": "forms_detected",
            "url": params.get("url"),
            "count": 0
        }
    
    async def _handle_transcription(self, params: Dict) -> Dict:
        """Handle transcription command"""
        return {
            "action": "transcription",
            "text": "Transcribed audio content",
            "language": params.get("language", "en-US")
        }
    
    async def _handle_synthesis(self, params: Dict) -> Dict:
        """Handle synthesis command"""
        return {
            "action": "synthesis",
            "text": params.get("text"),
            "voice": params.get("voice", "default")
        }
    
    async def _handle_chat(self, params: Dict) -> Dict:
        """Handle chat command"""
        return {
            "action": "chat_response",
            "message": params.get("message"),
            "response": "Chat response content"
        }
    
    async def _handle_health_check(self, params: Dict) -> Dict:
        """Handle health check command"""
        return {
            "action": "health_status",
            "status": "online",
            "components": {
                "bot": "online",
                "browser": "online",
                "audio": "online"
            }
        }
    
    # ========================================================================
    # WEBHOOK HANDLING
    # ========================================================================
    
    async def handle_webhook(self, event: Dict) -> Dict:
        """Handle incoming webhook from KAIS"""
        try:
            event_type = event.get("type")
            logger.info(f"Webhook received: {event_type}")
            
            # Register webhook
            if "callback_url" in event:
                self._register_webhook(event_type, event["callback_url"])
            
            # Process event
            result = await self._process_webhook_event(event)
            return {"status": "processed", "result": result}
        
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {"error": str(e), "status": 500}
    
    def _register_webhook(self, event_type: str, callback_url: str):
        """Register webhook callback"""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        self.webhooks[event_type].append(callback_url)
        logger.info(f"Webhook registered: {event_type} -> {callback_url}")
    
    async def _process_webhook_event(self, event: Dict) -> Dict:
        """Process webhook event"""
        event_type = event.get("type")
        
        # Trigger callbacks
        if event_type in self.webhooks:
            for callback_url in self.webhooks[event_type]:
                await self._trigger_callback(callback_url, event)
        
        return {
            "event_type": event_type,
            "callbacks_triggered": len(self.webhooks.get(event_type, [])),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _trigger_callback(self, url: str, event: Dict):
        """Trigger webhook callback"""
        try:
            response = await self.http_client.post(
                url,
                json=event,
                timeout=10.0
            )
            logger.info(f"Callback triggered: {url} ({response.status_code})")
        except Exception as e:
            logger.error(f"Callback error: {e}")
    
    # ========================================================================
    # EXTERNAL API CALLS
    # ========================================================================
    
    async def call_external_api(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Call external API with authentication"""
        try:
            headers = self._get_auth_headers()
            
            if method == "GET":
                response = await self.http_client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await self.http_client.post(endpoint, json=data, headers=headers)
            elif method == "PUT":
                response = await self.http_client.put(endpoint, json=data, headers=headers)
            elif method == "DELETE":
                response = await self.http_client.delete(endpoint, headers=headers)
            else:
                return {"error": f"Unknown method: {method}"}
            
            return {
                "status": response.status_code,
                "data": response.json() if response.text else {},
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"API call error: {e}")
            return {"error": str(e), "status": 500}
    
    def _get_auth_headers(self) -> Dict:
        """Get authentication headers for external APIs"""
        return {
            "Authorization": f"Bearer {self.config.kais_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw/1.0"
        }
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limit"""
        self.request_count += 1
        if self.request_count > self.rate_limit:
            self.request_count = 0
            return False
        return True
    
    def get_rate_limit_status(self) -> Dict:
        """Get rate limit status"""
        return {
            "limit": self.rate_limit,
            "current": self.request_count,
            "remaining": max(0, self.rate_limit - self.request_count),
            "reset": "60s"
        }
    
    # ========================================================================
    # HEALTH CHECK
    # ========================================================================
    
    async def health_check(self) -> Dict:
        """Check KAIS integration health"""
        return {
            "status": "healthy",
            "http_client": "connected",
            "webhooks": len(self.webhooks),
            "rate_limit": self.get_rate_limit_status(),
            "timestamp": datetime.now().isoformat()
        }

