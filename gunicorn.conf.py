# Configuração otimizada do Gunicorn para evitar worker starvation
import multiprocessing
import os

# Worker process configuration
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
threads = 4  # Threads por worker para lidar com I/O bloqueante

# Timeout configuration - tempos menores para falhar rapidamente
timeout = 60  # Reduzir de 120s para 60s
keepalive = 5
graceful_timeout = 30

# Performance optimization
preload_app = True
max_requests = 2000
max_requests_jitter = 200

# Connection settings
bind = "0.0.0.0:5000"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Memory management
worker_tmp_dir = "/dev/shm"  # Use RAM for worker temp files

print(f"🚀 Gunicorn configurado: {workers} workers, {threads} threads/worker, timeout={timeout}s")