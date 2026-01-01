# AWS Lightsail Deployment Guide

Complete guide to deploy the Image2Text application on AWS Lightsail.

## Prerequisites

- AWS Account
- Local machine with SSH client
- Your application code ready

---

## Step 1: Create AWS Lightsail Instance

### 1.1 Log in to AWS Console
1. Go to [AWS Console](https://console.aws.amazon.com)
2. Search for "Lightsail" in the services search bar
3. Click on **Lightsail**

### 1.2 Create Instance
1. Click **Create instance**
2. Select your preferred **Region** (e.g., `us-east-1`)
3. Choose platform: **Linux/Unix**
4. Select blueprint: **OS Only** → **Ubuntu 22.04 LTS**
5. Choose instance plan:
   - Recommended: **$5/month** (1 GB RAM, 1 vCPU) for testing
   - For production: **$10/month** (2 GB RAM, 1 vCPU) or higher
6. Name your instance: `image2text-server`
7. Click **Create instance**

### 1.3 Configure Networking
1. Wait for instance to be **Running**
2. Click on your instance name
3. Go to **Networking** tab
4. Under **IPv4 Firewall**, add rule:
   - Application: **HTTP** (Port 80)
   - Click **Create**
5. Add another rule for HTTPS:
   - Application: **HTTPS** (Port 443)
   - Click **Create**

### 1.4 Download SSH Key
1. Go to **Account** → **SSH keys**
2. Download the default key for your region
3. Save it as `LightsailDefaultKey.pem`
4. Set permissions: `chmod 400 LightsailDefaultKey.pem`

### 1.5 Note Your Public IP
- Find your instance's **Public IP** on the instance page
- Example: `54.123.45.67`

---

## Step 2: Connect to Your Instance

```bash
# Replace with your actual IP and key path
ssh -i ~/.ssh/LightsailDefaultKey.pem ubuntu@YOUR_PUBLIC_IP
```

---

## Step 3: Deploy Application

### Option A: Quick Deploy (Automated)

**On your local machine:**
```bash
cd /Users/divyakumar/workspace/dev_projects/image2text_pyproj

# Deploy to Lightsail
bash deploy/quick_deploy.sh YOUR_PUBLIC_IP ~/.ssh/LightsailDefaultKey.pem
```

**On the Lightsail server:**
```bash
cd /home/ubuntu/image2text_pyproj

# Run setup script
bash deploy/deploy.sh

# Configure Nginx
sudo bash deploy/configure_nginx.sh

# Configure Supervisor (starts the app)
sudo bash deploy/configure_supervisor.sh
```

### Option B: Manual Deploy

**On your local machine:**
```bash
cd /Users/divyakumar/workspace/dev_projects/image2text_pyproj

# Create deployment package
tar -czf image2text.tar.gz \
    app.py config.py document_processor.py image_extractor.py \
    ocr_processor.py gunicorn.conf.py requirements.txt \
    templates deploy

# Upload to server
scp -i ~/.ssh/LightsailDefaultKey.pem image2text.tar.gz ubuntu@YOUR_PUBLIC_IP:/home/ubuntu/
```

**On the server:**
```bash
# Extract files
cd /home/ubuntu
mkdir -p image2text_pyproj
tar -xzf image2text.tar.gz -C image2text_pyproj
cd image2text_pyproj

# Install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv tesseract-ocr tesseract-ocr-eng nginx supervisor

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create directories
mkdir -p uploads outputs

# Configure and start services
sudo bash deploy/configure_nginx.sh
sudo bash deploy/configure_supervisor.sh
```

---

## Step 4: Verify Deployment

### Check Application Status
```bash
# Check if app is running
sudo supervisorctl status image2text

# Check Nginx status
sudo systemctl status nginx

# View application logs
sudo tail -f /var/log/image2text/error.log
```

### Test the Application
Open in browser: `http://YOUR_PUBLIC_IP`

Or use curl:
```bash
curl http://YOUR_PUBLIC_IP/health
```

---

## Step 5: Set Up Custom Domain (Optional)

### 5.1 Register/Configure Domain
1. Register a domain (e.g., from Namecheap, GoDaddy, Route 53)
2. Add an **A Record** pointing to your Lightsail IP:
   - Type: A
   - Name: @ (or subdomain)
   - Value: YOUR_PUBLIC_IP
   - TTL: 300

### 5.2 Update Nginx Configuration
```bash
# Reconfigure Nginx with your domain
sudo bash deploy/configure_nginx.sh your-domain.com
```

### 5.3 Install SSL Certificate
```bash
# Install free SSL certificate from Let's Encrypt
sudo bash deploy/setup_ssl.sh your-domain.com
```

---

## Step 6: Production Security Checklist

### Environment Variables
Create `/home/ubuntu/image2text_pyproj/.env`:
```bash
SECRET_KEY=your-super-secure-random-key-here
FLASK_ENV=production
```

Generate a secure key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Firewall Configuration
```bash
# Enable UFW firewall
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### Regular Updates
```bash
# Keep system updated
sudo apt update && sudo apt upgrade -y
```

---

## Useful Commands

### Application Management
```bash
# Restart application
sudo supervisorctl restart image2text

# Stop application
sudo supervisorctl stop image2text

# Start application
sudo supervisorctl start image2text

# View status
sudo supervisorctl status
```

### Nginx Management
```bash
# Restart Nginx
sudo systemctl restart nginx

# Test configuration
sudo nginx -t

# View access logs
sudo tail -f /var/log/nginx/image2text_access.log
```

### Logs
```bash
# Application error log
sudo tail -f /var/log/image2text/error.log

# Application access log
sudo tail -f /var/log/image2text/access.log

# Nginx error log
sudo tail -f /var/log/nginx/image2text_error.log
```

### Cleanup Old Files
```bash
# Remove uploaded files older than 24 hours
find /home/ubuntu/image2text_pyproj/uploads -type f -mtime +1 -delete
find /home/ubuntu/image2text_pyproj/outputs -type f -mtime +1 -delete
```

---

## Troubleshooting

### App Not Starting
```bash
# Check supervisor logs
sudo tail -50 /var/log/supervisor/supervisord.log

# Check app error logs
sudo tail -50 /var/log/image2text/error.log

# Test manually
cd /home/ubuntu/image2text_pyproj
source venv/bin/activate
python app.py
```

### 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo supervisorctl status image2text

# Restart services
sudo supervisorctl restart image2text
sudo systemctl restart nginx
```

### Tesseract Not Found
```bash
# Verify Tesseract installation
tesseract --version

# Reinstall if needed
sudo apt install -y tesseract-ocr tesseract-ocr-eng
```

### Permission Issues
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/image2text_pyproj

# Fix directory permissions
chmod 755 /home/ubuntu/image2text_pyproj/uploads
chmod 755 /home/ubuntu/image2text_pyproj/outputs
```

---

## Cost Estimation

| Resource | Monthly Cost |
|----------|-------------|
| Lightsail Instance ($5 plan) | $5 |
| Static IP (included) | $0 |
| Data Transfer (first 1TB) | $0 |
| Domain (optional) | ~$12/year |
| **Total** | **~$5-7/month** |

---

## Architecture Overview

```
                    ┌─────────────┐
                    │   Users     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Nginx     │ (Port 80/443)
                    │  (Reverse   │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Gunicorn   │ (Port 8000)
                    │  (WSGI)     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Flask     │
                    │    App      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Image   │ │   OCR    │ │   Doc    │
        │Extractor │ │Processor │ │Processor │
        └──────────┘ └──────────┘ └──────────┘
```

---

## Quick Reference

```bash
# SSH into server
ssh -i ~/.ssh/LightsailDefaultKey.pem ubuntu@YOUR_IP

# Deploy code update
bash deploy/quick_deploy.sh YOUR_IP ~/.ssh/LightsailDefaultKey.pem

# Restart app after update
sudo supervisorctl restart image2text

# Check status
sudo supervisorctl status image2text

# View logs
sudo tail -f /var/log/image2text/error.log
```

---

**Your app will be live at: http://YOUR_PUBLIC_IP** 🚀
