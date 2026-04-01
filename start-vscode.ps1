# OpenClaw VS Code Development Environment Starter (Windows PowerShell)
# Purpose: Start VS Code with OpenClaw project, verify dependencies, setup Python environment

param(
    [switch]$CheckOnly,
    [switch]$InstallDeps,
    [switch]$Debug,
    [switch]$NoVenv,
    [switch]$TelegramBot,
    [switch]$HealthCheck,
    [switch]$Help
)

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ProjectDir ".venv"
$LogDir = Join-Path $ProjectDir "logs"
$LogFile = Join-Path $LogDir "vscode-start.log"

# Create logs directory
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

# Color functions
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error-Custom { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Warning-Custom { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }
function Write-Header { Write-Host "`n╔════════════════════════════════════════════════════════════╗`n║ $args`n╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Blue }

function Add-Log {
    param($Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $LogFile -Value "[$Timestamp] $Message"
}

function Show-Help {
    @"
OpenClaw VS Code Development Environment Starter

Usage:
  .\start-vscode.ps1 [OPTIONS]

Options:
  -Help              Show this help message
  -CheckOnly         Only check dependencies, don't start VS Code
  -InstallDeps       Install missing dependencies
  -Debug             Start in debug mode with verbose logging
  -NoVenv            Skip virtual environment setup
  -TelegramBot       Start with Telegram bot service
  -HealthCheck       Run health checks before starting

Examples:
  .\start-vscode.ps1                    # Start with all checks
  .\start-vscode.ps1 -CheckOnly         # Only verify setup
  .\start-vscode.ps1 -InstallDeps       # Install and start
"@
}

function Check-Command {
    param(
        [string]$Command,
        [string]$DisplayName = $Command
    )
    
    $cmd = Get-Command $Command -ErrorAction SilentlyContinue
    if ($cmd) {
        $version = & $Command --version 2>$null | Select-Object -First 1
        Write-Success "$DisplayName : $version"
        return $true
    } else {
        Write-Error-Custom "$DisplayName : NOT FOUND"
        return $false
    }
}

function Check-Dependencies {
    Write-Header "Checking Dependencies"
    
    $missing = 0
    
    if (-not (Check-Command python "Python 3")) { $missing++ }
    if (-not (Check-Command git "Git")) { $missing++ }
    if (-not (Check-Command code "VS Code")) { $missing++ }
    
    if ($missing -gt 0) {
        Write-Warning-Custom "Found $missing missing dependencies"
        return $false
    } else {
        Write-Success "All required dependencies found"
        return $true
    }
}

function Setup-Python-Venv {
    Write-Header "Setting Up Python Virtual Environment"
    
    if (Test-Path $VenvDir) {
        Write-Info "Virtual environment already exists at $VenvDir"
        return $true
    }
    
    Write-Info "Creating virtual environment..."
    python -m venv $VenvDir
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Virtual environment created"
    } else {
        Write-Error-Custom "Failed to create virtual environment"
        return $false
    }
    
    # Activate and upgrade pip
    & "$VenvDir\Scripts\Activate.ps1"
    python -m pip install --upgrade pip setuptools wheel --quiet
    
    Write-Success "pip upgraded"
    return $true
}

function Install-Python-Dependencies {
    Write-Header "Installing Python Dependencies"
    
    & "$VenvDir\Scripts\Activate.ps1"
    
    $reqFile = Join-Path $ProjectDir "requirements.txt"
    if (Test-Path $reqFile) {
        Write-Info "Installing packages from requirements.txt..."
        pip install -r $reqFile --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python packages installed"
            return $true
        } else {
            Write-Error-Custom "Failed to install some packages"
            return $false
        }
    } else {
        Write-Warning-Custom "requirements.txt not found"
        return $false
    }
}

function Setup-VSCode-Config {
    Write-Header "Setting Up VS Code Configuration"
    
    $vscodeDir = Join-Path $ProjectDir ".vscode"
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir | Out-Null
    }
    
    # Create launch.json
    $launchJson = @{
        version = "0.2.0"
        configurations = @(
            @{
                name = "Python: Telegram Bot"
                type = "python"
                request = "launch"
                program = "`${workspaceFolder}/telegram_bot_refactored.py"
                console = "integratedTerminal"
                justMyCode = $true
                env = @{
                    PYTHONUNBUFFERED = "1"
                }
                envFile = "`${workspaceFolder}/.openclaw.env"
            },
            @{
                name = "Python: Current File"
                type = "python"
                request = "launch"
                program = "`${file}"
                console = "integratedTerminal"
                justMyCode = $true
            }
        )
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path (Join-Path $vscodeDir "launch.json") -Value $launchJson
    Write-Success "launch.json created"
    
    # Create settings.json
    $settingsJson = @{
        "python.defaultInterpreterPath" = "`${workspaceFolder}/.venv/Scripts/python.exe"
        "python.linting.enabled" = $true
        "python.formatting.provider" = "black"
        "editor.formatOnSave" = $true
        "python.analysis.typeCheckingMode" = "basic"
        "files.exclude" = @{
            "**/__pycache__" = $true
            "**/*.pyc" = $true
        }
    } | ConvertTo-Json
    
    Set-Content -Path (Join-Path $vscodeDir "settings.json") -Value $settingsJson
    Write-Success "settings.json created"
}

function Run-Health-Checks {
    Write-Header "Running Health Checks"
    
    Write-Info "Checking Python modules..."
    & "$VenvDir\Scripts\Activate.ps1"
    
    python -c @"
import sys
required = ['telegram', 'openai', 'requests', 'python-dotenv']
for mod in required:
    try:
        __import__(mod.replace('-', '_'))
        print(f'✓ {mod}')
    except ImportError:
        print(f'✗ {mod}')
"@
    
    Write-Info "Checking project structure..."
    $requiredFiles = @(
        "telegram_bot_refactored.py",
        "config.py",
        "handlers.py",
        "ai_service.py",
        "system_prompt.py",
        "requirements.txt"
    )
    
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $ProjectDir $file
        if (Test-Path $filePath) {
            Write-Success $file
        } else {
            Write-Error-Custom "$file (missing)"
        }
    }
}

