#!/bin/bash
# Setup SSL certificate using Let's Encrypt (Certbot)
# Run this AFTER you have a domain name pointing to your server

set -e

DOMAIN="$1"

if [ -z "$DOMAIN" ]; then
    echo "Usage: sudo bash setup_ssl.sh your-domain.com"
    exit 1
fi

echo "=========================================="
echo "Setting up SSL for $DOMAIN"
echo "=========================================="

# Install Certbot
echo "Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
echo "Obtaining SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

# Setup auto-renewal
echo "Setting up auto-renewal..."
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "✅ SSL certificate installed successfully!"
echo ""
echo "Your site is now available at: https://$DOMAIN"
echo ""
echo "Certificate auto-renewal is enabled."
echo "To manually renew: sudo certbot renew"
