# Running Multiple Apps on Same Server

Guide to deploy the Image2Text app alongside your existing application on port 3000.

## Overview

Your server currently has:
- **Existing app** running on port 3000 (managed by PM2)
- **Image2Text app** will run on port 8001 (managed by Supervisor with Gunicorn)

**Both process managers (PM2 and Supervisor) will run together without conflicts.**

You have **3 deployment options**:

---

## Quick Start: Complete Deployment Steps

### Prerequisites
- AWS Lightsail instance running Ubuntu
- Existing app already deployed on port 3000
- SSH access to the server
- Domain name (optional, for subdomain/path setup)

### Step-by-Step Instructions

#### 1. SSH into Your Server
```bash
ssh -i ~/.ssh/LightsailDefaultKey.pem ubuntu@YOUR_SERVER_IP
```

#### 2. Clone the Repository
```bash
cd /home/ubuntu
git clone https://github.com/samdivyakumar/imagetotext_pyproj.git image2text_pyproj
cd image2text_pyproj
```

#### 3. Run Initial Setup
```bash
# Install system dependencies and create virtual environment
bash deploy/deploy.sh
```

This will:
- Install Python 3, pip, venv
- Install Tesseract OCR
- Install Nginx and Supervisor
- Create virtual environment
- Install Python packages

#### 4. Choose Your Deployment Method

**Option A: Subdomain (Recommended)**
```bash
# Replace with your actual subdomain
sudo bash deploy/configure_nginx.sh convert.yourdomain.com subdomain
```

**Option B: Path-based**
```bash
sudo bash deploy/configure_nginx.sh yourdomain.com path
# Then manually edit /etc/nginx/sites-available/default (see Option 2 below)
```

**Option C: Different Port (e.g., 8080)**
```bash
sudo bash deploy/configure_nginx.sh _ port 8080
```

#### 5. Start the Application
```bash
sudo bash deploy/configure_supervisor.sh
```

#### 6. Verify Deployment
```bash
# Check if app is running
sudo supervisorctl status image2text

# Check logs
sudo tail -f /var/log/image2text/error.log

# Test the app locally
curl http://localhost:8001/health
```

#### 7. Open Firewall Ports (if needed)

**For subdomain/path (uses port 80/443):**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

**For port-based deployment (e.g., port 8080):**
```bash
sudo ufw allow 8080/tcp
```

**Also open ports in AWS Lightsail Console:**
1. Go to Lightsail Console
2. Click on your instance
3. Go to "Networking" tab
4. Add Custom rule: TCP, Port 8080 (if using port-based)

#### 8. Set Up SSL (Optional but Recommended)

**For subdomain:**
```bash
sudo bash deploy/setup_ssl.sh convert.yourdomain.com
```

**For path-based (uses main domain SSL):**
```bash
sudo bash deploy/setup_ssl.sh yourdomain.com
```

#### 9. Access Your Applications

**Subdomain deployment:**
- Existing app: `http://yourdomain.com:3000`
- Image2Text: `http://convert.yourdomain.com`

**Path-based deployment:**
- Existing app: `http://yourdomain.com`
- Image2Text: `http://yourdomain.com/convert`

**Port-based deployment:**
- Existing app: `http://yourdomain.com:3000`
- Image2Text: `http://yourdomain.com:8080`

---

## Detailed Deployment Options

### Your Current Nginx Configuration

Your existing Nginx config (at `/etc/nginx/sites-available/default`):
```nginx
server {
    listen 80;
    server_name 3.7.243.78;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
}
```

---

### Recommended: Add Path-Based Routing

**This is the easiest option for your setup** - it won't affect your existing app at all.

#### Complete Modified Configuration

Edit your Nginx config:
```bash
sudo nano /etc/nginx/sites-available/default
```

Replace the entire content with this:
```nginx
server {
    listen 80;
    server_name 3.7.243.78;

    # Your existing app (unchanged)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # NEW: Image2Text Application
    location /convert {
        rewrite ^/convert(.*) $1 break;
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        client_max_body_size 16M;
    }

    # NEW: Static files for Image2Text
    location /convert/static {
        alias /home/ubuntu/image2text_pyproj/static;
        expires 30d;
    }
}
```

