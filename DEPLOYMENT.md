# OpenClaw Deployment Guide

## System Requirements

### Desktop (Linux Mint 22.2)
- Python 3.10+
- Node.js 18+ (for dashboard frontend)
- 4GB RAM minimum
- 10GB free disk space
- Network connectivity (for Telegram, APIs)

### Mobile (iPhone 16 Pro Max)
- iOS 16+
- Safari or compatible browser
- Network connectivity
- Microphone for voice commands
- Speaker for audio output

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/jokicdanijel/web-automation2-backend.git
cd web-automation2-backend
```

### 2. Create Virtual Environment (Python)
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (if using dashboard)
npm install  # in html directory if needed
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Audio & Speech Services
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=eastus

# Server Configuration
API_BASE_URL=http://localhost:8000
DASHBOARD_PORT=3000
BACKEND_PORT=8000
ENVIRONMENT=development  # development, staging, production

# Optional: Database
DATABASE_URL=postgresql://user:password@localhost:5432/openclaw
```

### 5. Get API Keys

#### Telegram Bot Token
1. Open Telegram and find @BotFather
2. Create new bot with `/newbot`
3. Copy the bot token

#### OpenAI API Key
1. Go to https://platform.openai.com
2. Create API key
3. Copy and save securely

#### Groq API Key (Free STT)
1. Go to https://console.groq.com
2. Sign up for free account
3. Get API key

#### ElevenLabs API Key (Free TTS)
1. Go to https://elevenlabs.io
2. Create account (free tier: 10K chars/month)
3. Get API key

## Running the System

### Option 1: Development Mode

#### Terminal 1: Start Telegram Bot
```bash
source venv/bin/activate
python3 telegram_bot.py
```

#### Terminal 2: Start Dashboard Server
```bash
cd html
# If you have Node.js
npm install
npm run dev

# Or use Python simple server
python3 -m http.server 3000
```

#### Terminal 3: Start Backend API
```bash
# If using FastAPI
pip install fastapi uvicorn
python3 -c "from api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

### Option 2: Using systemd (Production - Linux Mint)

#### 1. Create systemd service for Telegram Bot
Create `/etc/systemd/system/openclaw-telegram.service`:

```ini
[Unit]
Description=OpenClaw Telegram Bot
After=network.target

[Service]
Type=simple
User=danijel-jd
WorkingDirectory=/home/danijel-jd/web-automation2-backend
Environment="PATH=/home/danijel-jd/web-automation2-backend/venv/bin"
EnvironmentFile=/home/danijel-jd/.openclaw/openclaw.env
ExecStart=/home/danijel-jd/web-automation2-backend/venv/bin/python3 telegram_bot.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 2. Create systemd service for Dashboard
Create `/etc/systemd/system/openclaw-dashboard.service`:

```ini
[Unit]
Description=OpenClaw Dashboard
After=network.target

[Service]
Type=simple
User=danijel-jd
WorkingDirectory=/home/danijel-jd/web-automation2-backend/html
EnvironmentFile=/home/danijel-jd/.openclaw/openclaw.env
ExecStart=/usr/bin/env python3 -m http.server 3000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 3. Enable and start services
```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-telegram.service
sudo systemctl enable openclaw-dashboard.service
sudo systemctl start openclaw-telegram.service
sudo systemctl start openclaw-dashboard.service
```

#### 4. Check status
```bash
sudo systemctl status openclaw-telegram.service
sudo systemctl status openclaw-dashboard.service
sudo journalctl -u openclaw-telegram.service -f
```

## Accessing the System

### From Linux Mint Desktop
1. Open browser to `http://localhost:3000`
2. Or `http://127.0.0.1:3000`

### From iPhone 16 Pro Max
1. Find your Linux Mint IP: `hostname -I`
2. Open Safari and navigate to `http://YOUR_IP:3000`
3. Or use Telegram bot directly with @YourBotName

