# OpenClaw Configuration Guide

## Quick Start

### 1. Environment Files

Two environment files are provided:

- **env.example** - Complete template with all available options and descriptions
- **.openclaw.env** - Minimal production config for systemd service

### 2. Setup Instructions

#### For Development
```bash
# Copy and edit the example file
cp env.example .env
nano .env  # Edit with your API keys
```

#### For Production (Systemd)
```bash
# Copy to systemd service location
sudo cp .openclaw.env /home/danijel-jd/.openclaw/openclaw.env
sudo chown danijel-jd:danijel-jd /home/danijel-jd/.openclaw/openclaw.env
sudo chmod 600 /home/danijel-jd/.openclaw/openclaw.env
```

---

## Network Configuration

Your system uses the local network:
- **IP Address**: 192.168.0.140
- **Subnet**: 255.255.255.0
- **Gateway**: 192.168.0.1
- **DNS**: 192.168.0.1
- **Broadcast**: 192.168.0.255

### Telegram Webhook Setup
```
Webhook URL: http://192.168.0.140/telegram-webhook
Webhook Port: 8787
Webhook Host: 127.0.0.1
Webhook Secret: !
```

---

## Telegram Bot Configuration

### Bot Details
- **Token**: `8767785519:AAGriBZlO7grk1kWeXouh3GqCYWs55kx3Ek`
- **Bot Name**: `@openvlawbababab_bot`
- **Stream Mode**: `partial` (chunked text responses)
- **Text Chunk Limit**: 15000 characters
- **API Timeout**: 500 seconds

### Webhook Configuration
The webhook receives Telegram updates on:
```
http://192.168.0.140/telegram-webhook
```

Set up with BotFather:
```
/setwebhook https://your_domain.com/telegram-webhook
```

For local network testing, configure port forwarding to 127.0.0.1:8787

### Required User Configuration
Add your Telegram user ID to enable bot access:
```env
TELEGRAM_ALLOWED_USERS=123456789
TELEGRAM_ADMIN_USERS=123456789
```

Get your Telegram user ID by:
1. Message the bot: `/start`
2. The bot will respond with your user ID

---

## API Keys Configuration

### Priority Ranking

#### Speech-to-Text (Transcription)
1. **Groq Whisper** (RECOMMENDED)
   - Free tier available
   - Fast and accurate
   - Set: `GROQ_API_KEY`
   - Get: https://console.groq.com

2. **Deepgram** (Fallback)
   - Free tier: 600 min/month
   - Set: `DEEPGRAM_API_KEY`
   - Get: https://console.deepgram.com

#### Text-to-Speech (Synthesis)
1. **ElevenLabs** (RECOMMENDED)
   - Free tier: 10K chars/month
   - Highest quality voices
   - Set: `ELEVENLABS_API_KEY`
   - Get: https://elevenlabs.io
   - Voice ID: `21m00Tcm4TlvDq8ikWAM` (Bella)

2. **Google Cloud TTS** (Premium)
   - Free tier: 1M chars/month (trial)
   - Set: `GOOGLE_API_KEY`
   - Get: https://cloud.google.com

3. **Azure Speech Services** (Professional)
   - Free tier: 5 audio hours/month
   - Set: `AZURE_SPEECH_KEY` and `AZURE_SPEECH_REGION`
   - Get: https://azure.microsoft.com

4. **System Espeak** (Fallback)
   - Unlimited, free
   - Lower quality but reliable
   - Install: `sudo apt install espeak`

#### Chat & AI
- **OpenAI**
  - Set: `OPENAI_API_KEY`
  - Model: `gpt-4-turbo-preview`
  - Get: https://platform.openai.com

### Getting API Keys

#### Groq (Recommended for STT)
1. Visit https://console.groq.com
2. Sign up with email or GitHub
3. Create new API key
4. Copy and paste into `GROQ_API_KEY`

#### ElevenLabs (Recommended for TTS)
1. Visit https://elevenlabs.io
2. Sign up (free account)
3. Go to "API Keys" section
4. Copy and paste into `ELEVENLABS_API_KEY`

#### OpenAI (For Chat)
1. Visit https://platform.openai.com
2. Sign up and add payment method
3. Create new API key
4. Copy and paste into `OPENAI_API_KEY`

