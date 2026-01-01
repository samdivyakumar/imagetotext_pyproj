#!/bin/bash
# Deployment script for Image2Text application on AWS Lightsail
# Run this script on your Lightsail instance

set -e  # Exit on any error

APP_DIR="/home/ubuntu/image2text_pyproj"
APP_USER="ubuntu"

echo "=========================================="
echo "Image2Text Deployment Script"
echo "=========================================="

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and system dependencies..."
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install Tesseract OCR (required for the app)
echo "📝 Installing Tesseract OCR..."
sudo apt install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev

# Install additional language packs if needed (uncomment as required)
# sudo apt install -y tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-spa

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Install supervisor for process management
echo "⚙️ Installing Supervisor..."
sudo apt install -y supervisor

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p $APP_DIR
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# Navigate to app directory
cd $APP_DIR

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create necessary directories
echo "📂 Creating upload and output directories..."
mkdir -p uploads outputs
chmod 755 uploads outputs

# Deactivate virtual environment
deactivate

echo "✅ Basic setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your application files to $APP_DIR"
echo "2. Run: sudo bash /home/ubuntu/image2text_pyproj/deploy/configure_nginx.sh"
echo "3. Run: sudo bash /home/ubuntu/image2text_pyproj/deploy/configure_supervisor.sh"