#### Deployment Steps for Your Server

```bash
# 1. SSH into your server
ssh -i ~/.ssh/LightsailDefaultKey.pem ubuntu@3.7.243.78

# 2. Clone the repository
cd /home/ubuntu
git clone https://github.com/samdivyakumar/imagetotext_pyproj.git image2text_pyproj
cd image2text_pyproj

# 3. Run initial setup
bash deploy/deploy.sh

# 4. Edit your existing Nginx configuration
sudo nano /etc/nginx/sites-available/default
# Copy the complete configuration shown above

# 5. Test Nginx configuration
sudo nginx -t

# 6. If test passes, restart Nginx
sudo systemctl restart nginx

# 7. Start the Image2Text app
sudo bash deploy/configure_supervisor.sh

# Check your existing app (PM2)
pm2 status
pm2 list

# Check Image2Text app (Supervisor)
sudo supervisorctl status image2text

# Test both apps locally
curl http://localhost:3000  # Your existing app
curl http://localhost:8001/health  # Image2Text app

# 9. Test via browser
# Existing app: http://3.7.243.78
# Image2Text: http://3.7.243.78/convert
```

#### Important Notes for PM2 + Supervisor Setup

**Your existing app (PM2):**
- Managed by: PM2
- Commands: `pm2 status`, `pm2 restart app-name`, `pm2 logs`
- Port: 3000

**Image2Text app (Supervisor):**
- Managed by: Supervisor
- Commands: `sudo supervisorctl status image2text`, `sudo supervisorctl restart image2text`
- Port: 8001

**Both services run independently** - PM2 manages your existing app, Supervisor manages Image2Text.
# Existing app: http://3.7.243.78
# Image2Text: http://3.7.243.78/convert
```

#### Access Your Applications

- **Existing App**: `http://3.7.243.78` → port 3000 (unchanged)
- **Image2Text App**: `http://3.7.243.78/convert` → port 8001 (new)

Both apps run independently without any conflicts! ✅

---

## Alternative Deployment Options

---

## Option 1: Subdomain (Recommended)

Deploy on a subdomain like `convert.yourdomain.com`

### Setup:

1. **Add DNS A Record:**
   - Type: A
   - Name: `convert` (or your preferred subdomain)
   - Value: Your server IP
   - TTL: 300

2. **Deploy the app:**
   ```bash
   cd /home/ubuntu/image2text_pyproj
   bash deploy/deploy.sh
   
   # Configure Nginx for subdomain
   sudo bash deploy/configure_nginx.sh convert.yourdomain.com subdomain
   
   # Start the app with Supervisor
   sudo bash deploy/configure_supervisor.sh
   ```

3. **Access your apps:**
   - Existing app: `http://yourdomain.com:3000` (or your configured domain)
   - Image2Text: `http://convert.yourdomain.com`

### Pros:
✅ Clean separation between apps  
✅ Easy SSL setup per app  
✅ No URL path conflicts  

---

## Option 2: Path-Based Routing

Deploy on a path like `yourdomain.com/convert`

### Setup:

1. **Deploy the app:**
   ```bash
   cd /home/ubuntu/image2text_pyproj
   bash deploy/deploy.sh
   
   # This will show you the config to add
   sudo bash deploy/configure_nginx.sh yourdomain.com path
   ```

2. **Manual step - Edit your existing Nginx config:**
   ```bash
   sudo nano /etc/nginx/sites-available/default
   ```

3. **Add this inside your existing `server` block:**
   ```nginx
   # Image2Text Application
   location /convert {
       rewrite ^/convert(.*) $1 break;
       proxy_pass http://127.0.0.1:8001;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_connect_timeout 300;
       proxy_send_timeout 300;
       proxy_read_timeout 300;
   }
   
   location /convert/static {
       alias /home/ubuntu/image2text_pyproj/static;
       expires 30d;
   }
   ```