---

## Security Configuration

### API Key Security
```env
# Use strong, random values
API_KEY=generate_with: openssl rand -hex 32
SECRET_KEY=generate_with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=generate_with: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### CORS Configuration
Whitelist trusted origins:
```env
CORS_ORIGINS=http://192.168.0.140:5000,http://127.0.0.1:5000,http://localhost:5000
```

### File Permissions (Production)
```bash
# Secure the environment file
chmod 600 /home/danijel-jd/.openclaw/openclaw.env

# Only read by the service user
chown danijel-jd:danijel-jd /home/danijel-jd/.openclaw/openclaw.env
```

---

## System Monitoring Configuration

### Health Check Alerts
```env
HEALTH_CHECK_INTERVAL=60              # Check system every 60 seconds
SYSTEM_ALERT_CPU_THRESHOLD=80         # Alert when CPU > 80%
SYSTEM_ALERT_MEMORY_THRESHOLD=85      # Alert when Memory > 85%
SYSTEM_ALERT_DISK_THRESHOLD=90        # Alert when Disk > 90%
```

### Logging Configuration
```env
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=/home/danijel-jd/.openclaw/openclaw.log
LOG_MAX_SIZE=10485760                 # 10 MB
LOG_BACKUP_COUNT=5                    # Keep 5 backups
```

---

## Database Configuration

### SQLite (Default)
```env
DATABASE_URL=sqlite:////home/danijel-jd/.openclaw/openclaw.db
```

### PostgreSQL (Optional)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/openclaw
```

### Create Database Directory
```bash
mkdir -p /home/danijel-jd/.openclaw
chmod 755 /home/danijel-jd/.openclaw
```

---

## Mobile Device Configuration

### iPhone 16 Pro Max Remote Access
```env
REMOTE_HOST=192.168.0.101           # Your iPhone's IP
REMOTE_PORT=5001
REMOTE_AUTH_TOKEN=your_token_here
```

---

## Systemd Service Integration

The environment file is automatically loaded by the systemd service:

```ini
[Service]
EnvironmentFile=-/home/danijel-jd/.openclaw/openclaw.env
ExecStart=/usr/bin/env python3 /home/danijel-jd/.openclaw/openclaw_dashboard.py
```

### Verify Configuration
```bash
# Check if service can read env file
sudo systemctl cat openclaw

# View active environment
sudo systemctl show openclaw -p Environment

# Check service logs
journalctl -u openclaw -f
```

---

## Troubleshooting

### API Key Issues
```bash
# Test API connectivity
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.groq.com/health

# Check environment variables are set
env | grep -i openclaw
env | grep -i telegram
```

### Telegram Bot Not Responding
```bash
# Verify token format
# Should be: token_number:token_string

# Check webhook status
python3 -c "from telegram import Bot; b = Bot('TOKEN'); print(b.get_webhook_info())"
```

### Systemd Service Issues
```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart openclaw

# View service status
systemctl status openclaw

# View detailed logs
journalctl -u openclaw -n 100
```

---

## Configuration Validation

Run the configuration validator:
```bash
python3 scripts/validate_config.py
```

This checks:
- All required API keys are set
- API keys have valid format
- Network configuration is correct
- File permissions are secure
- Database connection works

---

## Next Steps

1. **Set up API Keys**
   - Get at least GROQ_API_KEY and ELEVENLABS_API_KEY
   - Optional: OPENAI_API_KEY for better chat

2. **Configure Telegram**
   - Set TELEGRAM_BOT_TOKEN
   - Set TELEGRAM_ALLOWED_USERS with your ID

3. **Deploy Service**
   ```bash
   sudo systemctl enable openclaw
   sudo systemctl start openclaw
   ```

4. **Verify Setup**
   ```bash
   # Check service is running
   systemctl status openclaw
   
   # Test dashboard
   curl http://192.168.0.140:5000/health
   
   # Test Telegram bot
   /start (message the bot)
   ```

---

## Support

For detailed documentation, see:
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Installation & deployment
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API endpoints
- [AUDIO_INTEGRATION.md](./AUDIO_INTEGRATION.md) - Audio setup
- [README.md](./README.md) - General information
