# VS Code Development Environment Setup for OpenClaw

## Quick Start

### Linux / macOS

```bash
# Make script executable
chmod +x start-vscode.sh

# Run with default options
./start-vscode.sh

# Or with specific options
./start-vscode.sh --install-deps      # Install missing dependencies
./start-vscode.sh --health-check      # Run health checks
./start-vscode.sh --telegram-bot      # Start Telegram bot service
./start-vscode.sh --debug             # Debug mode
./start-vscode.sh --check-only        # Only verify setup
```

### Windows (PowerShell)

```powershell
# Run with default options
.\start-vscode.ps1

# Or with specific options
.\start-vscode.ps1 -InstallDeps       # Install missing dependencies
.\start-vscode.ps1 -HealthCheck       # Run health checks
.\start-vscode.ps1 -TelegramBot       # Start Telegram bot service
.\start-vscode.ps1 -Debug             # Debug mode
.\start-vscode.ps1 -CheckOnly         # Only verify setup
.\start-vscode.ps1 -Help              # Show help
```

## What the Start Scripts Do

### Automated Setup Process

1. **Dependency Check** ✓
   - Verifies Python 3.8+
   - Checks for VS Code installation
   - Validates Git availability

2. **Python Virtual Environment** ✓
   - Creates `.venv` in project directory
   - Activates virtual environment
   - Upgrades pip, setuptools, wheel

3. **Python Dependencies** ✓
   - Installs packages from `requirements.txt`
   - All telegram, AI, and audio libraries

4. **VS Code Configuration** ✓
   - Creates `.vscode/launch.json` - Debug configurations
   - Creates `.vscode/settings.json` - Python settings
   - Creates `.vscode/extensions.json` - Recommended extensions

5. **Environment Variables** ✓
   - Verifies `.openclaw.env` exists
   - Reminds you to update API keys

6. **Health Checks** (optional) ✓
   - Validates Python module imports
   - Checks project file structure

7. **Services** (optional) ✓
   - Starts Telegram bot if `--telegram-bot` flag used
   - Opens VS Code automatically

## VS Code Configuration Files

### launch.json

Provides three pre-configured debug configurations:

1. **Python: Telegram Bot**
   - Launches `telegram_bot_refactored.py`
   - Loads environment from `.openclaw.env`
   - Integrated terminal output
   - Uses all environment variables

2. **Python: System Prompt**
   - Launches `system_prompt.py`
   - Testing system prompt generation

3. **Python: Current File**
   - Debug any file in the editor
   - Select this and press F5 to debug

### settings.json

Configures Python development environment:

- Python interpreter: Uses `.venv/bin/python`
- Linting: Pylint enabled
- Formatting: Black formatter
- Format on save: Enabled
- Type checking: Basic mode enabled
- Auto-organize imports

### extensions.json

Recommends VS Code extensions for Python development:

- **ms-python.python** - Official Python extension
- **ms-python.debugpy** - Debug support
- **ms-python.black-formatter** - Code formatter
- **ms-python.pylint** - Linting
- **GitHub.copilot** - AI code completion
- **GitLens** - Git history
- **Better Comments** - Comment formatting
- **Error Lens** - Inline error display

## Manual Setup (if needed)

If you prefer manual setup or the scripts don't work:

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate (Linux/macOS)
source .venv/bin/activate
# Or Windows
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp env.example .openclaw.env

# 5. Edit with your API keys
nano .openclaw.env

# 6. Open VS Code
code .
```

## Environment Variables Required

Create `.openclaw.env` with these keys:

```env
# Telegram Bot (REQUIRED)
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_BOT_NAME=openvlawbababab_bot

# Speech Services (Optional)
GROQ_API_KEY=your_groq_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
DEEPGRAM_API_KEY=your_deepgram_key_here

# AI Services (Optional)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# Server Configuration
SERVER_HOST=127.0.0.1
SERVER_PORT=8787
WEBHOOK_HOST=192.168.0.140
WEBHOOK_PORT=8787
```

## Debugging

### Run Health Checks

```bash
./start-vscode.sh --health-check
```

Verifies:
- All Python modules installed
- Required project files present
- Configuration files exist

### Debug Mode

```bash
./start-vscode.sh --debug
```

Enables:
- Verbose logging
- VS Code debug output
- Detailed error messages

### View Logs

```bash
tail -f logs/vscode-start.log
```

## Troubleshooting

### Python Not Found

**Linux/macOS:**
```bash
sudo apt-get install python3 python3-pip
# or on macOS
brew install python3
```

**Windows:**
- Download from python.org
- Add to PATH during installation

### VS Code Extension Issues

```bash
# Install recommended extensions automatically
code --install-extension ms-python.python
code --install-extension ms-python.debugpy
# ... etc
```

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf .venv
./start-vscode.sh
```

### Permission Denied (Linux/macOS)

```bash
chmod +x start-vscode.sh
chmod +x start-vscode.ps1
```

## Directory Structure After Setup

```
openclaw-project/
├── .venv/                    # Virtual environment (auto-created)
├── .vscode/                  # VS Code config (auto-created)
│   ├── launch.json          # Debug configurations
│   ├── settings.json        # Python settings
│   └── extensions.json      # Recommended extensions
├── logs/                     # Log files (auto-created)
│   └── vscode-start.log     # Startup log
├── start-vscode.sh          # Linux/macOS startup script
├── start-vscode.ps1         # Windows startup script
├── .openclaw.env            # Environment variables (needs setup)
├── requirements.txt         # Python dependencies
├── telegram_bot_refactored.py
├── config.py
├── handlers.py
├── ai_service.py
└── system_prompt.py
```

## Keyboard Shortcuts in VS Code

### Python Development

| Shortcut | Action |
|----------|--------|
| F5 | Start debugging |
| F10 | Step over |
| F11 | Step into |
| Shift+F11 | Step out |
| Ctrl+Shift+D | Debug panel |
| Ctrl+` | Terminal |
| Ctrl+Shift+F10 | Run current file |
| Alt+Shift+F | Format document |
| Ctrl+Shift+O | Go to symbol |

## Tips & Best Practices

### Always Use Virtual Environment

Keeps project dependencies isolated:

```bash
# On project start
source .venv/bin/activate

# On project end
deactivate
```

### Keep Environment Variables Secret

Never commit `.openclaw.env` to git:

```bash
# Already in .gitignore
*.env
.venv/
logs/
__pycache__/
```

### Use Debug Points

Click line numbers to set breakpoints, then press F5.

### Watch Expressions

In debug panel, add variables to watch their values change in real-time.

### Python Path

Both scripts ensure proper Python path by using virtual environment.

## Support

For issues:

1. Run with `--health-check`
2. Check `logs/vscode-start.log`
3. Verify API keys in `.openclaw.env`
4. Ensure all dependencies installed: `pip list`
5. Check Python version: `python --version`

## Next Steps

1. Run the startup script
2. Wait for VS Code to open
3. Install recommended extensions when prompted
4. Set breakpoints and start debugging
5. Check console output and debug panel

Happy coding!
