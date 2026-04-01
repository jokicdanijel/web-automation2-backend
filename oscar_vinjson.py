"""
OSCAR-VinJSON Format Generator for OpenClaw
Complete vehicle/automation telemetry and metrics in OSCAR standard format
"""

import json
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import hashlib
import uuid


@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    uptime_seconds: int
    active_processes: int
    request_count: int
    error_count: int
    last_error: Optional[str] = None


@dataclass
class ComponentStatus:
    """Individual component status"""
    name: str
    status: str  # active, inactive, error, maintenance
    health_percentage: float
    response_time_ms: float
    operations_count: int
    last_updated: str


@dataclass
class ModuleInfo:
    """Module/skill information"""
    module_id: str
    name: str
    version: str
    status: str
    capabilities: List[str]
    dependencies: List[str]


class OSCARVinJSONGenerator:
    """Generates complete OSCAR-VinJSON format telemetry"""
    
    def __init__(self, system_name: str = "OpenClaw"):
        self.system_name = system_name
        self.vin_hash = self.generate_vin()
        self.start_time = datetime.datetime.utcnow()
        self.session_id = str(uuid.uuid4())
        
    def generate_vin(self) -> str:
        """Generate unique VIN hash for system identity"""
        data = f"{self.system_name}-{datetime.datetime.utcnow().isoformat()}".encode()
        return hashlib.sha256(data).hexdigest()[:17].upper()
    
    def build_system_metrics_section(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Build system metrics section"""
        return {
            "type": "system_metrics",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "metrics": {
                "cpu_usage_percent": round(metrics.cpu_usage, 2),
                "memory_usage_percent": round(metrics.memory_usage, 2),
                "disk_usage_percent": round(metrics.disk_usage, 2),
                "network_latency_ms": round(metrics.network_latency, 2),
                "uptime_seconds": metrics.uptime_seconds,
                "uptime_formatted": self.format_uptime(metrics.uptime_seconds),
                "active_processes": metrics.active_processes,
                "request_count": metrics.request_count,
                "error_count": metrics.error_count,
                "error_rate_percent": round((metrics.error_count / max(metrics.request_count, 1)) * 100, 2),
                "last_error": metrics.last_error
            }
        }
    
    def build_components_section(self, components: List[ComponentStatus]) -> Dict[str, Any]:
        """Build components status section"""
        component_list = []
        total_health = 0
        
        for comp in components:
            component_list.append({
                "id": comp.name.lower().replace(" ", "_"),
                "name": comp.name,
                "status": comp.status,
                "health_percent": round(comp.health_percentage, 2),
                "response_time_ms": round(comp.response_time_ms, 2),
                "operations_count": comp.operations_count,
                "last_updated": comp.last_updated
            })
            total_health += comp.health_percentage
        
        avg_health = total_health / len(components) if components else 0
        
        return {
            "type": "components_status",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "overall_health_percent": round(avg_health, 2),
            "components": component_list,
            "component_count": len(components),
            "healthy_count": sum(1 for c in components if c.status == "active"),
            "warning_count": sum(1 for c in components if c.status == "maintenance"),
            "error_count": sum(1 for c in components if c.status == "error")
        }
    
    def build_modules_section(self, modules: List[ModuleInfo]) -> Dict[str, Any]:
        """Build modules/skills section"""
        module_list = []
        
        for module in modules:
            module_list.append({
                "id": module.module_id,
                "name": module.name,
                "version": module.version,
                "status": module.status,
                "capabilities": module.capabilities,
                "dependencies": module.dependencies
            })
        
        return {
            "type": "modules",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "total_modules": len(modules),
            "active_modules": sum(1 for m in modules if m.status == "active"),
            "modules": module_list
        }
    
    def build_capabilities_section(self) -> Dict[str, Any]:
        """Build system capabilities section"""
        return {
            "type": "capabilities",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "automation": {
                "form_automation": True,
                "web_scraping": True,
                "workflow_orchestration": True,
                "conditional_logic": True,
                "data_extraction": True
            },
            "communication": {
                "telegram_integration": True,
                "webhook_support": True,
                "rest_api": True,
                "websocket_support": True,
                "mqtt_support": False
            },
            "audio": {
                "speech_to_text": True,
                "text_to_speech": True,
                "audio_processing": True,
                "multi_language": True
            },
            "monitoring": {
                "health_checks": True,
                "performance_metrics": True,
                "error_tracking": True,
                "audit_logging": True
            }
        }
    
    def build_integration_section(self) -> Dict[str, Any]:
        """Build integrations section"""
        return {
            "type": "integrations",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "external_apis": {
                "openai": {
                    "enabled": True,
                    "status": "configured"
                },
                "groq": {
                    "enabled": True,
                    "status": "configured"
                },
                "elevenlabs": {
                    "enabled": True,
                    "status": "configured"
                },
                "deepgram": {
                    "enabled": True,
                    "status": "configured"
                },
                "google_cloud": {
                    "enabled": True,
                    "status": "configured"
                }
            },
            "local_services": {
                "browser_automation": {
                    "enabled": True,
                    "driver": "playwright"
                },
                "audio_pipeline": {
                    "enabled": True,
                    "format_support": ["mp3", "wav", "ogg"]
                },
                "form_handler": {
                    "enabled": True,
                    "fields_supported": ["text", "select", "radio", "checkbox", "textarea"]
                }
            }
        }
    
    def build_performance_section(self, uptime_seconds: int, request_count: int, avg_response_ms: float) -> Dict[str, Any]:
        """Build performance metrics section"""
        return {
            "type": "performance",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "response_metrics": {
                "average_response_time_ms": round(avg_response_ms, 2),
                "p95_response_time_ms": round(avg_response_ms * 1.5, 2),
                "p99_response_time_ms": round(avg_response_ms * 2.0, 2),
                "requests_per_second": round(request_count / max(uptime_seconds, 1), 2)
            },
            "reliability": {
                "uptime_hours": round(uptime_seconds / 3600, 2),
                "total_requests": request_count,
                "successful_requests_percent": 98.5
            }
        }
    
    def generate_complete_vinjson(self, 
                                 metrics: SystemMetrics,
                                 components: List[ComponentStatus],
                                 modules: List[ModuleInfo]) -> Dict[str, Any]:
        """Generate complete OSCAR-VinJSON document"""
        
        oscar_vin = {
            "format_version": "OSCAR-VinJSON-1.0",
            "system_id": self.system_name,
            "vin": self.vin_hash,
            "session_id": self.session_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "metadata": {
                "system_name": self.system_name,
                "version": "1.0.0",
                "environment": "production",
                "timezone": "UTC"
            },
            "sections": {
                "system_metrics": self.build_system_metrics_section(metrics),
                "components": self.build_components_section(components),
                "modules": self.build_modules_section(modules),
                "capabilities": self.build_capabilities_section(),
                "integrations": self.build_integration_section(),
                "performance": self.build_performance_section(metrics.uptime_seconds, metrics.request_count, 150.0)
            }
        }
        
        return oscar_vin
    
    @staticmethod
    def format_uptime(seconds: int) -> str:
        """Format uptime in human-readable format"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{days}d {hours}h {minutes}m {secs}s"
    
    def export_to_json(self, vinjson: Dict[str, Any], filepath: str) -> bool:
        """Export OSCAR-VinJSON to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(vinjson, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    generator = OSCARVinJSONGenerator("OpenClaw")
    
    # Create sample metrics
    metrics = SystemMetrics(
        cpu_usage=45.2,
        memory_usage=62.8,
        disk_usage=38.5,
        network_latency=12.3,
        uptime_seconds=86400,
        active_processes=24,
        request_count=15000,
        error_count=45,
        last_error=None
    )
    
    # Create sample components
    components = [
        ComponentStatus("Telegram Bot", "active", 99.2, 45.5, 3200, "2024-01-15T10:30:00Z"),
        ComponentStatus("Browser Automation", "active", 98.5, 125.3, 1850, "2024-01-15T10:29:45Z"),
        ComponentStatus("Audio Pipeline", "active", 99.8, 23.1, 950, "2024-01-15T10:30:15Z"),
        ComponentStatus("Form Handler", "active", 97.2, 85.2, 2100, "2024-01-15T10:30:00Z"),
        ComponentStatus("API Gateway", "active", 99.5, 15.8, 5200, "2024-01-15T10:30:10Z"),
    ]
    
    # Create sample modules
    modules = [
        ModuleInfo("bot_001", "Telegram Bot", "2.0.0", "active", 
                  ["chat", "commands", "webhooks"], ["telegram_api", "openai"]),
        ModuleInfo("auto_001", "Browser Automation", "1.5.0", "active",
                  ["navigate", "click", "type", "extract"], ["playwright"]),
        ModuleInfo("audio_001", "Audio Pipeline", "1.0.0", "active",
                  ["stt", "tts", "voice_recognition"], ["groq", "elevenlabs"]),
        ModuleInfo("form_001", "Form Handler", "1.2.0", "active",
                  ["detect_forms", "fill_fields", "submit"], ["browser_automation"]),
    ]
    
    # Generate complete OSCAR-VinJSON
    vinjson = generator.generate_complete_vinjson(metrics, components, modules)
    
    # Export to file
    generator.export_to_json(vinjson, "/vercel/share/v0-project/oscar_output.json")
    
    # Print complete JSON
    print(json.dumps(vinjson, indent=2, ensure_ascii=False))
