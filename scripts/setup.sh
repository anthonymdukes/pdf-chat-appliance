#!/bin/bash
set -e

echo "🚀 Setting up PDF Chat Appliance..."

# Create service user
sudo useradd -r -s /bin/false pdfchat || true

# Create directories
sudo mkdir -p /var/lib/pdfchat
sudo mkdir -p /var/log/pdfchat
sudo mkdir -p /etc/pdfchat

# Set permissions
sudo chown -R pdfchat:pdfchat /var/lib/pdfchat
sudo chown -R pdfchat:pdfchat /var/log/pdfchat
sudo chown -R pdfchat:pdfchat /opt/pdf-chat-appliance

# Install Ollama
echo "📦 Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Install Python dependencies
echo "🐍 Setting up Python environment..."
cd /opt/pdf-chat-appliance
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/pdfchat.service > /dev/null <<EOF
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
EOF

# Configure nginx
echo "🌐 Configuring nginx..."
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

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/pdfchat /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Enable and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable pdfchat
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl start pdfchat

# Create CLI symlink
sudo ln -sf /opt/pdf-chat-appliance/pdfchat.py /usr/local/bin/pdfchat

echo "✅ PDF Chat Appliance setup complete!"
echo "🌐 Access the WebUI at: http://$(hostname -I | awk '{print $1}')"
echo "📋 Check status with: sudo systemctl status pdfchat" 