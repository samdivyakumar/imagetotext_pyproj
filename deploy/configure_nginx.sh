#!/bin/bash
# Configure Nginx for Image2Text application

set -e

DOMAIN="${1:-_}"  # Use underscore as default (catches all requests)
APP_DIR="/home/ubuntu/image2text_pyproj"

echo "=========================================="
echo "Configuring Nginx..."
echo "=========================================="

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/image2text > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Max upload size (match Flask config)
    client_max_body_size 16M;

    # Logging
    access_log /var/log/nginx/image2text_access.log;
    error_log /var/log/nginx/image2text_error.log;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeout settings for large file processing
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Static files (if any)
    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host \$host;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/image2text /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Nginx configured successfully!"
