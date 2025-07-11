#!/bin/bash

# VPS Deployment Script for PecanTV API
# This script sets up your API on a VPS with direct IP access

echo "🚀 Setting up PecanTV API on VPS..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv nginx

# Create app directory
sudo mkdir -p /opt/pecantv-api
sudo chown $USER:$USER /opt/pecantv-api

# Clone your repository (replace with your repo URL)
cd /opt/pecantv-api
git clone https://github.com/sdbmich1/PecanTV.git .

# Set up Python environment
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/pecantv-api.service > /dev/null <<EOF
[Unit]
Description=PecanTV API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/pecantv-api/api
Environment=PATH=/opt/pecantv-api/api/venv/bin
ExecStart=/opt/pecantv-api/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable pecantv-api
sudo systemctl start pecantv-api

# Configure Nginx
sudo tee /etc/nginx/sites-available/pecantv-api > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/pecantv-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "✅ PecanTV API deployed successfully!"
echo "🌐 Your API is now accessible at: http://$(curl -s ifconfig.me)"
echo "📊 Health check: http://$(curl -s ifconfig.me)/health"
echo "📝 Content endpoint: http://$(curl -s ifconfig.me)/content" 