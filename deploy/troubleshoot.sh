#!/bin/bash
# Troubleshooting script for Image2Text deployment

APP_DIR="/var/www/apps/image2text_pyproj"
APP_USER="ubuntu"

echo "=========================================="
echo "Image2Text Deployment Troubleshooting"
echo "=========================================="
echo ""

# Check if app directory exists
echo "1. Checking application directory..."
if [ -d "$APP_DIR" ]; then
    echo "   ✓ App directory exists: $APP_DIR"
else
    echo "   ✗ App directory NOT found: $APP_DIR"
    echo "   → Run: git clone https://github.com/samdivyakumar/imagetotext_pyproj.git $APP_DIR"
    exit 1
fi

# Check required files
echo ""
echo "2. Checking required files..."
files=("app.py" "gunicorn.conf.py" "requirements.txt" "config.py")
for file in "${files[@]}"; do
    if [ -f "$APP_DIR/$file" ]; then
        echo "   ✓ $file exists"
    else
        echo "   ✗ $file NOT found"
    fi
done

# Check virtual environment
echo ""
echo "3. Checking virtual environment..."
if [ -d "$APP_DIR/venv" ]; then
    echo "   ✓ Virtual environment exists"
    if [ -f "$APP_DIR/venv/bin/python" ]; then
        echo "   ✓ Python in venv: $($APP_DIR/venv/bin/python --version)"
    else
        echo "   ✗ Python not found in venv"
    fi
    if [ -f "$APP_DIR/venv/bin/gunicorn" ]; then
        echo "   ✓ Gunicorn installed"
    else
        echo "   ✗ Gunicorn NOT installed"
        echo "   → Run: cd $APP_DIR && source venv/bin/activate && pip install gunicorn"
    fi
else
    echo "   ✗ Virtual environment NOT found"
    echo "   → Run: cd $APP_DIR && python3 -m venv venv"
    exit 1
fi

# Check Python packages
echo ""
echo "4. Checking Python packages..."
cd "$APP_DIR"
source venv/bin/activate
packages=("flask" "gunicorn" "python-docx" "pytesseract" "Pillow")
for pkg in "${packages[@]}"; do
    if python -c "import ${pkg//-/_}" 2>/dev/null; then
        echo "   ✓ $pkg installed"
    else
        echo "   ✗ $pkg NOT installed"
        echo "   → Run: pip install $pkg"
    fi
done
deactivate

# Check Tesseract
echo ""
echo "5. Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "   ✓ Tesseract installed: $(tesseract --version | head -1)"
else
    echo "   ✗ Tesseract NOT installed"
    echo "   → Run: sudo apt install tesseract-ocr tesseract-ocr-eng"
fi

# Check directories
echo ""
echo "6. Checking upload/output directories..."
for dir in "uploads" "outputs"; do
    if [ -d "$APP_DIR/$dir" ]; then
        echo "   ✓ $dir directory exists"
        echo "     Permissions: $(stat -c '%A %U:%G' $APP_DIR/$dir 2>/dev/null || stat -f '%Sp %Su:%Sg' $APP_DIR/$dir)"
    else
        echo "   ✗ $dir directory NOT found"
        echo "   → Run: mkdir -p $APP_DIR/$dir"
    fi
done

# Check log directory
echo ""
echo "7. Checking log directory..."
if [ -d "/var/log/image2text" ]; then
    echo "   ✓ Log directory exists"
    echo "     Permissions: $(stat -c '%A %U:%G' /var/log/image2text 2>/dev/null || stat -f '%Sp %Su:%Sg' /var/log/image2text)"
else
    echo "   ✗ Log directory NOT found"
    echo "   → Run: sudo mkdir -p /var/log/image2text && sudo chown $APP_USER:$APP_USER /var/log/image2text"
fi

# Check Supervisor
echo ""
echo "8. Checking Supervisor..."
if command -v supervisorctl &> /dev/null; then
    echo "   ✓ Supervisor installed"
    if [ -f "/etc/supervisor/conf.d/image2text.conf" ]; then
        echo "   ✓ Supervisor config exists"
        echo ""
        echo "   Current status:"
        sudo supervisorctl status image2text 2>&1 | sed 's/^/     /'
    else
        echo "   ✗ Supervisor config NOT found"
        echo "   → Run: sudo bash deploy/configure_supervisor.sh"
    fi
else
    echo "   ✗ Supervisor NOT installed"
    echo "   → Run: sudo apt install supervisor"
fi

# Check Nginx
echo ""
echo "9. Checking Nginx..."
if command -v nginx &> /dev/null; then
    echo "   ✓ Nginx installed: $(nginx -v 2>&1)"
    if sudo nginx -t &> /dev/null; then
        echo "   ✓ Nginx configuration valid"
    else
        echo "   ✗ Nginx configuration has errors:"
        sudo nginx -t 2>&1 | sed 's/^/     /'
    fi
else
    echo "   ✗ Nginx NOT installed"
    echo "   → Run: sudo apt install nginx"
fi

# Check ports
echo ""
echo "10. Checking ports..."
echo "   Port 3000 (existing app):"
if sudo lsof -i :3000 &> /dev/null; then
    sudo lsof -i :3000 | grep LISTEN | sed 's/^/     /'
else
    echo "     (not in use)"
fi

echo "   Port 8001 (Image2Text):"
if sudo lsof -i :8001 &> /dev/null; then
    sudo lsof -i :8001 | grep LISTEN | sed 's/^/     /'
else
    echo "     (not in use)"
fi

echo "   Port 80 (Nginx):"
if sudo lsof -i :80 &> /dev/null; then
    sudo lsof -i :80 | grep LISTEN | sed 's/^/     /'
else
    echo "     (not in use)"
fi

# Test Gunicorn command
echo ""
echo "11. Testing Gunicorn command..."
cd "$APP_DIR"
if sudo -u $APP_USER $APP_DIR/venv/bin/gunicorn --version &> /dev/null; then
    echo "   ✓ Gunicorn can execute: $($APP_DIR/venv/bin/gunicorn --version)"
else
    echo "   ✗ Gunicorn execution failed"
fi

# Show recent error logs if they exist
echo ""
echo "12. Recent error logs (last 10 lines)..."
if [ -f "/var/log/image2text/error.log" ]; then
    echo "   From /var/log/image2text/error.log:"
    sudo tail -10 /var/log/image2text/error.log | sed 's/^/     /'
else
    echo "   (no error log found yet)"
fi

if [ -f "/var/log/supervisor/supervisord.log" ]; then
    echo ""
    echo "   From /var/log/supervisor/supervisord.log (image2text related):"
    sudo grep -i image2text /var/log/supervisor/supervisord.log | tail -10 | sed 's/^/     /'
fi

echo ""
echo "=========================================="
echo "Troubleshooting complete!"
echo "=========================================="
