#!/bin/bash

###############################################################################
# OpenClaw Localhost Startup Script
# Complete development environment setup and startup
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
DATA_DIR="$PROJECT_DIR/data"
PORT=8000

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       OpenClaw Command Center - Startup Script        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# STEP 1: Check Python version
# ============================================================================

echo -e "${YELLOW}[1/8]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# ============================================================================
# STEP 2: Create virtual environment
# ============================================================================

echo -e "${YELLOW}[2/8]${NC} Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

source "$VENV_DIR/bin/activate"

# ============================================================================
# STEP 3: Install dependencies
# ============================================================================

echo -e "${YELLOW}[3/8]${NC} Installing Python dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

# ============================================================================
# STEP 4: Create directories
# ============================================================================

echo -e "${YELLOW}[4/8]${NC} Creating necessary directories..."
mkdir -p "$LOG_DIR" "$DATA_DIR" "$PROJECT_DIR/html/js" "$PROJECT_DIR/html/css"
echo -e "${GREEN}✓ Directories created${NC}"

# ============================================================================
# STEP 5: Environment configuration
# ============================================================================

echo -e "${YELLOW}[5/8]${NC} Configuring environment..."

if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Creating .env file..."
    cat > "$PROJECT_DIR/.env" << 'ENVEOF'
# OpenClaw Environment Configuration

# Server
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=sqlite:///openclaw.db
# For PostgreSQL: postgresql://user:password@localhost/openclaw

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# APIs & Services
TELEGRAM_BOT_TOKEN=your_telegram_token_here
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# KAIS Integration
KAIS_API_KEY=your_kais_api_key_here
KAIS_API_URL=http://localhost:9000

# Security
SECRET_KEY=your-secret-key-change-in-production
API_KEY=default-api-key

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/openclaw.log
ENVEOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# ============================================================================
# STEP 6: Database initialization
# ============================================================================

echo -e "${YELLOW}[6/8]${NC} Initializing database..."
python3 << 'DBEOF'
import os
from models import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)
print("✓ Database initialized")
DBEOF

# ============================================================================
# STEP 7: Display startup information
# ============================================================================

echo -e "${YELLOW}[7/8]${NC} Preparing startup information..."
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           🚀 OpenClaw Ready to Start! 🚀              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Project Directory:${NC} $PROJECT_DIR"
echo -e "${BLUE}🐍 Python Version:${NC} $PYTHON_VERSION"
echo -e "${BLUE}📦 Virtual Environment:${NC} $VENV_DIR"
echo -e "${BLUE}📝 Logs Directory:${NC} $LOG_DIR"
echo ""
echo -e "${BLUE}Configuration:${NC}"
echo -e "  → Host: 127.0.0.1"
echo -e "  → Port: $PORT"
echo -e "  → API: http://localhost:$PORT"
echo -e "  → Dashboard: http://localhost:$PORT/dashboard"
echo -e "  → Docs: http://localhost:$PORT/docs"
echo ""
echo -e "${YELLOW}Available Services:${NC}"
echo -e "  • FastAPI Server"
echo -e "  • WebSocket Real-time Updates"
echo -e "  • Browser Automation"
echo -e "  • Audio/Speech Processing"
echo -e "  • Telegram Bot Integration"
echo -e "  • KAIS External API"
echo ""

# ============================================================================
# STEP 8: Start FastAPI server
# ============================================================================

echo -e "${YELLOW}[8/8]${NC} Starting FastAPI server..."
echo ""
echo -e "${GREEN}✓ Starting on http://localhost:$PORT${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start with hot reload
python3 -m uvicorn main:app \
    --host 127.0.0.1 \
    --port $PORT \
    --reload \
    --log-level info

