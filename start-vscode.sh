#!/bin/bash

##############################################################################
# OpenClaw VS Code Development Environment Starter
# 
# Purpose: Start VS Code with OpenClaw project, verify dependencies,
#          setup Python environment, and configure debugging
#
# Usage: ./start-vscode.sh [options]
#        ./start-vscode.sh --help
##############################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
LOG_FILE="${PROJECT_DIR}/logs/vscode-start.log"
LOG_DIR="${PROJECT_DIR}/logs"

# Ensure logs directory exists
mkdir -p "$LOG_DIR"

##############################################################################
# Helper Functions
##############################################################################

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

show_help() {
    cat << EOF
${BLUE}OpenClaw VS Code Development Environment Starter${NC}

${GREEN}Usage:${NC}
  ./start-vscode.sh [OPTIONS]

${GREEN}Options:${NC}
  --help              Show this help message
  --check-only        Only check dependencies, don't start VS Code
  --install-deps      Install missing dependencies
  --debug             Start in debug mode with verbose logging
  --no-venv           Skip virtual environment setup
  --telegram-bot      Start with Telegram bot service
  --health-check      Run health checks before starting

${GREEN}Examples:${NC}
  ./start-vscode.sh                    # Start with all checks
  ./start-vscode.sh --check-only       # Only verify setup
  ./start-vscode.sh --install-deps     # Install and start
  ./start-vscode.sh --debug            # Debug mode

${GREEN}Environment:${NC}
  - Python 3.8+
  - VS Code with Python extension
  - Git
  - Virtual environment support

EOF
}

##############################################################################
# Dependency Checks
##############################################################################

check_command() {
    local cmd=$1
    local display_name=${2:-$cmd}
    
    if command -v "$cmd" &> /dev/null; then
        local version=$("$cmd" --version 2>/dev/null | head -n1 || echo "installed")
        print_success "${display_name}: ${version}"
        return 0
    else
        print_error "${display_name}: NOT FOUND"
        return 1
    fi
}

check_dependencies() {
    print_header "Checking Dependencies"
    
    local missing=0
    
    check_command "python3" "Python 3" || missing=$((missing + 1))
    check_command "git" "Git" || missing=$((missing + 1))
    check_command "code" "VS Code" || missing=$((missing + 1))
    check_command "pip3" "pip3" || missing=$((missing + 1))
    
    if [ $missing -gt 0 ]; then
        print_warning "Found $missing missing dependencies"
        return 1
    else
        print_success "All required dependencies found"
        return 0
    fi
}

##############################################################################
# Python Environment Setup
##############################################################################

setup_python_venv() {
    print_header "Setting Up Python Virtual Environment"
    
    if [ -d "$VENV_DIR" ]; then
        print_info "Virtual environment already exists at ${VENV_DIR}"
        return 0
    fi
    
    print_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        return 1
    fi
    
    # Activate and upgrade pip
    source "$VENV_DIR/bin/activate"
    python -m pip install --upgrade pip setuptools wheel --quiet
    
    print_success "pip upgraded"
}

install_python_dependencies() {
    print_header "Installing Python Dependencies"
    
    source "$VENV_DIR/bin/activate"
    
    if [ -f "${PROJECT_DIR}/requirements.txt" ]; then
        print_info "Installing packages from requirements.txt..."
        pip install -r "${PROJECT_DIR}/requirements.txt" --quiet
        
        if [ $? -eq 0 ]; then
            print_success "Python packages installed"
        else
            print_error "Failed to install some packages"
            return 1
        fi
    else
        print_warning "requirements.txt not found"
    fi
}

##############################################################################
# VS Code Configuration
##############################################################################

setup_vscode_config() {
    print_header "Setting Up VS Code Configuration"
    
    local vscode_dir="${PROJECT_DIR}/.vscode"
    mkdir -p "$vscode_dir"
    
    # Create launch.json for debugging
    cat > "${vscode_dir}/launch.json" << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Telegram Bot",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/telegram_bot_refactored.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "env": {
                "PYTHONUNBUFFERED": "1"
            },
            "envFile": "${workspaceFolder}/.openclaw.env"
        },
        {
            "name": "Python: System Prompt",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/system_prompt.py",
            "console": "integratedTerminal",
            "justMyCode": true
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
EOF
    
    print_success "launch.json created"
    
    # Create settings.json for Python development
    cat > "${vscode_dir}/settings.json" << 'EOF'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.pylintPath": "${workspaceFolder}/.venv/bin/pylint",
    "python.formatting.provider": "black",
    "python.formatting.blackPath": "${workspaceFolder}/.venv/bin/black",
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python",
    "[python]": {
        "editor.defaultFormatter": "ms-python.python",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    },
    "python.analysis.extraPaths": ["${workspaceFolder}"],
    "python.analysis.typeCheckingMode": "basic",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true,
        "**/.coverage": true
    },
    "search.exclude": {
        "**/__pycache__": true,
        ".venv": true
    }
}
EOF
    
    print_success "settings.json created"
    
    # Create extensions.json with recommended extensions
    cat > "${vscode_dir}/extensions.json" << 'EOF'
{
    "recommendations": [
        "ms-python.python",
        "ms-python.debugpy",
        "ms-python.black-formatter",
        "ms-python.pylint",
        "ms-python.mypy-type-checker",
        "GitHub.copilot",
        "ms-vscode.makefile-tools",
        "ms-vscode.cpptools",
        "REST Client",
        "Thunder Client",
        "GitLens",
        "Better Comments",
        "Error Lens"
    ]
}
EOF
    
    print_success "extensions.json created"
}

