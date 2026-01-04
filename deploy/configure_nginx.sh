#!/bin/bash
# Configure Nginx for Image2Text application

set -e

DOMAIN="${1:-_}"  # Domain or subdomain (e.g., convert.yourdomain.com)
DEPLOY_MODE="${2:-subdomain}"  # Options: subdomain, path, port
APP_DIR="/home/ubuntu/image2text_pyproj"
GUNICORN_PORT="8001"  # Different from existing app on port 3000

echo "=========================================="
echo "Configuring Nginx for Image2Text..."
echo "Domain: $DOMAIN"
echo "Mode: $DEPLOY_MODE"
echo "=========================================="

if [ "$DEPLOY_MODE" = "subdomain" ]; then
    # OPTION 1: Subdomain deployment (e.g., convert.yourdomain.com)
    echo "Setting up subdomain configuration..."
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
        proxy_pass http://127.0.0.1:$GUNICORN_PORT;
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
        proxy_pass http://127.0.0.1:$GUNICORN_PORT/health;
        proxy_set_header Host \$host;
    }
}
EOF

elif [ "$DEPLOY_MODE" = "path" ]; then
    # OPTION 2: Path-based deployment (e.g., yourdomain.com/convert)
    echo "Setting up path-based configuration..."
    echo "This will add a location block to your existing Nginx config."
    echo ""
    echo "Add this to your existing server block in /etc/nginx/sites-available/default:"
    echo ""
    cat <<EOF
    # Image2Text Application
    location /convert {
        rewrite ^/convert(.*) \$1 break;
        proxy_pass http://127.0.0.1:$GUNICORN_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
    
    location /convert/static {
        alias $APP_DIR/static;
        expires 30d;
    }
EOF
    echo ""
    read -p "Press Enter after you've added the above configuration..."

elif [ "$DEPLOY_MODE" = "port" ]; then
    # OPTION 3: Direct port access (e.g., yourdomain.com:8080)
    PUBLIC_PORT="${3:-8080}"
    echo "Setting up port-based configuration on port $PUBLIC_PORT..."
    sudo tee /etc/nginx/sites-available/image2text > /dev/null <<EOF
server {
    listen $PUBLIC_PORT;
    server_name _;

    client_max_body_size 16M;
    access_log /var/log/nginx/image2text_access.log;
    error_log /var/log/nginx/image2text_error.log;

    location / {
        proxy_pass http://127.0.0.1:$GUNICORN_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
EOF
    
    # Open firewall port if using UFW
    if command -v ufw &> /dev/null; then
        echo "Opening port $PUBLIC_PORT in firewall..."
        sudo ufw allow $PUBLIC_PORT/tcp
    fi
    
    echo "⚠️  Remember to open port $PUBLIC_PORT in AWS Lightsail firewall!"
fi

if [ "$DEPLOY_MODE" != "path" ]; then
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/image2text /etc/nginx/sites-enabled/
fi

# Test Nginx configuration
echo "Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ Nginx configured successfully!"
