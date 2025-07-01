# Deployment Guide

## Overview
PDF Chat Appliance supports multiple deployment methods: Docker, OVA, and manual installation.

## Deployment Methods

### 1. Docker Deployment

#### Prerequisites
- Docker and Docker Compose
- 4GB+ RAM available

#### Quick Start
```bash
git clone https://github.com/your-org/pdf-chat-appliance.git
cd pdf-chat-appliance
docker-compose up --build
```

#### Access
- WebUI: http://localhost:80
- API: http://localhost:5000

### 2. OVA Deployment (Recommended)

#### Prerequisites
- VMware Workstation/Player, VirtualBox, or Proxmox
- 4GB+ RAM for VM
- 25GB+ disk space

#### Installation
1. Download the OVA file
2. Import into your virtualization platform
3. Start the VM
4. Access via http://<VM_IP>

#### OVA Features
- Pre-configured Ubuntu 24.04 LTS
- Auto-starting services
- Nginx reverse proxy
- Systemd service management
- Non-root user security

### 3. Manual Installation

#### Prerequisites
- Ubuntu 22.04+ or similar Linux
- Python 3.9+
- 4GB+ RAM

#### Installation Steps
```bash
# Clone repository
git clone https://github.com/your-org/pdf-chat-appliance.git
cd pdf-chat-appliance

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama (optional)
curl -fsSL https://ollama.ai/install.sh | sh

# Run setup script
chmod +x scripts/setup.sh
sudo ./scripts/setup.sh
```

## Production Deployment

### System Requirements
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 25GB+ for OS and data
- **Network**: Internet access for model downloads

### Security Considerations
- Use HTTPS in production
- Configure firewall rules
- Regular security updates
- Non-root service user

### Monitoring
- Check service status: `sudo systemctl status pdfchat`
- View logs: `sudo journalctl -u pdfchat`
- Monitor disk usage: `df -h /var/lib/pdfchat`

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
sudo systemctl status pdfchat
sudo journalctl -u pdfchat -f
```

#### Port Already in Use
```bash
sudo netstat -tlnp | grep :5000
sudo systemctl stop conflicting-service
```

#### Permission Issues
```bash
sudo chown -R pdfchat:pdfchat /var/lib/pdfchat
sudo chown -R pdfchat:pdfchat /var/log/pdfchat
```

#### Memory Issues
- Increase VM RAM
- Check ChromaDB memory usage
- Monitor system resources

### Log Locations
- Application logs: `/var/log/pdfchat/`
- System logs: `sudo journalctl -u pdfchat`
- Nginx logs: `/var/log/nginx/`

## Backup and Recovery

### Data Backup
```bash
# Backup ChromaDB data
sudo tar -czf chroma_backup.tar.gz /var/lib/pdfchat/chroma_store

# Backup configuration
sudo tar -czf config_backup.tar.gz /etc/pdfchat
```

### Recovery
```bash
# Restore data
sudo tar -xzf chroma_backup.tar.gz -C /

# Restart services
sudo systemctl restart pdfchat
```

## Scaling

### Horizontal Scaling
- Load balancer with multiple instances
- Shared ChromaDB backend
- Redis for session management

### Vertical Scaling
- Increase VM resources
- Optimize embedding model
- Use GPU acceleration (future) 