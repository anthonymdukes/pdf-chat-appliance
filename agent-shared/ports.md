# Port Management Registry

**Date:** 2025-07-06  
**Purpose:** Track all container ports in use to prevent conflicts  
**Policy:** All agents must check this file before launching new services  

---

## Active Services

### Draw.io Diagramming Service
- **Service:** draw.io
- **Container:** `jgraph/drawio:latest`
- **Port:** 8081
- **Status:** Active
- **Mounted To:** `agent-shared/diagrams/`
- **Access:** `http://localhost:8081`
- **Notes:** No longer conflicts with Open WebUI
- **Started:** 2025-07-06 17:30 (redeployed 2025-07-06 18:15)

---

## Reserved Ports

### Development Services
- **Port 8000:** FastAPI development server (reserved)
- **Port 8080:** Open WebUI (active)
- **Port 8081:** Draw.io diagramming service (active)
- **Port 3000:** Web UI development (reserved)
- **Port 5432:** PostgreSQL (reserved)
- **Port 6379:** Redis (reserved)
- **Port 6333:** Qdrant vector database (reserved)

### Monitoring Services
- **Port 9090:** Prometheus (reserved)
- **Port 3001:** Grafana (reserved)
- **Port 16686:** Jaeger tracing (reserved)

---

## Port Conflict Resolution

### Known Conflicts
1. **Open WebUI vs Draw.io:** Both previously used port 8080
   - **Solution:** Draw.io now uses `-p 8081:8080`
   - **Command:** `docker run -d --name drawio -p 8081:8080 -v ${PWD}/agent-shared/diagrams:/opt/drawio/diagrams jgraph/drawio:latest`

### Port Change Procedures
1. **Check this file** before launching any new service
2. **Update this file** when adding or removing services
3. **Use alternative ports** if conflicts detected
4. **Update documentation** when port mappings change

---

## Service Launch Checklist

Before launching any new containerized service:

- [ ] Check this file for port conflicts
- [ ] Choose an available port
- [ ] Update this file with service details
- [ ] Test port availability
- [ ] Update any related documentation
- [ ] Log the deployment in `session_notes.md`

---

## Emergency Port Management

### Quick Port Check
```bash
# Check what's using a specific port
netstat -ano | findstr :8081

# List all active containers and their ports
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

### Force Port Change
```bash
# Stop conflicting service
docker stop <container-name>

# Remove container
docker rm <container-name>

# Restart with different port
docker run -d --name <service> -p <new-port>:<internal-port> <image>
```

---

## Last Updated
- **Date:** 2025-07-06
- **Updated By:** system-architect
- **Reason:** Redeployed Draw.io on port 8081 to resolve conflict with Open WebUI 