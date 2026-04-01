"""
OpenClaw Bot Creation Agent - Main Orchestrator
Coordinates the complete workflow from specification to deployment.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

from botfather_prompts import get_system_prompts_bundle
from botfather_parser import BotFatherParser, BotConfiguration, BotCommand
from bot_generator import BotGenerator, BotTemplate, generate_bot_project

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BotSpecification:
    """Bot specification from user input"""
    bot_name: str
    description: str
    commands: List[Dict[str, str]]
    features: Dict[str, bool]
    target_users: str
    language: str
    privacy_mode: bool = True
    inline_mode: bool = False
    admin_ids: List[int] = None
    webhook_url: str = ""
    
    def __post_init__(self):
        if self.admin_ids is None:
            self.admin_ids = []


@dataclass
class OrchestrationStep:
    """Single orchestration step result"""
    name: str
    status: str  # "pending", "in_progress", "success", "failed"
    timestamp: str
    result: Dict[str, Any] = None
    error: str = None
    
    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "timestamp": self.timestamp,
            "result": self.result,
            "error": self.error
        }


class BotCreationAgent:
    """
    Main orchestrator for automated bot creation.
    Handles all steps from specification to deployment.
    """
    
    def __init__(self):
        """Initialize the bot creation agent"""
        self.orchestration_id = str(uuid.uuid4())
        self.steps: Dict[str, OrchestrationStep] = {}
        self.prompts = get_system_prompts_bundle()
        self.parser = BotFatherParser()
        self.specification: Optional[BotSpecification] = None
        self.bot_token: Optional[str] = None
        self.bot_config: Optional[BotConfiguration] = None
        self.generated_files: Dict[str, str] = {}
        
        logger.info(f"[v0] Bot Creation Agent initialized: {self.orchestration_id}")
    
    def parse_specification(self, spec_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and validate user input specification.
        
        Args:
            spec_input: User input specification
            
        Returns:
            Parsed specification result
        """
        step = OrchestrationStep(
            name="parse_specification",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            # Validate required fields
            required_fields = ["bot_name", "description", "commands"]
            for field in required_fields:
                if field not in spec_input:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create specification
            self.specification = BotSpecification(
                bot_name=spec_input.get("bot_name"),
                description=spec_input.get("description"),
                commands=spec_input.get("commands", []),
                features=spec_input.get("features", {}),
                target_users=spec_input.get("target_users", "General"),
                language=spec_input.get("language", "de"),
                privacy_mode=spec_input.get("privacy_mode", True),
                inline_mode=spec_input.get("inline_mode", False),
                admin_ids=spec_input.get("admin_ids", []),
                webhook_url=spec_input.get("webhook_url", "")
            )
            
            step.status = "success"
            step.result = asdict(self.specification)
            
            logger.info(f"[v0] Specification parsed: {self.specification.bot_name}")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"[v0] Specification parsing failed: {e}")
        
        self.steps["parse_specification"] = step
        return step.to_dict()
    
    def generate_code(self) -> Dict[str, Any]:
        """
        Generate bot code and configuration files.
        
        Returns:
            Generation result
        """
        step = OrchestrationStep(
            name="generate_code",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            if not self.specification:
                raise ValueError("Specification not parsed yet")
            
            # Determine template based on complexity
            if len(self.specification.commands) <= 3:
                template = BotTemplate.MINIMAL
            elif len(self.specification.commands) <= 10:
                template = BotTemplate.STANDARD
            else:
                template = BotTemplate.ADVANCED
            
            # Generate project files
            self.generated_files = generate_bot_project(
                bot_name=self.specification.bot_name,
                description=self.specification.description,
                token="PLACEHOLDER_TOKEN",  # Will be replaced after BotFather creation
                bot_id=0,  # Will be updated
                template=template,
                webhook_url=self.specification.webhook_url,
                admin_ids=self.specification.admin_ids
            )
            
            step.status = "success"
            step.result = {
                "template": template.value,
                "files_generated": list(self.generated_files.keys()),
                "file_count": len(self.generated_files)
            }
            
            logger.info(f"[v0] Generated {len(self.generated_files)} files")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"[v0] Code generation failed: {e}")
        
        self.steps["generate_code"] = step
        return step.to_dict()
    
    def handle_botfather_interaction(
        self,
        botfather_responses: List[str]
    ) -> Dict[str, Any]:
        """
        Parse BotFather interaction and extract token.
        
        Args:
            botfather_responses: List of BotFather responses
            
        Returns:
            BotFather interaction result
        """
        step = OrchestrationStep(
            name="botfather_interaction",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            if not botfather_responses:
                raise ValueError("No BotFather responses provided")
            
            # Parse token from responses
            token = None
            for response in botfather_responses:
                token = self.parser.extract_token(response)
                if token:
                    break
            
            if not token:
                raise ValueError("Could not extract token from BotFather responses")
            
            self.bot_token = token.token
            
            # Create bot configuration
            commands = [
                BotCommand(cmd.get("command", ""), cmd.get("description", ""))
                for cmd in self.specification.commands
            ]
            
            self.bot_config = BotConfiguration(
                token=token.token,
                bot_id=token.bot_id,
                bot_name=token.bot_name,
                description=self.specification.description,
                commands=commands,
                webhook_url=self.specification.webhook_url,
                admin_ids=self.specification.admin_ids
            )
            
            step.status = "success"
            step.result = {
                "token": token.token,
                "bot_id": token.bot_id,
                "bot_name": token.bot_name,
                "telegram_url": f"https://t.me/{token.bot_name}"
            }
            
            logger.info(f"[v0] BotFather interaction successful: {token.bot_name}")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"[v0] BotFather interaction failed: {e}")
        
        self.steps["botfather_interaction"] = step
        return step.to_dict()
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate complete bot configuration.
        
        Returns:
            Validation result
        """
        step = OrchestrationStep(
            name="validate_configuration",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            checks = {
                "has_token": bool(self.bot_token),
                "has_config": bool(self.bot_config),
                "has_commands": len(self.specification.commands) > 0,
                "has_description": len(self.specification.description) > 0,
                "valid_admin_ids": all(isinstance(aid, int) for aid in self.specification.admin_ids),
            }
            
            all_valid = all(checks.values())
            
            step.status = "success" if all_valid else "failed"
            step.result = {
                "checks": checks,
                "valid": all_valid,
                "score": int(sum(checks.values()) / len(checks) * 100)
            }
            
            if all_valid:
                logger.info(f"[v0] Validation passed: {step.result['score']}% score")
            else:
                logger.warning(f"[v0] Validation issues found: {checks}")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"[v0] Validation failed: {e}")
        
        self.steps["validate_configuration"] = step
        return step.to_dict()
    
    def prepare_deployment(self) -> Dict[str, Any]:
        """
        Prepare deployment configuration.
        
        Returns:
            Deployment preparation result
        """
        step = OrchestrationStep(
            name="prepare_deployment",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            deployment_config = {
                "deployment_id": self.orchestration_id,
                "bot_name": self.specification.bot_name,
                "bot_id": self.bot_config.bot_id if self.bot_config else None,
                "created_at": datetime.now().isoformat(),
                "deployment_type": "docker",  # or "systemd"
                "files": {
                    "config": self.bot_config.to_json() if self.bot_config else None,
                    "generated_files": list(self.generated_files.keys())
                },
                "environment": {
                    "TELEGRAM_BOT_TOKEN": self.bot_token or "SET_FROM_BOTFATHER",
                    "BOT_ID": self.bot_config.bot_id if self.bot_config else None,
                    "ADMIN_IDS": json.dumps(self.specification.admin_ids),
                    "LOG_LEVEL": "INFO"
                },
                "instructions": [
                    "1. Set TELEGRAM_BOT_TOKEN in environment",
                    "2. Configure webhook if using HTTP polling",
                    "3. Run: docker build -t mybot .",
                    "4. Run: docker run -e TELEGRAM_BOT_TOKEN=... mybot"
                ]
            }
            
            step.status = "success"
            step.result = deployment_config
            
            logger.info(f"[v0] Deployment prepared: {self.orchestration_id}")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"[v0] Deployment preparation failed: {e}")
        
        self.steps["prepare_deployment"] = step
        return step.to_dict()
    
    def document_bot(self) -> Dict[str, Any]:
        """
        Generate bot documentation.
        
        Returns:
            Documentation result
        """
        step = OrchestrationStep(
            name="document_bot",
            status="in_progress",
            timestamp=datetime.now().isoformat()
        )
        
        try:
            documentation = f"""# {self.specification.bot_name} Bot Documentation

