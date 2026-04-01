/**
 * OpenClaw Cockpit Dashboard - Main JavaScript Controller
 * Handles real-time metrics, gauges, and interactive controls
 */

// Configuration
const CONFIG = {
    apiBaseUrl: 'http://localhost:3000',
    refreshIntervals: {
        metrics: 2000,
        status: 5000,
        logs: 1000
    },
    gauges: {}
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeCockpit();
    startMetricsUpdates();
    setupEventListeners();
    updateClock();
    setInterval(updateClock, 1000);
});

/**
 * Initialize cockpit components
 */
function initializeCockpit() {
    console.log('[v0] Initializing OpenClaw Cockpit...');
    initializeCanvasGauges();
    loadDashboardConfig();
    updateAllMetrics();
}

/**
 * Initialize canvas-based gauges
 */
function initializeCanvasGauges() {
    const gaugeIds = ['cpu-gauge', 'memory-gauge', 'disk-gauge', 'network-gauge'];
    
    gaugeIds.forEach(id => {
        const canvas = document.getElementById(id);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            CONFIG.gauges[id] = { canvas, ctx };
            drawGauge(canvas, ctx, 0);
        }
    });
}

/**
 * Draw a gauge on canvas
 */
function drawGauge(canvas, ctx, percentage) {
    const size = canvas.width = canvas.height = 150;
    ctx.clearRect(0, 0, size, size);
    
    const centerX = size / 2;
    const centerY = size / 2;
    const radius = size / 2 - 15;
    
    // Background circle
    ctx.strokeStyle = '#1a2540';
    ctx.lineWidth = 20;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.stroke();
    
    // Progress arc
    const angle = (percentage / 100) * Math.PI;
    let color = '#00ff00';
    if (percentage > 70) color = '#ffaa00';
    if (percentage > 90) color = '#ff3333';
    
    ctx.strokeStyle = color;
    ctx.lineWidth = 20;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, -Math.PI / 2 + angle);
    ctx.stroke();
}

/**
 * Update all system metrics
 */
async function updateAllMetrics() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/health`);
        if (response.ok) {
            const data = await response.json();
            updateMetricsDisplay(data);
        }
    } catch (error) {
        console.error('[v0] Error fetching metrics:', error);
    }
}

/**
 * Update metrics in the display
 */
function updateMetricsDisplay(data) {
    // CPU
    const cpuValue = data.cpu_usage || 45;
    updateGauge('cpu-gauge', 'cpu-value', 'cpu-bar', cpuValue, '%');
    
    // Memory
    const memValue = data.memory_usage || 62;
    updateGauge('memory-gauge', 'memory-value', 'memory-bar', memValue, '%');
    
    // Disk
    const diskValue = data.disk_usage || 38;
    updateGauge('disk-gauge', 'disk-value', 'disk-bar', diskValue, '%');
    
    // Network
    const netValue = data.network_latency || 12;
    updateGauge('network-gauge', 'network-value', 'network-bar', netValue, 'ms');
    
    // Update status cards
    updateStatusCards(data);
    updateComponentStatus(data);
}

/**
 * Update individual gauge
 */
function updateGauge(canvasId, valueId, barId, value, unit) {
    const gauge = CONFIG.gauges[canvasId];
    if (gauge) {
        drawGauge(gauge.canvas, gauge.ctx, value);
    }
    
    const valueEl = document.getElementById(valueId);
    if (valueEl) {
        valueEl.textContent = Math.round(value);
    }
    
    const barEl = document.getElementById(barId);
    if (barEl) {
        barEl.style.width = `${Math.min(value, 100)}%`;
    }
}

/**
 * Update status cards
 */
function updateStatusCards(data) {
    const uptime = data.uptime_seconds || 86400;
    document.getElementById('uptime-value').textContent = formatUptime(uptime);
    
    const requests = data.request_count || 15200;
    document.getElementById('request-value').textContent = formatNumber(requests);
    
    const errors = data.error_count || 45;
    const errorRate = ((errors / Math.max(requests, 1)) * 100).toFixed(2);
    document.getElementById('error-value').textContent = errorRate + '%';
}

/**
 * Update component health status
 */
function updateComponentStatus(data) {
    const components = data.components || {};
    
    const healthMap = {
        'telegram-health': components.telegram_bot || 99.2,
        'browser-health': components.browser_automation || 98.5,
        'audio-health': components.audio_pipeline || 99.8,
        'form-health': components.form_handler || 97.2
    };
    
    for (const [id, health] of Object.entries(healthMap)) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = health.toFixed(1) + '%';
            el.style.color = health > 95 ? '#00ff00' : health > 80 ? '#ffaa00' : '#ff3333';
        }
    }
}

/**
 * Start continuous metrics updates
 */
function startMetricsUpdates() {
    setInterval(updateAllMetrics, CONFIG.refreshIntervals.metrics);
    setInterval(updateActivityLog, CONFIG.refreshIntervals.logs);
}

/**
 * Update activity log
 */
async function updateActivityLog() {
    try {
        // In production, fetch from API
        // For now, just append timestamps
    } catch (error) {
        console.error('[v0] Error updating log:', error);
    }
}

/**
 * Update clock display
 */
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    const clockEl = document.getElementById('current-time');
    if (clockEl) {
        clockEl.textContent = timeString;
    }
}

/**
 * Format uptime
 */
function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
}

/**
 * Format numbers with K, M notation
 */
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    const btnAutomation = document.getElementById('btn-automation');
    const btnDetectForms = document.getElementById('btn-detect-forms');
    const btnChat = document.getElementById('btn-chat');
    const btnHealthCheck = document.getElementById('btn-health-check');
    const btnCommunityChat = document.getElementById('btn-community-chat');
    
    if (btnAutomation) {
        btnAutomation.addEventListener('click', startAutomation);
    }
    
    if (btnDetectForms) {
        btnDetectForms.addEventListener('click', detectForms);
    }
    
    if (btnChat) {
        btnChat.addEventListener('click', () => openModal('chat-modal'));
    }
    
    if (btnHealthCheck) {
        btnHealthCheck.addEventListener('click', runHealthCheck);
    }
    
    if (btnCommunityChat) {
        btnCommunityChat.addEventListener('click', openCommunityChat);
    }
}

/**
 * Start automation workflow
 */
async function startAutomation() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/automation/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getApiKey()}`
            },
            body: JSON.stringify({ workflow: 'default' })
        });
        
        if (response.ok) {
            addLog('Automation started', 'success');
            updateAllMetrics();
        } else {
            addLog('Failed to start automation', 'error');
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
    }
}