function Main {
    Write-Header "OpenClaw Development Environment"
    Add-Log "Starting OpenClaw VS Code setup"
    
    if ($Help) {
        Show-Help
        exit 0
    }
    
    # Check dependencies
    if (-not (Check-Dependencies)) {
        if ($InstallDeps) {
            Write-Info "Installing missing dependencies..."
            Write-Warning-Custom "Please install dependencies manually: Python, Git, VS Code"
        } else {
            Write-Error-Custom "Please install missing dependencies or use -InstallDeps"
            exit 1
        }
    }
    
    # Setup Python environment
    if (-not $NoVenv) {
        Setup-Python-Venv
        Install-Python-Dependencies
    }
    
    # Setup VS Code configuration
    Setup-VSCode-Config
    
    # Run health checks if requested
    if ($HealthCheck) {
        Run-Health-Checks
    }
    
    # Exit if only checking
    if ($CheckOnly) {
        Write-Success "Checks completed successfully"
        exit 0
    }
    
    # Start Telegram bot if requested
    if ($TelegramBot) {
        Write-Header "Starting Telegram Bot"
        & "$VenvDir\Scripts\Activate.ps1"
        Add-Log "Starting telegram_bot_refactored.py"
        Start-Process python -ArgumentList "telegram_bot_refactored.py" -WorkingDirectory $ProjectDir
        Start-Sleep -Seconds 2
    }
    
    # Open VS Code
    Write-Header "Opening VS Code"
    Add-Log "Opening VS Code with project directory: $ProjectDir"
    
    if ($Debug) {
        Write-Info "Starting VS Code in debug mode..."
        & code --log debug $ProjectDir
    } else {
        & code $ProjectDir
    }
    
    Write-Success "VS Code started successfully"
    Add-Log "OpenClaw development environment ready"
}

Main