4. **Test and restart Nginx:**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Start the app:**
   ```bash
   sudo bash deploy/configure_supervisor.sh
   ```

6. **Access your apps:**
   - Existing app: `http://yourdomain.com` (port 3000 or as configured)
   - Image2Text: `http://yourdomain.com/convert`

### Pros:
✅ Single domain  
✅ Single SSL certificate  

### Cons:
⚠️ Requires manual Nginx config editing  
⚠️ Potential URL conflicts  

---

## Option 3: Different Port

Expose Image2Text on a different public port like `yourdomain.com:8080`

### Setup:

1. **Deploy the app:**
   ```bash
   cd /home/ubuntu/image2text_pyproj
   bash deploy/deploy.sh
   
   # Configure Nginx to listen on port 8080
   sudo bash deploy/configure_nginx.sh _ port 8080
   
   # Start the app
   sudo bash deploy/configure_supervisor.sh
   ```

2. **Open port in AWS Lightsail:**
   - Go to Lightsail console
   - Select your instance
   - Go to "Networking" tab
   - Add Custom rule: TCP, Port 8080

3. **Access your apps:**
   - Existing app: `http://yourdomain.com:3000`
   - Image2Text: `http://yourdomain.com:8080`

### Pros:
✅ Complete isolation  
✅ Easy to set up  

### Cons:
⚠️ Requires opening additional firewall ports  
⚠️ Less professional URLs  

---

## Port Configuration Summary

| Application | Internal Port (Gunicorn/App) | External Port (Nginx) |
|-------------|------------------------------|----------------------|
| Existing App | 3000 | 80 or 3000 |
| Image2Text | 8001 | 80 (subdomain/path) or 8080 (port) |

---

## Complete Deployment Example (Subdomain)

```bash
# SSH into your server
ssh -i ~/.ssh/LightsailDefaultKey.pem ubuntu@YOUR_IP

# Clone the repository (PM2)
pm2 status
curl http://localhost:3000

# Check Image2Text app (Supervisor)
sudo supervisorctl status image2text
curl http://localhost:8001/health

# Check Nginx configurations and status
sudo nginx -t
sudo systemctl status nginx

# View all processes
pm2 list  # Your existing app
sudo supervisorctl status  # Image2Text app

# Check ports in use
sudo lsof -i :3000  # Your existing app
sudo lsof -i :8001  # Image2Text app
sudo lsof -i :80    # Nginx
sudo bash deploy/configure_supervisor.sh

# Check status
sudo supervisorctl status image2text
```

---

# Check PM2 apps (your existing app)
pm2 status
pm2 list

# Check Supervisor apps (Image2Text)
sudo supervisorctl status
```

### Managing Your Existing App (PM2):
```bash
# View status
pm2 status

# Restart
pm2 restart <app-name>

# View logs
pm2 logs

# Stop/Start
pm2 stop <app-name>
pm2 start <app-name>
```

### Managing Image2Text App (Supervisor):
```bash
# View status
sudo supervisorctl status image2text

# Restart
sudo supervisorctl restart image2text

# Stop/Start
sudo supervisorctl stop image2text
sudo supervisorctl start image2text

# View logs
sudo tail -f /var/log/image2text/error.log
sudo tail -f /var/log/image2text/access.log
```

### View Nginx logs (affects both apps):
```bash
# Access logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/image2text_access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/image2text_error.log
```

### Restart Nginx (if configuration changed):
```bash
sudo nginx -t  # Test configuration first
sudo systemctl restart nginx
```

---

## Managing Multiple Apps

### Existing app (PM2) not working:
```bash
# Check PM2 status
pm2 status
pm2 logs

# Restart PM2 app
pm2 restart <app-name>

# Check if port 3000 is available
sudo lsof -i :3000
```

### Image2Text app not starting:
```bash
# Check supervisor logs
sudo tail -50 /var/log/supervisor/supervisord.log

# Check app logs
sudo tail -50 /var/log/image2text/error.log

# Check if port 8001 is available
sudo lsof -i :8001

# Restart app
sudo supervisorctl restart image2text

