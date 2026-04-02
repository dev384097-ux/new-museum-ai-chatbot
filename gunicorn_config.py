import multiprocessing

# Worker Settings
# Formula: (2 * workers) + 1
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
threads = 2
timeout = 120

# Network Settings
bind = "0.0.0.0:5000"

# Logging Settings
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Performance Tuning
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
