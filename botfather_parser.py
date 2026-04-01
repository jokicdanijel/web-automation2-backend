"""
BotFather Response Parser and Handler
Parses BotFather responses and extracts critical bot information.
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any
from enum import Enum


class BotFatherAction(Enum):
    """Enumeration of BotFather actions"""
    CREATE_BOT = "newbot"
    SET_COMMANDS = "setcommands"
    SET_DESCRIPTION = "setdescription"
    SET_WEBHOOK = "setwebhook"
    DELETE_WEBHOOK = "deletewebhook"
    GET_WEBHOOK_INFO = "getwebhookinfo"
    SET_PRIVACY = "setprivacy"
    SET_INLINE = "setinlinequeries"
    SET_PIC = "setuserpic"
    GET_BOT_INFO = "getmyinfo"


@dataclass
class BotToken:
    """Extracted bot token information"""
    token: str
    bot_id: str
    bot_name: str
    is_bot: bool
    first_name: str
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BotCommand:
    """Bot command definition"""
    command: str
    description: str
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BotConfiguration:
    """Complete bot configuration"""
    token: str
    bot_id: str
    bot_name: str
    description: str = ""
    commands: List[BotCommand] = None
    webhook_url: str = ""
    webhook_secret: str = ""
    privacy_mode: bool = True
    inline_mode: bool = False
    admin_ids: List[int] = None
    
    def __post_init__(self):
        if self.commands is None:
            self.commands = []
        if self.admin_ids is None:
            self.admin_ids = []
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        data = asdict(self)
        data['commands'] = [asdict(cmd) for cmd in self.commands]
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return json.loads(self.to_json())


class BotFatherParser:
    """Parser for BotFather messages and responses"""
    
    # Regex patterns for token extraction
    TOKEN_PATTERN = r"([0-9]+):([A-Za-z0-9_-]{27})"
    BOT_ID_PATTERN = r"Done! Congratulations on your new bot\. You will find it at t\.me/(\w+)\. You can now add a description, commands, and other stuff using the `/setdescription`, `/setcommands`\[^a-zA-Z]*commands that your bot supports\."
    BOT_NAME_PATTERN = r"t\.me/([\w_]+)"
    
    def __init__(self):
        """Initialize the parser"""
        self.last_parsed_token: Optional[BotToken] = None
    
    @staticmethod
    def extract_token(message: str) -> Optional[BotToken]:
        """
        Extract bot token from BotFather response.
        
        Args:
            message: BotFather response message
            
        Returns:
            BotToken object or None if no token found
        """
        match = re.search(BotFatherParser.TOKEN_PATTERN, message)
        if not match:
            return None
        
        token = f"{match.group(1)}:{match.group(2)}"
        bot_id = int(match.group(1))
        
        # Extract bot name from telegram link
        name_match = re.search(BotFatherParser.BOT_NAME_PATTERN, message)
        bot_name = name_match.group(1) if name_match else f"bot_{bot_id}"
        
        return BotToken(
            token=token,
            bot_id=bot_id,
            bot_name=bot_name,
            is_bot=True,
            first_name=bot_name
        )
    
    @staticmethod
    def parse_commands_list(message: str) -> List[BotCommand]:
        """
        Parse command list from message.
        Format: /command - Description
        """
        commands = []
        # Match patterns like "/command - Description"
        pattern = r"/(\w+)\s*-\s*([^\n]+)"
        matches = re.finditer(pattern, message)
        
        for match in matches:
            commands.append(BotCommand(
                command=match.group(1),
                description=match.group(2).strip()
            ))
        
        return commands
    
    @staticmethod
    def is_success_response(message: str) -> bool:
        """Check if BotFather response indicates success"""
        success_keywords = [
            "Done!",
            "success",
            "successfully",
            "updated",
            "set",
            "enabled",
            "created",
            "configured"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in success_keywords)
    
    @staticmethod
    def is_error_response(message: str) -> bool:
        """Check if BotFather response indicates an error"""
        error_keywords = [
            "error",
            "failed",
            "invalid",
            "not found",
            "already exists",
            "too many requests",
            "bad request"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in error_keywords)
    
    @staticmethod
    def extract_error_details(message: str) -> Optional[str]:
        """Extract error details from BotFather response"""
        # Common error patterns in BotFather
        error_patterns = [
            r"Error: (.+?)(?:\n|$)",
            r"❌ (.+?)(?:\n|$)",
            r"Invalid (.+?)(?:\n|$)"
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        
        return None
    
    def parse_newbot_response(self, message: str) -> Dict[str, Any]:
        """
        Parse response from /newbot command.
        
        Returns:
            Dictionary with token, bot_id, bot_name, and status
        """
        token = self.extract_token(message)
        
        if token:
            self.last_parsed_token = token
            return {
                "status": "success",
                "action": "newbot",
                "token": token.token,
                "bot_id": token.bot_id,
                "bot_name": token.bot_name,
                "telegram_url": f"https://t.me/{token.bot_name}",
                "raw_message": message
            }
        elif self.is_error_response(message):
            return {
                "status": "error",
                "action": "newbot",
                "error": self.extract_error_details(message) or message,
                "raw_message": message
            }
        else:
            return {
                "status": "pending",
                "action": "newbot",
                "message": message,
                "raw_message": message
            }
    
    def parse_setcommands_response(self, message: str, commands: List[BotCommand]) -> Dict[str, Any]:
        """Parse response from /setcommands"""
        if self.is_success_response(message):
            return {
                "status": "success",
                "action": "setcommands",
                "commands": [asdict(cmd) for cmd in commands],
                "message": message
            }
        elif self.is_error_response(message):
            return {
                "status": "error",
                "action": "setcommands",
                "error": self.extract_error_details(message) or message
            }
        else:
            return {
                "status": "pending",
                "action": "setcommands",
                "message": message
            }
    
    def parse_webhook_response(self, message: str, webhook_url: str) -> Dict[str, Any]:
        """Parse response from /setwebhook"""
        if self.is_success_response(message):
            return {
                "status": "success",
                "action": "setwebhook",
                "webhook_url": webhook_url,
                "message": message
            }
        elif self.is_error_response(message):
            return {
                "status": "error",
                "action": "setwebhook",
                "webhook_url": webhook_url,
                "error": self.extract_error_details(message) or message
            }
        else:
            return {
                "status": "pending",
                "action": "setwebhook",
                "webhook_url": webhook_url,
                "message": message
            }
    
    def create_bot_config(
        self,
        token: str,
        description: str,
        commands: List[BotCommand],
        webhook_url: str = "",
        webhook_secret: str = "",
        admin_ids: List[int] = None
    ) -> BotConfiguration:
        """Create complete BotConfiguration from parsed data"""
        bot_id = int(token.split(":")[0])
        bot_name = self.last_parsed_token.bot_name if self.last_parsed_token else f"bot_{bot_id}"
        
        return BotConfiguration(
            token=token,
            bot_id=bot_id,
            bot_name=bot_name,
            description=description,
            commands=commands,
            webhook_url=webhook_url,
            webhook_secret=webhook_secret,
            admin_ids=admin_ids or []
        )


def parse_botfather_interaction(interaction_log: str) -> Dict[str, Any]:
    """
    Parse a complete BotFather interaction log.
    
    Args:
        interaction_log: Complete chat log with BotFather
        
    Returns:
        Parsed interaction data
    """
    parser = BotFatherParser()
    
    results = {
        "total_messages": len(interaction_log.split("\n")),
        "parsed_data": {},
        "errors": [],
        "warnings": []
    }
    
    lines = interaction_log.split("\n")
    
    for line in lines:
        if "Done! Congratulations" in line or ":" in line:
            token = parser.extract_token(line)
            if token:
                results["parsed_data"]["token"] = token.to_dict()
    
    return results


if __name__ == "__main__":
    # Test parser
    parser = BotFatherParser()
    
    # Test token extraction
    test_message = "Done! Congratulations on your new bot. You will find it at t.me/testbot. Here is your token: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    token = parser.extract_token(test_message)
    
    if token:
        print(f"✅ Token extracted: {token.token}")
        print(f"   Bot ID: {token.bot_id}")
        print(f"   Bot Name: {token.bot_name}")
    
    # Test command parsing
    commands_text = "/start - Start the bot\n/help - Show help\n/status - Show status"
    commands = parser.parse_commands_list(commands_text)
    print(f"\n✅ Commands parsed: {len(commands)}")
    for cmd in commands:
        print(f"   /{cmd.command}: {cmd.description}")
    
    print("\n✅ BotFather parser ready!")
