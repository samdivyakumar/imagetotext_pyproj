#!/bin/bash
# Quick deployment script - Run this on your LOCAL machine
# This script packages and uploads your app to AWS Lightsail

set -e

# Configuration - UPDATE THESE VALUES
LIGHTSAIL_IP="${1:-your-lightsail-ip}"
SSH_KEY="${2:-~/.ssh/id_rsa}"
APP_NAME="image2text_pyproj"
REMOTE_USER="ubuntu"
REMOTE_DIR="/home/ubuntu/$APP_NAME"

if [ "$LIGHTSAIL_IP" == "your-lightsail-ip" ]; then
    echo "Usage: bash quick_deploy.sh <lightsail-ip> [ssh-key-path]"
    echo "Example: bash quick_deploy.sh 54.123.45.67 ~/.ssh/LightsailDefaultKey.pem"
    exit 1
fi

echo "=========================================="
echo "Deploying to AWS Lightsail: $LIGHTSAIL_IP"
echo "=========================================="

# Files to deploy (excluding unnecessary files)
DEPLOY_FILES=(
    "app.py"
    "config.py"
    "document_processor.py"
    "image_extractor.py"
    "ocr_processor.py"
    "gunicorn.conf.py"
    "requirements.txt"
    "templates"
    "deploy"
)

# Create a temporary directory for deployment package
TEMP_DIR=$(mktemp -d)
echo "📦 Creating deployment package..."

for item in "${DEPLOY_FILES[@]}"; do
    if [ -e "$item" ]; then
        cp -r "$item" "$TEMP_DIR/"
    fi
done

# Create tarball
TARBALL="$APP_NAME.tar.gz"
cd "$TEMP_DIR"
tar -czf "$TARBALL" *
cd -

# Upload to server
echo "📤 Uploading to server..."
scp -i "$SSH_KEY" "$TEMP_DIR/$TARBALL" "$REMOTE_USER@$LIGHTSAIL_IP:/tmp/"

# Deploy on server
echo "🚀 Deploying on server..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$LIGHTSAIL_IP" << EOF
    set -e
    
    # Create app directory
    mkdir -p $REMOTE_DIR
    
    # Extract files
    cd $REMOTE_DIR
    tar -xzf /tmp/$TARBALL
    
    # Make deploy scripts executable
    chmod +x deploy/*.sh
    
    # Cleanup
    rm /tmp/$TARBALL
    
    echo "Files deployed to $REMOTE_DIR"
EOF

# Cleanup local temp files
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Deployment package uploaded successfully!"
echo ""
echo "Next steps (SSH into your server and run):"
echo "  1. ssh -i $SSH_KEY $REMOTE_USER@$LIGHTSAIL_IP"
echo "  2. cd $REMOTE_DIR"
echo "  3. bash deploy/deploy.sh"
echo "  4. sudo bash deploy/configure_nginx.sh"
echo "  5. sudo bash deploy/configure_supervisor.sh"