# Reread and update supervisor config
sudo supervisorctl reread
sudo supervisorctl update
```

### Both apps not accessible via web:
```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -50 /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
### View logs:
```bash
# Image2Text logs
sudo tail -f /var/log/image2text/error.log

# Nginx logs
sudo tail -f /var/log/nginx/image2text_access.log
```

---

## Firewall Configuration

If using UFW firewall:

```bash
# Allow existing app port (if not already allowed)
sudo ufw allow 3000/tcp

# For subdomain/path deployment (uses port 80/443)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# For port-based deployment
sudo ufw allow 8080/tcp

# Check firewall status
sudo ufw status
```

---

## SSL Setup (Subdomain)

To add SSL to your subdomain:

```bash
sudo bash deploy/setup_ssl.sh convert.yourdomain.com
```

For path-based deployment, SSL is shared with your main domain.

---

## Troubleshooting

### Common Error: "image2text: ERROR (no such file)"

This error means Supervisor can't find required files or the Gunicorn executable.

**Quick fix - Run troubleshooting script:**
```bash
cd /home/ubuntu/image2text_pyproj
bash deploy/troubleshoot.sh
```

This will check all requirements and show you what's missing.

**Manual diagnostic steps:**
```bash
# 1. Verify app directory and files exist
ls -la /home/ubuntu/image2text_pyproj/app.py
ls -la /home/ubuntu/image2text_pyproj/gunicorn.conf.py

# 2. Check virtual environment and Gunicorn
ls -la /home/ubuntu/image2text_pyproj/venv/bin/gunicorn
/home/ubuntu/image2text_pyproj/venv/bin/gunicorn --version

# 3. Verify Python packages are installed
cd /home/ubuntu/image2text_pyproj
source venv/bin/activate
pip list | grep -E "flask|gunicorn|python-docx|pytesseract"
deactivate

# 4. Test Gunicorn command manually
cd /home/ubuntu/image2text_pyproj
/home/ubuntu/image2text_pyproj/venv/bin/gunicorn --config gunicorn.conf.py app:app
# If it starts successfully, press Ctrl+C and continue below

# 5. Check logs for details
sudo tail -50 /var/log/supervisor/supervisord.log
sudo tail -50 /var/log/image2text/error.log
```

**Solution - If deploy.sh wasn't run:**
```bash
cd /home/ubuntu/image2text_pyproj
bash deploy/deploy.sh
sudo bash deploy/configure_supervisor.sh
```

---

### Existing app (PM2) not working:
```bash
# Check PM2 status
pm2 status
pm2 logs

# Restart PM2 app
pm2 restart <app-name>

# Check if port 3000 is available
sudo lsof -i :3000
```

### Image2Text app not starting:
```bash
# Check supervisor logs
sudo tail -50 /var/log/supervisor/supervisord.log

# Check app logs
sudo tail -50 /var/log/image2text/error.log

# Check if port 8001 is available
sudo lsof -i :8001

# Restart app
sudo supervisorctl restart image2text

# Reread and update supervisor config
sudo supervisorctl reread
sudo supervisorctl update
```

### Both apps not accessible via web:
```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Check Nginx error logs
sudo tail -50 /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### Port already in use:
```bash
# Check what's using a port
sudo lsof -i :8001
sudo netstat -tulpn | grep 8001
```

### Nginx conflicts:
```bash
# Test configuration
sudo nginx -t

# Check for conflicting server blocks
sudo nginx -T | grep "server_name"
```

---

## Recommended Setup

For production, I recommend:

1. **Use Option 1 (Subdomain)** for clean separation
2. Set up DNS: `convert.yourdomain.com` → Your server IP
3. Enable SSL for both domains
4. Keep apps in separate directories:
   - Existing: `/home/ubuntu/app` (port 3000)
   - Image2Text: `/home/ubuntu/image2text_pyproj` (port 8001)

This gives you:
- ✅ `https://yourdomain.com` (existing app)
- ✅ `https://convert.yourdomain.com` (Image2Text app)

Both apps run independently without interference! 🚀
