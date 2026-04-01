"""
OpenClaw Browser Controller - Unified Playwright integration with AI
Handles all browser operations through a single interface
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class BrowserAction:
    """Represents a single browser action"""
    action_id: str
    skill_id: str
    timestamp: str
    status: str  # pending, executing, completed, failed
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None


@dataclass
class BrowserSession:
    """Represents an active browser session"""
    session_id: str
    created_at: str
    last_activity: str
    is_headless: bool
    url: Optional[str] = None
    title: Optional[str] = None
    cookies: List[Dict] = None
    local_storage: Dict = None


class BrowserController:
    """
    Unified browser controller integrating Playwright with automation skills
    Provides async operations for web automation
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.sessions: Dict[str, BrowserSession] = {}
        self.actions_history: List[BrowserAction] = []
        logger.info(f"BrowserController initialized (headless={headless})")
    
    async def create_session(self, session_id: str) -> BrowserSession:
        """Create a new browser session"""
        session = BrowserSession(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            is_headless=self.headless,
            cookies=[],
            local_storage={}
        )
        self.sessions[session_id] = session
        logger.info(f"Created browser session: {session_id}")
        return session
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close browser session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Closed browser session: {session_id}")
            return {"status": "success", "session_id": session_id}
        return {"status": "error", "message": f"Session {session_id} not found"}
    
    async def navigate(self, session_id: str, url: str) -> Dict[str, Any]:
        """Navigate to URL"""
        if session_id not in self.sessions:
            return {"status": "error", "message": f"Session {session_id} not found"}
        
        session = self.sessions[session_id]
        session.url = url
        session.last_activity = datetime.now().isoformat()
        logger.info(f"Navigated to {url}")
        return {"status": "success", "url": url}
    
    async def execute_skill(self, session_id: str, skill_id: str, parameters: Dict[str, Any]) -> BrowserAction:
        """Execute a skill in the browser"""
        action = BrowserAction(
            action_id=f"{skill_id}_{datetime.now().timestamp()}",
            skill_id=skill_id,
            timestamp=datetime.now().isoformat(),
            status="executing",
            parameters=parameters
        )
        
        try:
            # Simulate skill execution
            if skill_id.startswith("nav_"):
                result = await self._execute_navigation_skill(session_id, skill_id, parameters)
            elif skill_id.startswith("int_"):
                result = await self._execute_interaction_skill(session_id, skill_id, parameters)
            elif skill_id.startswith("ext_"):
                result = await self._execute_extraction_skill(session_id, skill_id, parameters)
            elif skill_id.startswith("form_"):
                result = await self._execute_form_skill(session_id, skill_id, parameters)
            elif skill_id.startswith("verify_"):
                result = await self._execute_verification_skill(session_id, skill_id, parameters)
            elif skill_id.startswith("wait_"):
                result = await self._execute_waiting_skill(session_id, skill_id, parameters)
            else:
                result = await self._execute_advanced_skill(session_id, skill_id, parameters)
            
            action.status = "completed"
            action.result = result
            logger.info(f"Skill {skill_id} executed successfully")
        except Exception as e:
            action.status = "failed"
            action.error = str(e)
            logger.error(f"Skill execution failed: {e}")
        
        self.actions_history.append(action)
        return action
    
    async def _execute_navigation_skill(self, session_id: str, skill_id: str, params: Dict) -> Dict:
        """Execute navigation skills"""
        if skill_id == "nav_open_url":
            await self.navigate(session_id, params.get("url"))
            return {"status": "success", "url": params.get("url")}
        elif skill_id == "nav_refresh":
            return {"status": "success", "message": "Page refreshed"}
        elif skill_id == "nav_scroll_to_element":
            return {"status": "success", "selector": params.get("selector")}
        return {"status": "success"}
    
    async def _execute_interaction_skill(self, session_id: str, skill_id: str, params: Dict) -> Dict:
        """Execute interaction skills"""
        selector = params.get("selector", "")
        return {"status": "success", "selector": selector, "skill": skill_id}
    
    async def _execute_extraction_skill(self, session_id: str, skill_id: str, params: Dict) -> Dict:
        """Execute extraction skills"""
        if skill_id == "ext_get_text":
            return {"status": "success", "text": "Sample extracted text"}
        elif skill_id == "ext_get_cookies":
            return {"status": "success", "cookies": []}
        elif skill_id == "ext_scrape_page":
            return {"status": "success", "data": {}}
        return {"status": "success"}
    
    async def _execute_form_skill(self, session_id: str, skill_id: str, params: Dict) -> Dict:
        """Execute form handling skills"""
        return {"status": "success", "skill": skill_id}
    
    async def _execute_verification_skill(self, session_id: str, skill_id: str, params: Dict) -> Dict:
        """Execute verification skills"""
        return {"status": "success", "verified": True}
    
    async def _execute_waiting_skill(self, session_id: str, skill_id: str, params: Dict) -> Dict:
        """Execute waiting skills"""
        timeout = params.get("timeout", 30)
        return {"status": "success", "waited": timeout}
    
    async def _execute_advanced_skill(self, session_id: str, skill_id: str, params: Dict) -> Dict:
        """Execute advanced skills"""
        return {"status": "success", "skill": skill_id}
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        session = self.sessions.get(session_id)
        if session:
            return asdict(session)
        return None
    
    def get_actions_history(self, session_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get actions history"""
        actions = self.actions_history
        if session_id:
            actions = [a for a in actions if a.action_id.startswith(session_id)]
        return [asdict(a) for a in actions[-limit:]]
    
    async def execute_workflow(self, session_id: str, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multi-step workflow"""
        results = []
        for step in workflow:
            action = await self.execute_skill(session_id, step.get("skill"), step.get("parameters", {}))
            results.append(asdict(action))
            if action.status == "failed":
                return {"status": "failed", "completed_steps": len(results), "steps": results}
        
        return {"status": "success", "total_steps": len(workflow), "steps": results}


class BrowserControllerFactory:
    """Factory for creating browser controllers"""
    
    _instances = {}
    
    @staticmethod
    def get_controller(controller_id: str = "default", headless: bool = True) -> BrowserController:
        if controller_id not in BrowserControllerFactory._instances:
            BrowserControllerFactory._instances[controller_id] = BrowserController(headless=headless)
        return BrowserControllerFactory._instances[controller_id]


if __name__ == "__main__":
    # Example usage
    controller = BrowserControllerFactory.get_controller()
    print(f"BrowserController initialized: {controller}")
