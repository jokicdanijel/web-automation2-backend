# OpenClaw FastAPI Localhost Setup & Integration Guide

Complete workflow for creating a production-ready localhost environment with FastAPI, Docker, and full system integration.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [API Endpoints](#api-endpoints)
6. [WebSocket Integration](#websocket-integration)
7. [KAIS Integration](#kais-integration)
8. [Docker Deployment](#docker-deployment)
9. [Master Agent System](#master-agent-system)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option 1: Direct Startup (Recommended for Development)

```bash
# Navigate to project directory
cd /path/to/openclaw

# Run startup script
chmod +x startup.sh
./startup.sh

# Server will start on http://localhost:8000
```

### Option 2: Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f openclaw-api

# Stop all services
docker-compose down
```

### Option 3: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start server
python3 main.py
```

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                  OpenClaw Dashboard                      │
│         (HTML/CSS/JS - Cockpit Interface)               │
└────────────────────┬────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐   ┌─────▼──────┐  ┌─────▼──────┐
│  HTTP   │   │ WebSocket  │  │  REST API  │
│ Requests│   │  Real-time │  │ Endpoints  │
└────┬────┘   └──────┬─────┘  └─────┬──────┘
     │               │              │
     └───────────────┼──────────────┘
                     │
        ┌────────────▼────────────┐
        │    FastAPI Main App     │
        │     (main.py)           │
        └────────┬────────────────┘
                 │
     ┌───────────┼───────────┬────────────┬──────────────┐
     │           │           │            │              │
┌────▼──┐  ┌─────▼─┐  ┌─────▼───┐  ┌────▼────┐  ┌─────▼────┐
│Master │  │Browser│  │Audio/   │  │  Form   │  │  KAIS    │
│Agent  │  │Auto   │  │Speech   │  │Handler  │  │Integration
│       │  │       │  │         │  │         │  │          │
└──┬────┘  └───────┘  └─────────┘  └─────────┘  └──────────┘
   │
   ├─ Telegram Bot
   ├─ Health Monitor
   ├─ Automation Skills
   └─ AI Service

        ┌─────────────────────────┐
        │   Database Layer        │
        ├─────────────────────────┤
        │ PostgreSQL │ SQLite     │
        │ Redis      │ File Cache │
        └─────────────────────────┘
```

---

## Installation Methods

### Method 1: Development Setup (Recommended)

**Requirements:**
- Python 3.9+
- pip/venv
- Optional: PostgreSQL, Redis

**Steps:**

```bash
# 1. Clone/Setup project
mkdir openclaw
cd openclaw

# 2. Run startup script
./startup.sh

# 3. Access dashboard
open http://localhost:8000/dashboard
```

**Expected Output:**
```
[✓] Python 3.11 found
[✓] Virtual environment created
[✓] Dependencies installed
[✓] Directories created
[✓] .env file created
[✓] Database initialized
[✓] Starting on http://localhost:8000
```

### Method 2: Docker Container

**Requirements:**
- Docker 20.10+
- Docker Compose 2.0+

**Steps:**

```bash
# 1. Copy .env.example to .env
cp .env.example .env

# 2. Edit .env with API keys
nano .env

# 3. Build and start
docker-compose up --build

# 4. Check services
docker-compose ps
```

**Services Running:**
- OpenClaw API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Telegram Bot: Running in background

### Method 3: Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace openclaw

# Apply manifests
kubectl apply -f k8s/deployment.yaml -n openclaw

# Check deployment
kubectl get pods -n openclaw
```

---

## Configuration

### Environment Variables

Key variables in `.env`:

```env
# Server
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=sqlite:///openclaw.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost/openclaw

# API Keys
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZ
GROQ_API_KEY=gsk_xxxxx
ELEVENLABS_API_KEY=sk_xxxxx

# KAIS Integration
KAIS_API_KEY=your_key_here
KAIS_API_URL=http://localhost:9000
```

### Dashboard Configuration

Edit `dashboard_config.json`:

```json
{
  "theme": "dark",
  "refresh_interval": 2000,
  "api_endpoint": "http://localhost:8000",
  "features": {
    "audio_enabled": true,
    "chat_enabled": true,
    "automation_enabled": true
  }
}
```

---

## API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | System health check |
| `/metrics` | GET | Detailed system metrics |
| `/oscar` | GET | OSCAR-VinJSON format data |
| `/docs` | GET | OpenAPI documentation |

### Automation

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/automation/start` | POST | Start automation workflow |
| `/api/automation/execute` | POST | Execute single skill |
| `/api/skills` | GET | List available skills |

### Forms

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/form-automate/detect` | POST | Detect forms on page |
| `/api/form-automate/fill` | POST | Fill and submit form |

### Audio/Speech

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/audio/transcribe` | POST | Transcribe audio to text |
| `/api/audio/synthesize` | POST | Synthesize speech from text |

### Chat

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Send message to bot |

### KAIS Integration

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/kais/execute` | POST | Execute KAIS command |
| `/api/kais/webhook` | POST | Handle incoming webhook |

---

## WebSocket Integration

### Real-time Dashboard Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

// Receive metrics every 2 seconds
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Metrics:', data.metrics);
    console.log('Components:', data.components);
};

// Close connection
ws.close();
```

### Real-time Logs

```javascript
const logsWs = new WebSocket('ws://localhost:8000/ws/logs');

logsWs.onmessage = (event) => {
    const logs = JSON.parse(event.data).logs;
    logs.forEach(log => {
        console.log(`[${log.level}] ${log.message}`);
    });
};
```

---

## KAIS Integration

### Execute Command

```bash
curl -X POST http://localhost:8000/api/kais/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "execute_automation",
    "params": {
      "workflow": "full_automation"
    }
  }'
```

### Response Format

```json
{
  "status": 200,
  "command": "execute_automation",
  "result": {
    "action": "automation_started",
    "workflow": "full_automation",
    "status": "executing"
  }
}
```

### Webhook Registration

```bash
curl -X POST http://localhost:8000/api/kais/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "type": "automation_complete",
    "callback_url": "http://your-system.com/callback"
  }'
```

---

## Docker Deployment

### Build Custom Image

```bash
docker build -t openclaw:latest .
docker run -p 8000:8000 -e TELEGRAM_BOT_TOKEN=xxx openclaw:latest
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f openclaw-api

# Scale services
docker-compose up -d --scale worker=3

# Stop and remove
docker-compose down -v
```

### Environment Variables in Docker

```bash
docker run -e TELEGRAM_BOT_TOKEN=xxx \
           -e GROQ_API_KEY=yyy \
           -e DATABASE_URL=postgresql://user:pass@db:5432/openclaw \
           -p 8000:8000 \
           openclaw:latest
```

---

## Master Agent System

### Understanding Master Agent

The Master Agent (`master_agent.py`) orchestrates all OpenClaw components:

```python
# Initialize master agent
agent = MasterAgent(config)
await agent.initialize()

# Execute workflow
result = await agent.execute_workflow("full_automation")

# Execute skill
result = await agent.execute_skill("navigate", {"url": "https://example.com"})

# Get status
status = await agent.get_status()
```

### Available Workflows

1. **Default Workflow**
   - Health check
   - Screenshot
   - Basic metrics

2. **Full Automation**
   - Navigation
   - Form detection
   - Data extraction
   - Screenshot

3. **Custom Workflows**
   - Define in `master_agent.py`
   - Combine skills as needed

### Component Status

Master agent monitors:
- Telegram Bot (99.2% health)
- Browser Automation (98.5% health)
- Audio Pipeline (99.8% health)
- Form Handler (97.2% health)

---

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python3 main.py --port 8001
```

**2. Module Not Found**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

**3. Database Connection Error**
```bash
# Check SQLite file exists
ls -la openclaw.db

# Or PostgreSQL connection
psql -h localhost -U openclaw -d openclaw
```

**4. CORS Issues**
```bash
# Already configured in main.py
# If issues persist, check dashboard_config.json
```

**5. WebSocket Connection Failed**
```bash
# Check firewall
sudo ufw allow 8000

# Verify WebSocket support in reverse proxy (nginx/apache)
```

### Debug Mode

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python3 main.py

# Or in .env
LOG_LEVEL=DEBUG
```

### Health Check

```bash
# Check system health
curl http://localhost:8000/health | jq

# Expected response:
{
  "status": "online",
  "uptime_seconds": 3600,
  "cpu_usage": 15.2,
  "memory_usage": 45.8,
  "components": {
    "telegram_bot": 99.2,
    "browser_automation": 98.5,
    "audio_pipeline": 99.8,
    "form_handler": 97.2
  }
}
```

---

## Performance Tips

1. **Enable Caching**
   - Redis for distributed cache
   - Browser cache for automation

2. **Optimize Queries**
   - Database indexes
   - Connection pooling

3. **Async Operations**
   - Use asyncio for concurrent tasks
   - WebSocket for real-time updates

4. **Resource Limits**
   - Set memory limits in docker-compose
   - Configure max workers

---

## Next Steps

1. Access Dashboard: http://localhost:8000/dashboard
2. Read API Docs: http://localhost:8000/docs
3. Configure Telegram Bot: Edit `TELEGRAM_BOT_TOKEN` in `.env`
4. Set up KAIS Integration: Add `KAIS_API_KEY` and `KAIS_API_URL`
5. Customize Workflows: Edit `master_agent.py`

---

## Support & Documentation

- Documentation: `/docs` endpoint
- API Reference: OpenAPI docs
- Examples: `examples/` directory
- Issues: GitHub Issues

---

**Last Updated:** 2024
**Version:** 1.0.0
**Status:** Production Ready ✓

