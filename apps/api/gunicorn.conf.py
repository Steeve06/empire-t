"""Gunicorn settings for production. Tunable through environment variables."""

import multiprocessing
import os

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS") or min(multiprocessing.cpu_count() * 2 + 1, 5))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
worker_class = "gthread"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
forwarded_allow_ips = "*"