### Telegram Access
1. Search for your bot in Telegram
2. Send `/start` to initialize
3. Use commands:
   - `/status` - System status
   - `/health` - Health check
   - `/automate` - Start automation
   - `/help` - Show help
   - `/chat` - Chat mode

## System Prompts

The system uses comprehensive prompts for AI behavior:

```bash
# Generate and display prompts
python3 system_prompt.py

# Prompts are saved to:
# /tmp/openclaw_system_prompt.json
# /tmp/openclaw_telegram_prompt.json
# /tmp/openclaw_health_prompt.json
```

## Monitoring

### Check Services Status
```bash
# Check if services are running
ps aux | grep telegram_bot
ps aux | grep python

# Check system health
top -b -n 1 | head -20
free -h
df -h
```

### View Logs
```bash
# Telegram bot logs
sudo journalctl -u openclaw-telegram.service -f

# Dashboard logs
sudo journalctl -u openclaw-dashboard.service -f

# All OpenClaw logs
sudo journalctl -u openclaw* -f
```

### Telegram Health Monitoring
Send `/health` to your bot in Telegram for system health report.

## Troubleshooting

### Bot not responding
1. Check API keys in `.env`
2. Verify Telegram token is valid
3. Check logs: `sudo journalctl -u openclaw-telegram.service -f`
4. Restart service: `sudo systemctl restart openclaw-telegram.service`

### Dashboard not accessible
1. Check if port 3000 is in use: `sudo lsof -i :3000`
2. Verify dashboard service is running
3. Try accessing from localhost first
4. Check firewall: `sudo ufw status`

### API errors
1. Verify all API keys are set in `.env`
2. Check internet connectivity
3. Test individual APIs separately
4. Check rate limits on API providers

### Audio issues
1. Verify Groq/Deepgram API keys
2. Check audio format compatibility (WAV, MP3)
3. Test STT with: `curl -X POST http://localhost:8000/api/speech-to-text`
4. Test TTS with: `curl -X POST http://localhost:8000/api/text-to-speech`

## Performance Optimization

### For Desktop (Linux Mint)
- Adjust CPU/Memory allocation
- Enable hardware acceleration
- Cache API responses
- Use local providers when available

### For Mobile (iPhone)
- Optimize image sizes
- Compress JSON responses
- Minimize data transfer
- Use responsive design

## Security Best Practices

1. **Never commit API keys** - Use `.env` and `.gitignore`
2. **Use HTTPS** - Enable SSL in production
3. **Validate inputs** - Check all user inputs
4. **Rate limiting** - Prevent abuse
5. **Audit logging** - Log all actions
6. **Regular updates** - Keep dependencies updated

```bash
# Check for security vulnerabilities
pip audit
npm audit  # if using npm packages
```

## Backup & Recovery

```bash
# Backup configuration
cp .env .env.backup
cp -r venv venv.backup

# Backup logs
mkdir -p backups/logs
sudo journalctl -u openclaw* > backups/logs/openclaw_$(date +%Y%m%d).log
```

## Updates & Maintenance

```bash
# Update Python dependencies
pip install --upgrade -r requirements.txt

# Check for outdated packages
pip list --outdated

# Clean up
pip cache purge
rm -rf __pycache__ .pytest_cache
```

## Production Deployment

For production environments:

1. Use strong, randomly generated API keys
2. Configure HTTPS/SSL
3. Set up database (PostgreSQL recommended)
4. Use process manager (systemd, supervisord)
5. Configure proper logging and monitoring
6. Set up automated backups
7. Enable rate limiting
8. Implement authentication
9. Use environment-specific configs
10. Monitor uptime and performance

## Support & Troubleshooting

For detailed information on each component:
- Audio/Speech: See [AUDIO_INTEGRATION.md](./AUDIO_INTEGRATION.md)
- Dashboard: See [html/dashboard.html](./html/dashboard.html)
- API Documentation: See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- Telegram Bot: See [telegram_bot.py](./telegram_bot.py)

For additional support, check logs and ensure all API keys are properly configured.