##############################################################################
# Environment File Setup
##############################################################################

setup_env_file() {
    print_header "Setting Up Environment Variables"
    
    local env_file="${PROJECT_DIR}/.openclaw.env"
    
    if [ -f "$env_file" ]; then
        print_info "Environment file already exists"
        print_warning "Make sure to update with your API keys:"
        echo ""
        echo "  - TELEGRAM_BOT_TOKEN"
        echo "  - GROQ_API_KEY (for speech-to-text)"
        echo "  - ELEVENLABS_API_KEY (for text-to-speech)"
        echo "  - OPENAI_API_KEY (optional, for chat features)"
        echo ""
    else
        print_warning "Environment file not found at ${env_file}"
        print_info "Copy env.example and configure it:"
        echo "  cp env.example .openclaw.env"
    fi
}

##############################################################################
# Health Checks
##############################################################################

run_health_checks() {
    print_header "Running Health Checks"
    
    # Check Python modules
    print_info "Checking Python modules..."
    source "$VENV_DIR/bin/activate" 2>/dev/null || true
    
    python3 << 'PYEOF'
import sys
required_modules = ['telegram', 'openai', 'requests', 'python-dotenv']
missing = []

for module in required_modules:
    try:
        __import__(module.replace('-', '_'))
        print(f"✓ {module}")
    except ImportError:
        print(f"✗ {module}")
        missing.append(module)

if missing:
    print(f"\nMissing: {', '.join(missing)}")
    sys.exit(1)
PYEOF
    
    # Check project structure
    print_info "Checking project structure..."
    local required_files=(
        "telegram_bot_refactored.py"
        "config.py"
        "handlers.py"
        "ai_service.py"
        "system_prompt.py"
        "requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "${PROJECT_DIR}/${file}" ]; then
            print_success "${file}"
        else
            print_error "${file} (missing)"
        fi
    done
}

##############################################################################
# Main Execution
##############################################################################

main() {
    local check_only=false
    local install_deps=false
    local debug=false
    local skip_venv=false
    local start_telegram=false
    local health_check=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_help
                exit 0
                ;;
            --check-only)
                check_only=true
                shift
                ;;
            --install-deps)
                install_deps=true
                shift
                ;;
            --debug)
                debug=true
                shift
                ;;
            --no-venv)
                skip_venv=true
                shift
                ;;
            --telegram-bot)
                start_telegram=true
                shift
                ;;
            --health-check)
                health_check=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header "OpenClaw Development Environment"
    log "INFO" "Starting OpenClaw VS Code setup"
    
    # Check dependencies
    if ! check_dependencies; then
        if [ "$install_deps" = true ]; then
            print_info "Installing missing dependencies..."
            sudo apt-get update && sudo apt-get install -y python3 python3-pip git
        else
            print_error "Please install missing dependencies or use --install-deps"
            exit 1
        fi
    fi
    
    # Setup Python environment
    if [ "$skip_venv" = false ]; then
        setup_python_venv
        install_python_dependencies
    fi
    
    # Setup VS Code configuration
    setup_vscode_config
    setup_env_file
    
    # Run health checks if requested
    if [ "$health_check" = true ]; then
        run_health_checks
    fi
    
    # Exit if only checking
    if [ "$check_only" = true ]; then
        print_success "Checks completed successfully"
        exit 0
    fi
    
    # Start services
    if [ "$start_telegram" = true ]; then
        print_header "Starting Telegram Bot"
        source "$VENV_DIR/bin/activate"
        log "INFO" "Starting telegram_bot_refactored.py"
        python telegram_bot_refactored.py &
        sleep 2
    fi
    
    # Open VS Code
    print_header "Opening VS Code"
    log "INFO" "Opening VS Code with project directory: ${PROJECT_DIR}"
    
    if [ "$debug" = true ]; then
        print_info "Starting VS Code in debug mode..."
        code --log debug "$PROJECT_DIR"
    else
        code "$PROJECT_DIR"
    fi
    
    print_success "VS Code started successfully"
    log "INFO" "OpenClaw development environment ready"
}

# Run main function
main "$@"
