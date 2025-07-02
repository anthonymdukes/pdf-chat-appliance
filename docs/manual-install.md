# Manual Installation Guide

## Overview
This guide provides step-by-step instructions for manually installing PDF Chat Appliance on a fresh Ubuntu system. This is useful for custom deployments, testing, or when OVA deployment is not preferred.

## Prerequisites

### System Requirements
- **CPU**: 2+ cores (4+ recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 25GB+ available space
- **Network**: Internet access for downloads
- **OS**: Ubuntu 22.04 LTS or 24.04 LTS

### Software Requirements
- **Python**: 3.12.3+ (recommended) or 3.9+
- **Git**: For cloning repository
- **curl**: For Ollama installation

## Step 1: VM Creation

### VMware Workstation/Player
1. **Create New VM:**
   - File → New Virtual Machine
   - Choose "Typical" configuration
   - Select "Installer disc image file (iso)"
   - Browse to Ubuntu 24.04 LTS ISO
   - Set VM name: `pdf-chat-appliance`
   - Set disk size: 25GB
   - Set memory: 4GB (4096MB)

2. **VM Settings:**
   - Right-click VM → Settings
   - **Hardware tab:**
     - Memory: 4GB
     - Processors: 2 cores
     - Hard disk: 25GB
   - **Options tab:**
     - Advanced → Firmware type: UEFI
   - **Network:**
     - Network adapter: Bridged (recommended) or NAT

### VirtualBox
1. **Create New VM:**
   - Machine → New
   - Name: `pdf-chat-appliance`
   - Type: Linux
   - Version: Ubuntu (64-bit)
   - Memory: 4GB
   - Hard disk: Create virtual hard disk now
   - Size: 25GB

2. **VM Settings:**
   - Right-click VM → Settings
   - **System:**
     - Base memory: 4GB
     - Processors: 2
   - **Storage:**
     - Add Ubuntu ISO to SATA controller
   - **Network:**
     - Adapter 1: Bridged Adapter

### Proxmox
1. **Create VM:**
   - Datacenter → Create VM
   - General:
     - Name: `pdf-chat-appliance`
     - VM ID: Auto-assigned
   - OS:
     - Use CD/DVD disc image file
     - Select Ubuntu 24.04 ISO
   - System:
     - Sockets: 1
     - Cores: 2
     - Memory: 4096
   - Hard Disk:
     - Size: 25GB
     - Storage: Local

## Step 2: Ubuntu Installation

### Installation Steps
1. **Boot from ISO:**
   - Start VM and boot from Ubuntu ISO
   - Select "Install Ubuntu Server"

2. **Language & Keyboard:**
   - Language: English
   - Keyboard layout: English (US)

3. **Network:**
   - Select network interface (usually auto-detected)
   - Configure if needed (DHCP recommended)

4. **Storage:**
   - **Option A (Simple):** Use entire disk
   - **Option B (Advanced):** Custom partitioning
     - `/` (root): 20GB
     - `/var`: 5GB
     - Swap: 2GB

5. **User Setup:**
   - Your name: `PDF Chat User`
   - Username: `ubuntu`
   - Password: Choose secure password
   - **Important:** Remember this password!

6. **SSH Setup:**
   - Install OpenSSH server: **Yes**
   - Import SSH identity: No (unless you have one)

7. **Featured Snaps:**
   - Select none (we'll install what we need)

8. **Installation:**
   - Wait for installation to complete
   - Reboot when prompted

## Step 3: System Preparation

### Update System
```bash
# Login as ubuntu user
ssh ubuntu@<VM_IP>
# or use VM console

# Update system packages
sudo apt update
sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv git curl wget nginx
```

### Create Application Directory
```bash
# Create application directory
sudo mkdir -p /opt/pdf-chat-appliance
sudo chown ubuntu:ubuntu /opt/pdf-chat-appliance

# Create data directories
sudo mkdir -p /var/lib/pdfchat
sudo mkdir -p /var/log/pdfchat
sudo mkdir -p /etc/pdfchat
sudo chown -R ubuntu:ubuntu /var/lib/pdfchat
sudo chown -R ubuntu:ubuntu /var/log/pdfchat
sudo chown -R ubuntu:ubuntu /etc/pdfchat
```

## Step 4: Install Ollama

### Install Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Add ollama to PATH (if not already added)
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
source ~/.bashrc

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull a model (optional, for testing)
ollama pull mistral
```

### Verify Ollama Installation
```bash
# Check Ollama status
ollama list

# Test Ollama (optional)
ollama run mistral "Hello, world!"
```

## Step 5: Install PDF Chat Appliance

### Clone Repository
```bash
# Navigate to application directory
cd /opt/pdf-chat-appliance

# Clone repository (replace with actual repo URL)
git clone https://github.com/your-org/pdf-chat-appliance.git .

# Set proper ownership
sudo chown -R ubuntu:ubuntu /opt/pdf-chat-appliance
```

### Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Configure Application
```bash
# Copy default configuration
cp config/default.yaml /etc/pdfchat/config.yaml

# Edit configuration if needed
sudo nano /etc/pdfchat/config.yaml

# Test configuration
python pdfchat.py config show
```

## Step 6: Setup Services

### Create Systemd Service
```bash
# Create service file
sudo tee /etc/systemd/system/pdfchat.service > /dev/null <<EOF
[Unit]
Description=PDF Chat Appliance
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/pdf-chat-appliance
Environment=PATH=/opt/pdf-chat-appliance/venv/bin
ExecStart=/opt/pdf-chat-appliance/venv/bin/python pdfchat.py serve --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### Configure Nginx
```bash
# Create nginx configuration
sudo tee /etc/nginx/sites-available/pdfchat > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/pdfchat /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start services
sudo systemctl daemon-reload
sudo systemctl enable pdfchat
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl start pdfchat
```

### Create CLI Symlink
```bash
# Create CLI symlink
sudo ln -sf /opt/pdf-chat-appliance/pdfchat.py /usr/local/bin/pdfchat

# Test CLI
pdfchat version
```

## Step 7: Testing

### Test Services
```bash
# Check service status
sudo systemctl status pdfchat
sudo systemctl status nginx
sudo systemctl status ollama

# Check logs if needed
sudo journalctl -u pdfchat -f
```

### Test Web Interface
```bash
# Get VM IP address
ip addr show

# Access web interface
# Open browser to: http://<VM_IP>
```

### Test CLI Commands
```bash
# Test CLI functionality
pdfchat version
pdfchat config show

# Test with sample PDF (if available)
pdfchat ingest /path/to/sample/pdfs
```

### Test API Endpoints
```bash
# Test health endpoint
curl http://localhost:5000/health

# Test query endpoint
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

### Run Tests
```bash
# Navigate to project directory
cd /opt/pdf-chat-appliance

# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest -v

# Run specific test categories
pytest tests/memory/ -v
pytest tests/test_ingestion.py -v
pytest tests/test_server.py -v
```

## Step 8: Security & Firewall

### Configure Firewall
```bash
# Install ufw if not present
sudo apt install -y ufw

# Configure firewall
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Check firewall status
sudo ufw status
```

### Security Hardening
```bash
# Disable root login
sudo passwd -l root

# Configure SSH security
sudo nano /etc/ssh/sshd_config
# Add/modify:
# PermitRootLogin no
# PasswordAuthentication yes (or no for key-based)

# Restart SSH
sudo systemctl restart ssh
```

## Usage Guide

### CLI Commands

#### Ingest PDFs
```bash
# Ingest PDFs from a directory
pdfchat ingest /path/to/pdfs

# Use custom config file
pdfchat ingest /path/to/pdfs --config /etc/pdfchat/config.yaml
```

#### Start Server
```bash
# Start server with default settings
pdfchat serve

# Start with custom host and port
pdfchat serve --host 127.0.0.1 --port 8080

# Start in debug mode
pdfchat serve --debug
```

#### Manage Configuration
```bash
# Show current configuration
pdfchat config show

# Edit configuration
pdfchat config edit

# Reset to defaults
pdfchat config reset
```

#### Check Version
```bash
pdfchat version
```

### API Usage

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Query PDFs
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of this document?",
    "top_k": 3
  }'
```

#### Web Interface
- Open browser to `http://<server-ip>:5000`
- Simple HTML interface for testing

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status pdfchat

# Check logs
sudo journalctl -u pdfchat -f

# Check permissions
ls -la /opt/pdf-chat-appliance/
ls -la /var/lib/pdfchat/
```

#### Port Already in Use
```bash
# Check what's using port 5000
sudo netstat -tlnp | grep :5000

# Kill process if needed
sudo kill -9 <PID>
```

#### Permission Issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /opt/pdf-chat-appliance
sudo chown -R ubuntu:ubuntu /var/lib/pdfchat
sudo chown -R ubuntu:ubuntu /var/log/pdfchat
```

#### Memory Issues
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Monitor system resources
htop
```

#### Test Failures
```bash
# Check Python environment
python --version
pip list | grep llama

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run tests with verbose output
pytest -v -s
```

### Log Locations
- Application logs: `/var/log/pdfchat/`
- System logs: `sudo journalctl -u pdfchat`
- Nginx logs: `/var/log/nginx/`
- Ollama logs: `sudo journalctl -u ollama`

## Environment Variables

### Optional Environment Variables
```bash
# Set in /etc/pdfchat/config.yaml or environment
export PDFCHAT_CONFIG_FILE=/etc/pdfchat/config.yaml
export PDFCHAT_LOG_LEVEL=INFO
export PDFCHAT_DEBUG=false
```

## Next Steps

### Production Considerations
1. **SSL/HTTPS:** Configure SSL certificates
2. **Backup:** Set up regular backups
3. **Monitoring:** Implement system monitoring
4. **Updates:** Schedule regular updates

### Customization
1. **Models:** Configure different Ollama models
2. **Embeddings:** Customize embedding models
3. **Storage:** Configure external storage
4. **Authentication:** Add user authentication

## Support

For additional help:
- Check the [main documentation](README.md)
- Review [troubleshooting guide](docs/deployment.md)
- Open an issue on GitHub 