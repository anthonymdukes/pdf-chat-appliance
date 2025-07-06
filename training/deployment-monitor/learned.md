# Deployment Monitor Knowledge Log

Use this file to track deep-dive learnings, cheat sheets, CLI examples, or key takeaways.

## Current Training Focus - 2025-07-06

### Active Responsibilities
- **Comprehensive Health Monitoring**: Implement multi-layered health checks for all services and dependencies
- **Automated Recovery**: Design intelligent restart and recovery mechanisms with proper backoff strategies
- **Container Orchestration**: Optimize container lifecycle management and resource allocation
- **Alert Management**: Configure intelligent alerting with proper severity levels and escalation policies
- **Performance Monitoring**: Track system performance metrics and resource utilization patterns

### Key Implementation Patterns

#### Docker Health Check Configuration
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install health check dependencies
RUN pip install requests psutil

# Copy health check script
COPY health_check.py /usr/local/bin/
RUN chmod +x /usr/local/bin/health_check.py

# Configure health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD /usr/local/bin/health_check.py

# Application setup
COPY app.py /app/
WORKDIR /app
CMD ["python", "app.py"]
```

#### Health Check Script
```python
# health_check.py
#!/usr/bin/env python3
import requests
import psutil
import sys
import os

def check_service_health():
    """Comprehensive health check for PDF Chat service"""
    
    # Check 1: Basic system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    if cpu_percent > 90 or memory_percent > 90 or disk_percent > 95:
        print(f"Resource usage too high: CPU={cpu_percent}%, MEM={memory_percent}%, DISK={disk_percent}%")
        return 1
    
    # Check 2: API endpoint availability
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code != 200:
            print(f"API health check failed: {response.status_code}")
            return 1
    except requests.RequestException as e:
        print(f"API health check error: {e}")
        return 1
    
    # Check 3: Database connectivity
    try:
        response = requests.get('http://localhost:5000/db/health', timeout=5)
        if response.status_code != 200:
            print(f"Database health check failed: {response.status_code}")
            return 1
    except requests.RequestException as e:
        print(f"Database health check error: {e}")
        return 1
    
    # Check 4: Vector store connectivity
    try:
        response = requests.get('http://localhost:5000/vector/health', timeout=5)
        if response.status_code != 200:
            print(f"Vector store health check failed: {response.status_code}")
            return 1
    except requests.RequestException as e:
        print(f"Vector store health check error: {e}")
        return 1
    
    print("All health checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(check_service_health())
```

#### Kubernetes Probe Configuration
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pdf-chat-appliance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pdf-chat-appliance
  template:
    metadata:
      labels:
        app: pdf-chat-appliance
    spec:
      containers:
      - name: pdf-chat-api
        image: pdf-chat-appliance:latest
        ports:
        - containerPort: 5000
        
        # Startup probe for slow-starting services
        startupProbe:
          httpGet:
            path: /health
            port: 5000
          failureThreshold: 30
          periodSeconds: 10
        
        # Liveness probe to detect broken state
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        
        # Readiness probe to determine traffic readiness
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

#### Automated Recovery Manager
```python
# recovery_manager.py
import subprocess
import time
import logging
from typing import List, Dict

class RecoveryManager:
    def __init__(self, max_attempts: int = 3, backoff_multiplier: int = 2):
        self.max_attempts = max_attempts
        self.backoff_multiplier = backoff_multiplier
        self.recovery_attempts: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if a Docker service is healthy"""
        try:
            result = subprocess.run(
                ['docker-compose', 'ps', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check if service is running and healthy
            if result.returncode == 0 and "Up" in result.stdout:
                return True
            else:
                self.logger.warning(f"Service {service_name} is not healthy")
                return False
                
        except Exception as e:
            self.logger.error(f"Health check failed for {service_name}: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a Docker service"""
        try:
            self.logger.info(f"Restarting service: {service_name}")
            result = subprocess.run(
                ['docker-compose', 'restart', service_name],
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Failed to restart {service_name}: {e}")
            return False
    
    def perform_recovery(self, service_name: str) -> bool:
        """Perform automated recovery for a service"""
        if service_name not in self.recovery_attempts:
            self.recovery_attempts[service_name] = 0
        
        if self.recovery_attempts[service_name] >= self.max_attempts:
            self.logger.error(f"Max recovery attempts reached for {service_name}")
            return False
        
        self.recovery_attempts[service_name] += 1
        self.logger.warning(f"Recovery attempt {self.recovery_attempts[service_name]} for {service_name}")
        
        # Restart service
        if not self.restart_service(service_name):
            return False
        
        # Wait with exponential backoff
        wait_time = self.backoff_multiplier ** self.recovery_attempts[service_name]
        time.sleep(wait_time)
        
        # Check if recovery was successful
        if self.check_service_health(service_name):
            self.logger.info(f"Recovery successful for {service_name}")
            self.recovery_attempts[service_name] = 0
            return True
        else:
            self.logger.error(f"Recovery failed for {service_name}")
            return False
    
    def monitor_and_recover(self, services: List[str]):
        """Monitor services and perform recovery as needed"""
        while True:
            for service in services:
                if not self.check_service_health(service):
                    self.perform_recovery(service)
            
            time.sleep(60)  # Check every minute

# Usage
if __name__ == "__main__":
    recovery_manager = RecoveryManager()
    services = ["pdf-chat-api", "qdrant", "ollama"]
    recovery_manager.monitor_and_recover(services)
```

### Best Practices Implemented

- **Progressive Health Checks**: Start with basic connectivity, then test application functionality
- **Graceful Degradation**: Implement fallback mechanisms when dependencies are unavailable
- **Resource Monitoring**: Track CPU, memory, disk, and network usage with appropriate thresholds
- **Automated Remediation**: Self-healing capabilities for common failure scenarios
- **Comprehensive Logging**: Detailed logging for troubleshooting and incident response

### Current Focus Areas

1. **Documentation Structure Remediation**: Supporting Phase 2 consolidation efforts
2. **Comprehensive Health Monitoring**: Implementing multi-layered health checks
3. **Automated Recovery**: Designing intelligent restart and recovery mechanisms
4. **Container Orchestration**: Optimizing container lifecycle management
5. **Alert Management**: Configuring intelligent alerting with proper severity levels

### Recent Learnings

- **Health Check Commands**: Use lightweight commands that test actual service functionality
- **Interval Configuration**: Set appropriate intervals (30s default) to balance responsiveness and overhead
- **Timeout Settings**: Configure timeouts shorter than intervals to prevent overlapping checks
- **Retry Logic**: Implement retry mechanisms with appropriate start periods for slow-starting services
- **Exit Codes**: Use proper exit codes (0=healthy, 1=unhealthy) for clear health status

### GPU Architecture Knowledge

#### NVIDIA GPU Architecture Mastery
- **T4 GPUs**: Entry-level inference with 16GB VRAM, perfect for small models and development
- **A100 GPUs**: Enterprise-grade with 40-80GB VRAM, ideal for large-scale deployments
- **A6000 GPUs**: Workstation class with 48GB VRAM, excellent for development and testing
- **RTX 4090**: Consumer GPU with 24GB VRAM, cost-effective for development

#### GPU Memory Management Strategies
- **Dynamic Model Loading**: Intelligent model loading based on available VRAM
- **Batch Optimization**: Adaptive batch sizes for memory constraints
- **Fallback Mechanisms**: Graceful CPU fallback when GPU unavailable
- **Performance Monitoring**: Real-time GPU utilization tracking

---

**Last Updated:** 2025-07-06  
**Status:** Active training and implementation  
**Next Review:** 2025-07-07
