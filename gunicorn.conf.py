# Gunicorn configuration file for production deployment

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 4  # Recommended: 2 * CPU cores + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120  # OCR processing can take time
keepalive = 2

# Process naming
proc_name = "image2text"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (uncomment and configure for HTTPS)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# Environment variables
raw_env = [
    "FLASK_ENV=production",
]
