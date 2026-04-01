"""
OpenClaw Unified REST API
Provides complete REST interface for all automation capabilities
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps
import asyncio

from automation_skills import AutomationSkills
from browser_controller import BrowserControllerFactory

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

skills = AutomationSkills()


# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"status": "error", "message": "Missing or invalid authorization"}), 401
        return f(*args, **kwargs)
    return decorated


# ============= HEALTH & STATUS =============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "skills": "operational",
            "browser": "operational"
        }
    })


@app.route('/api/status', methods=['GET'])
def status():
    """System status endpoint"""
    return jsonify({
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "total_skills": len(skills.skills),
        "api_version": "1.0.0"
    })


# ============= SKILLS ENDPOINTS =============

@app.route('/api/skills', methods=['GET'])
def get_skills():
    """Get all available skills"""
    category = request.args.get('category')
    tag = request.args.get('tag')
    
    if category:
        skill_list = skills.get_skills_by_category(category)
    elif tag:
        skill_list = skills.get_skills_by_tag(tag)
    else:
        skill_list = list(skills.skills.values())
    
    return jsonify({
        "status": "success",
        "count": len(skill_list),
        "skills": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "difficulty": s.difficulty,
                "tags": s.tags
            }
            for s in skill_list
        ]
    })


@app.route('/api/skills/<skill_id>', methods=['GET'])
def get_skill(skill_id):
    """Get skill details"""
    skill = skills.get_skill(skill_id)
    if not skill:
        return jsonify({"status": "error", "message": f"Skill {skill_id} not found"}), 404
    
    return jsonify({
        "status": "success",
        "skill": {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "category": skill.category,
            "parameters": skill.parameters,
            "expected_output": skill.expected_output,
            "difficulty": skill.difficulty,
            "timeout_seconds": skill.timeout_seconds,
            "retry_count": skill.retry_count,
            "tags": skill.tags
        }
    })


# ============= BROWSER ENDPOINTS =============

@app.route('/api/browser/session', methods=['POST'])
@require_auth
def create_session():
    """Create a new browser session"""
    data = request.get_json() or {}
    headless = data.get('headless', True)
    
    controller = BrowserControllerFactory.get_controller(headless=headless)
    session_id = f"session_{datetime.now().timestamp()}"
    
    async def _create():
        return await controller.create_session(session_id)
    
    session = asyncio.run(_create())
    return jsonify({
        "status": "success",
        "session_id": session_id,
        "headless": headless,
        "created_at": session.created_at
    })


@app.route('/api/browser/session/<session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    """Get session information"""
    controller = BrowserControllerFactory.get_controller()
    info = controller.get_session_info(session_id)
    
    if not info:
        return jsonify({"status": "error", "message": f"Session {session_id} not found"}), 404
    
    return jsonify({
        "status": "success",
        "session": info
    })


@app.route('/api/browser/session/<session_id>/close', methods=['POST'])
@require_auth
def close_session(session_id):
    """Close browser session"""
    controller = BrowserControllerFactory.get_controller()
    result = asyncio.run(controller.close_session(session_id))
    return jsonify(result)


# ============= AUTOMATION ENDPOINTS =============

@app.route('/api/automation/execute', methods=['POST'])
@require_auth
def execute_skill():
    """Execute a single skill"""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    skill_id = data.get('skill_id')
    parameters = data.get('parameters', {})
    
    if not session_id or not skill_id:
        return jsonify({"status": "error", "message": "Missing session_id or skill_id"}), 400
    
    skill = skills.get_skill(skill_id)
    if not skill:
        return jsonify({"status": "error", "message": f"Skill {skill_id} not found"}), 404
    
    controller = BrowserControllerFactory.get_controller()
    action = asyncio.run(controller.execute_skill(session_id, skill_id, parameters))
    
    return jsonify({
        "status": "success",
        "action": {
            "action_id": action.action_id,
            "skill_id": action.skill_id,
            "status": action.status,
            "result": action.result,
            "error": action.error,
            "timestamp": action.timestamp
        }
    })


@app.route('/api/automation/workflow', methods=['POST'])
@require_auth
def execute_workflow():
    """Execute a multi-step workflow"""
    data = request.get_json() or {}
    session_id = data.get('session_id')
    workflow = data.get('workflow', [])
    
    if not session_id or not workflow:
        return jsonify({"status": "error", "message": "Missing session_id or workflow"}), 400
    
    controller = BrowserControllerFactory.get_controller()
    result = asyncio.run(controller.execute_workflow(session_id, workflow))
    
    return jsonify({
        "status": "success",
        "workflow_result": result
    })


@app.route('/api/automation/history', methods=['GET'])
@require_auth
def get_history():
    """Get automation actions history"""
    session_id = request.args.get('session_id')
    limit = int(request.args.get('limit', 100))
    
    controller = BrowserControllerFactory.get_controller()
    history = controller.get_actions_history(session_id, limit)
    
    return jsonify({
        "status": "success",
        "count": len(history),
        "actions": history
    })


# ============= BOT INTEGRATION =============

@app.route('/api/bot/create', methods=['POST'])
@require_auth
def create_bot():
    """Create new bot with automation skills"""
    data = request.get_json() or {}
    bot_name = data.get('bot_name')
    skills_list = data.get('skills', [])
    
    if not bot_name:
        return jsonify({"status": "error", "message": "Missing bot_name"}), 400
    
    return jsonify({
        "status": "success",
        "bot": {
            "name": bot_name,
            "created_at": datetime.now().isoformat(),
            "skills": skills_list,
            "status": "ready"
        }
    })


# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500


# ============= SERVER CONFIG =============

def create_app(config=None):
    """Create and configure Flask app"""
    if config:
        app.config.update(config)
    
    logger.info("OpenClaw API initialized")
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="127.0.0.1", port=8000, debug=True)