## Bot Information
- **Name**: {self.specification.bot_name}
- **ID**: {self.bot_config.bot_id if self.bot_config else 'N/A'}
- **Telegram**: [@{self.bot_config.bot_name}](https://t.me/{self.bot_config.bot_name if self.bot_config else 'bot'})
- **Description**: {self.specification.description}

## Available Commands
"""
            
            for cmd in self.specification.commands:
                documentation += f"- `/{cmd.get('command')}` - {cmd.get('description', 'No description')}\n"
            
            documentation += f"""
## Setup Instructions
1. Get your API token from [@BotFather](https://t.me/botfather)
2. Set the TELEGRAM_BOT_TOKEN environment variable
3. Run the bot using Python or Docker
4. Configure webhook if needed

## Configuration
- **Privacy Mode**: {'Enabled' if self.specification.privacy_mode else 'Disabled'}
- **Inline Mode**: {'Enabled' if self.specification.inline_mode else 'Disabled'}
- **Language**: {self.specification.language.upper()}

## Features
{json.dumps(self.specification.features, indent=2)}

## Generated Files
{json.dumps(list(self.generated_files.keys()), indent=2)}

---
Generated by OpenClaw Bot Creation Agent at {datetime.now().isoformat()}
"""
            
            step.status = "success"
            step.result = {
                "documentation": documentation,
                "length": len(documentation)
            }
            
            logger.info(f"[v0] Documentation generated")
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            logger.error(f"[v0] Documentation generation failed: {e}")
        
        self.steps["document_bot"] = step
        return step.to_dict()
    
    def run_full_workflow(
        self,
        spec_input: Dict[str, Any],
        botfather_responses: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete bot creation workflow.
        
        Args:
            spec_input: User specification input
            botfather_responses: BotFather interaction responses
            
        Returns:
            Complete workflow result
        """
        logger.info(f"[v0] Starting bot creation workflow: {self.orchestration_id}")
        
        results = {
            "orchestration_id": self.orchestration_id,
            "status": "in_progress",
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }
        
        # Step 1: Parse specification
        results["steps"]["parse_specification"] = self.parse_specification(spec_input)
        if results["steps"]["parse_specification"]["status"] != "success":
            results["status"] = "failed"
            return results
        
        # Step 2: Generate code
        results["steps"]["generate_code"] = self.generate_code()
        if results["steps"]["generate_code"]["status"] != "success":
            results["status"] = "failed"
            return results
        
        # Step 3: Handle BotFather interaction (if responses provided)
        if botfather_responses:
            results["steps"]["botfather_interaction"] = self.handle_botfather_interaction(botfather_responses)
            if results["steps"]["botfather_interaction"]["status"] != "success":
                results["status"] = "failed"
                return results
        
        # Step 4: Validate configuration
        results["steps"]["validate_configuration"] = self.validate_configuration()
        if results["steps"]["validate_configuration"]["status"] != "success":
            results["status"] = "warning"
        
        # Step 5: Prepare deployment
        results["steps"]["prepare_deployment"] = self.prepare_deployment()
        
        # Step 6: Document bot
        results["steps"]["document_bot"] = self.document_bot()
        
        # Final status
        results["status"] = "success"
        results["bot_data"] = {
            "token": self.bot_token,
            "bot_id": self.bot_config.bot_id if self.bot_config else None,
            "bot_name": self.bot_config.bot_name if self.bot_config else None,
            "files_count": len(self.generated_files)
        }
        
        logger.info(f"[v0] Workflow completed: {self.orchestration_id}")
        
        return results


def main():
    """Test the bot creation agent"""
    agent = BotCreationAgent()
    
    # Example specification
    spec = {
        "bot_name": "AutoBot",
        "description": "Ein automatisierter Bot für Web-Automation",
        "commands": [
            {"command": "start", "description": "Bot starten"},
            {"command": "help", "description": "Hilfe anzeigen"},
            {"command": "status", "description": "Status prüfen"},
            {"command": "automate", "description": "Automatisierung starten"}
        ],
        "features": {
            "chat": True,
            "commands": True,
            "automation": True,
            "health_check": True
        },
        "target_users": "Tech-Enthusiasts",
        "language": "de"
    }
    
    # Run workflow
    result = agent.run_full_workflow(spec)
    
    print("\n" + "="*60)
    print("BOT CREATION WORKFLOW RESULT")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