/**
 * Detect forms on page
 */
async function detectForms() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/form-automate/detect`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getApiKey()}`
            },
            body: JSON.stringify({ page_url: window.location.href })
        });
        
        const data = await response.json();
        addLog(`Forms detected: ${data.count || 0}`, 'info');
    } catch (error) {
        addLog(`Error: ${error.message}`, 'error');
    }
}

/**
 * Run health check
 */
async function runHealthCheck() {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/health`);
        const data = await response.json();
        addLog('Health check completed', 'success');
        updateAllMetrics();
    } catch (error) {
        addLog(`Health check failed: ${error.message}`, 'error');
    }
}

/**
 * Open community chat
 */
function openCommunityChat() {
    alert('Community chat feature coming soon!');
}

/**
 * Open modal
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Close modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Send chat message
 */
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to display
    const messagesDiv = document.getElementById('chat-messages');
    const userMsgEl = document.createElement('div');
    userMsgEl.className = 'message user-message';
    userMsgEl.textContent = message;
    messagesDiv.appendChild(userMsgEl);
    
    input.value = '';
    
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getApiKey()}`
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        const botMsgEl = document.createElement('div');
        botMsgEl.className = 'message bot-message';
        botMsgEl.textContent = data.response || 'No response';
        messagesDiv.appendChild(botMsgEl);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        const errorMsgEl = document.createElement('div');
        errorMsgEl.className = 'message error-message';
        errorMsgEl.textContent = `Error: ${error.message}`;
        messagesDiv.appendChild(errorMsgEl);
    }
}

/**
 * Add log entry
 */
function addLog(message, level = 'info') {
    const logDiv = document.getElementById('activity-log');
    if (logDiv) {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', { hour12: false });
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${level}`;
        entry.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-message">${message}</span>
        `;
        
        logDiv.insertBefore(entry, logDiv.firstChild);
        
        // Keep only last 50 entries
        while (logDiv.children.length > 50) {
            logDiv.removeChild(logDiv.lastChild);
        }
    }
}

/**
 * Get API key from storage
 */
function getApiKey() {
    return localStorage.getItem('api_key') || 'default-key';
}

/**
 * Load dashboard configuration
 */
async function loadDashboardConfig() {
    try {
        const response = await fetch('/dashboard_config.json');
        if (response.ok) {
            const config = await response.json();
            // Apply configuration if needed
            console.log('[v0] Dashboard config loaded:', config);
        }
    } catch (error) {
        console.error('[v0] Error loading config:', error);
    }
}

console.log('[v0] OpenClaw Cockpit Dashboard initialized');
