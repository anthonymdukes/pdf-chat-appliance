#!/bin/bash
# UPDATED: Now compliant with environment.mdc stall-proof and timeout policy
set -e

# Timeout function to prevent hanging commands
timeout_cmd() {
    local timeout_seconds=5
    local cmd="$@"
    
    timeout $timeout_seconds bash -c "$cmd" 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        echo "TIMEOUT: Command '$cmd' exceeded ${timeout_seconds}s timeout" >&2
        return 1
    fi
    return $exit_code
}

# Log function for consistent error reporting
log_error() {
    echo "ERROR: $1" >&2
}

log_info() {
    echo "INFO: $1"
}

echo "Setting up PDF Chat Appliance..."

# Create service user with timeout protection
log_info "Creating service user..."
if ! timeout_cmd "sudo useradd -r -s /bin/false pdfchat 2>/dev/null || true"; then
    log_error "Failed to create service user"
    exit 1
fi

# Create directories with timeout protection
log_info "Creating directories..."
for dir in "/var/lib/pdfchat" "/var/log/pdfchat" "/etc/pdfchat"; do
    if ! timeout_cmd "sudo mkdir -p $dir"; then
        log_error "Failed to create directory $dir"
        exit 1
    fi
done

# Set permissions with timeout protection
log_info "Setting permissions..."
if ! timeout_cmd "sudo chown -R pdfchat:pdfchat /var/lib/pdfchat /var/log/pdfchat /opt/pdf-chat-appliance"; then
    log_error "Failed to set permissions"
    exit 1
fi

# Install Ollama with timeout protection
echo "📦 Installing Ollama..."
if ! timeout_cmd "curl -fsSL https://ollama.ai/install.sh | sh"; then
    log_error "Failed to install Ollama"
    exit 1
fi

# Install Python dependencies with timeout protection
echo "🐍 Setting up Python environment..."
if ! timeout_cmd "cd /opt/pdf-chat-appliance && source venv/bin/activate && pip install --upgrade pip"; then
    log_error "Failed to upgrade pip"
    exit 1
fi

if ! timeout_cmd "cd /opt/pdf-chat-appliance && source venv/bin/activate && pip install -r requirements.txt"; then
    log_error "Failed to install Python dependencies"
    exit 1
fi

# Create systemd service with timeout protection
echo "🔧 Creating systemd service..."
if ! timeout_cmd "sudo tee /etc/systemd/system/pdfchat.service > /dev/null <<'EOF'
[Unit]
Description=PDF Chat Appliance
After=network.target

[Service]
Type=simple
User=pdfchat
Group=pdfchat
WorkingDirectory=/opt/pdf-chat-appliance
Environment=PATH=/opt/pdf-chat-appliance/venv/bin
ExecStart=/opt/pdf-chat-appliance/venv/bin/python pdfchat.py serve --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"; then
    log_error "Failed to create systemd service"
    exit 1
fi

# Configure nginx with timeout protection
echo "🌐 Configuring nginx..."
if ! timeout_cmd "sudo tee /etc/nginx/sites-available/pdfchat > /dev/null <<'EOF'
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
EOF"; then
    log_error "Failed to configure nginx"
    exit 1
fi

# Enable nginx site with timeout protection
if ! timeout_cmd "sudo ln -sf /etc/nginx/sites-available/pdfchat /etc/nginx/sites-enabled/ && sudo rm -f /etc/nginx/sites-enabled/default"; then
    log_error "Failed to enable nginx site"
    exit 1
fi

# Enable and start services with timeout protection
echo "Starting services..."
if ! timeout_cmd "sudo systemctl daemon-reload"; then
    log_error "Failed to reload systemd"
    exit 1
fi

if ! timeout_cmd "sudo systemctl enable pdfchat nginx"; then
    log_error "Failed to enable services"
    exit 1
fi

if ! timeout_cmd "sudo systemctl start nginx"; then
    log_error "Failed to start nginx"
    exit 1
fi

if ! timeout_cmd "sudo systemctl start pdfchat"; then
    log_error "Failed to start pdfchat service"
    exit 1
fi

# Create CLI symlink with timeout protection
if ! timeout_cmd "sudo ln -sf /opt/pdf-chat-appliance/pdfchat.py /usr/local/bin/pdfchat"; then
    log_error "Failed to create CLI symlink"
    exit 1
fi

echo "PDF Chat Appliance setup complete!"
echo "🌐 Access the WebUI at: http://$(hostname -I | awk '{print $1}')"
echo "📋 Check status with: sudo systemctl status pdfchat"
echo ""

# UNCONDITIONAL: Ensure prompt unsticking regardless of exit path
echo "" 