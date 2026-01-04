#!/bin/bash
# Configure Supervisor to manage the Gunicorn process

set -e

APP_DIR="/var/www/apps/image2text_pyproj"
APP_USER="ubuntu"

echo "=========================================="
echo "Configuring Supervisor..."
echo "=========================================="

# Verify required files exist
if [ ! -f "$APP_DIR/app.py" ]; then
    echo "❌ Error: app.py not found in $APP_DIR"
    exit 1
fi

if [ ! -f "$APP_DIR/gunicorn.conf.py" ]; then
    echo "❌ Error: gunicorn.conf.py not found in $APP_DIR"
    exit 1
fi

if [ ! -f "$APP_DIR/venv/bin/gunicorn" ]; then
    echo "❌ Error: Gunicorn not found. Please run deploy.sh first"
    exit 1
fi

echo "✓ Required files verified"

# Create Supervisor configuration for the app
sudo tee /etc/supervisor/conf.d/image2text.conf > /dev/null <<EOF
[program:image2text]
command=$APP_DIR/venv/bin/gunicorn --config $APP_DIR/gunicorn.conf.py app:app
directory=$APP_DIR
user=$APP_USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/image2text/error.log
stdout_logfile=/var/log/image2text/access.log
environment=SECRET_KEY="$(openssl rand -hex 32)",FLASK_ENV="production"
EOF

# Create log directory
sudo mkdir -p /var/log/image2text
sudo chown -R $APP_USER:$APP_USER /var/log/image2text

# Reload Supervisor configuration
echo "Reloading Supervisor..."
sudo supervisorctl reread
sudo supervisorctl update

# Start the service (don't restart if it doesn't exist yet)
echo "Starting image2text service..."
sudo supervisorctl start image2text 2>/dev/null || sudo supervisorctl restart image2text

# Check status
echo ""
echo "Service status:"
sudo supervisorctl status image2text

echo "✅ Supervisor configured successfully!"
echo ""
echo "Useful commands:"
echo "  sudo supervisorctl status image2text    - Check status"
echo "  sudo supervisorctl restart image2text   - Restart app"
echo "  sudo supervisorctl stop image2text      - Stop app"
echo "  sudo supervisorctl start image2text     - Start app"
echo "  sudo tail -f /var/log/image2text/error.log  - View error logs"
