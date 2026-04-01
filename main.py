"""
OpenClaw FastAPI Main Application
Complete async FastAPI server with WebSocket, master agent orchestration, and dashboard integration
"""

from fastapi import FastAPI, WebSocket, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn

from config import AppConfig
from master_agent import MasterAgent
from kais_integration import KAISIntegration
from models import SystemMetrics
from oscar_vinjson import OSCARVinJSONGenerator
from ai_service import AIService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
master_agent: Optional[MasterAgent] = None
kais_service: Optional[KAISIntegration] = None
metrics_collector: Optional[SystemMetrics] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown"""
    global master_agent, kais_service, metrics_collector
    
    # Startup
    logger.info("Starting OpenClaw FastAPI Server...")
    config = AppConfig()
    master_agent = MasterAgent(config)
    kais_service = KAISIntegration(config)
    metrics_collector = SystemMetrics()
    
    await master_agent.initialize()
    await kais_service.initialize()
    logger.info("OpenClaw initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OpenClaw...")
    await master_agent.shutdown()
    await kais_service.shutdown()

# Create FastAPI app
app = FastAPI(
    title="OpenClaw Command Center",
    description="Master automation and control platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="html"), name="static")

# ============================================================================
# DASHBOARD ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main dashboard"""
    with open("html/cockpit.html", "r") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve dashboard"""
    with open("html/cockpit.html", "r") as f:
        return f.read()

@app.get("/config")
async def get_config():
    """Get dashboard configuration"""
    with open("dashboard_config.json", "r") as f:
        return json.load(f)

# ============================================================================
# HEALTH & METRICS
# ============================================================================

@app.get("/health")
async def health_check() -> Dict:
    """System health check with all metrics"""
    metrics = await metrics_collector.collect()
    components = await master_agent.get_components_status()
    
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": metrics["uptime"],
        "cpu_usage": metrics["cpu"],
        "memory_usage": metrics["memory"],
        "disk_usage": metrics["disk"],
        "network_latency": metrics["latency"],
        "request_count": metrics["requests"],
        "error_count": metrics["errors"],
        "components": components
    }

@app.get("/metrics")
async def get_metrics() -> Dict:
    """Get detailed system metrics"""
    return await metrics_collector.collect_detailed()

@app.get("/oscar")
async def get_oscar_vinjson() -> Dict:
    """Get OSCAR-VinJSON format data"""
    generator = OSCARVinJSONGenerator()
    metrics = await metrics_collector.collect()
    components = await master_agent.get_components_status()
    return generator.generate(metrics, components)

# ============================================================================
# AUTOMATION ENDPOINTS
# ============================================================================

@app.post("/api/automation/start")
async def start_automation(workflow: str = "default", background_tasks: BackgroundTasks = None) -> Dict:
    """Start automation workflow"""
    try:
        result = await master_agent.execute_workflow(workflow)
        background_tasks.add_task(logger.info, f"Workflow {workflow} completed")
        return {
            "status": "success",
            "workflow": workflow,
            "execution_id": result.get("id"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/automation/execute")
async def execute_skill(skill: str, params: Dict = None) -> Dict:
    """Execute single skill"""
    try:
        result = await master_agent.execute_skill(skill, params or {})
        return {
            "status": "success",
            "skill": skill,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Skill execution error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/skills")
async def list_skills() -> Dict:
    """List all available skills"""
    skills = await master_agent.list_skills()
    return {
        "total": len(skills),
        "skills": skills,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# FORM AUTOMATION
# ============================================================================

@app.post("/api/form-automate/detect")
async def detect_forms(page_url: str) -> Dict:
    """Detect forms on page"""
    try:
        forms = await master_agent.detect_forms(page_url)
        return {
            "status": "success",
            "url": page_url,
            "count": len(forms),
            "forms": forms,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/form-automate/fill")
async def fill_form(form_id: str, data: Dict) -> Dict:
    """Fill and submit form"""
    try:
        result = await master_agent.fill_form(form_id, data)
        return {
            "status": "success",
            "form_id": form_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# AUDIO & SPEECH
# ============================================================================

@app.post("/api/audio/transcribe")
async def transcribe_audio(audio_data: str, language: str = "en-US") -> Dict:
    """Transcribe audio to text"""
    try:
        result = await master_agent.transcribe_audio(audio_data, language)
        return {
            "status": "success",
            "text": result.get("text"),
            "language": language,
            "confidence": result.get("confidence"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/audio/synthesize")
async def synthesize_speech(text: str, voice: str = "default", language: str = "en-US") -> Dict:
    """Synthesize speech from text"""
    try:
        audio = await master_agent.synthesize_speech(text, voice, language)
        return {
            "status": "success",
            "text": text,
            "voice": voice,
            "language": language,
            "audio_base64": audio.get("base64"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# CHAT & BOT INTERACTION
# ============================================================================

@app.post("/api/chat")
async def chat_message(message: str, context: Optional[Dict] = None) -> Dict:
    """Send chat message to bot"""
    try:
        response = await master_agent.chat(message, context)
        return {
            "status": "success",
            "user_message": message,
            "bot_response": response,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# WEBSOCKET - REAL-TIME UPDATES
# ============================================================================

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket for real-time dashboard updates"""
    await websocket.accept()
    try:
        while True:
            # Send metrics every 2 seconds
            metrics = await metrics_collector.collect()
            components = await master_agent.get_components_status()
            
            await websocket.send_json({
                "type": "metrics_update",
                "metrics": metrics,
                "components": components,
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket for real-time logs"""
    await websocket.accept()
    try:
        while True:
            logs = await master_agent.get_recent_logs(limit=10)
            await websocket.send_json({
                "type": "logs_update",
                "logs": logs,
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

# ============================================================================
# KAIS INTEGRATION
# ============================================================================

@app.post("/api/kais/execute")
async def kais_execute(command: str, params: Dict = None) -> Dict:
    """Execute KAIS command"""
    try:
        result = await kais_service.execute_command(command, params or {})
        return {
            "status": "success",
            "command": command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/kais/webhook")
async def kais_webhook(event: Dict) -> Dict:
    """Receive KAIS webhook"""
    try:
        result = await kais_service.handle_webhook(event)
        return {
            "status": "success",
            "event_processed": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# MASTER AGENT CONTROL
# ============================================================================

@app.get("/api/agent/status")
async def agent_status() -> Dict:
    """Get master agent status"""
    status = await master_agent.get_status()
    return {
        "agent": "OpenClaw Master",
        "status": status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/agent/restart")
async def restart_agent() -> Dict:
    """Restart master agent"""
    try:
        await master_agent.restart()
        return {
            "status": "restarted",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# DOCUMENTATION
# ============================================================================

@app.get("/docs")
async def docs():
    """API documentation"""
    return {
        "title": "OpenClaw API Documentation",
        "base_url": "http://localhost:8000",
        "endpoints": {
            "dashboard": "/",
            "health": "/health",
            "metrics": "/metrics",
            "oscar": "/oscar",
            "websocket_dashboard": "/ws/dashboard",
            "websocket_logs": "/ws/logs"
        },
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    logger.info("Starting OpenClaw FastAPI Server on http://localhost:8000")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
