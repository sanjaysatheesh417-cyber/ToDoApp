import os

bind = "0.0.0.0:8006"

worker_class = "uvicorn.workers.UvicornWorker"
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
timeout = 30
graceful_timeout = 5
keepalive = 5
loglevel = "info"
accesslog = "-"
errorlog = "-"
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "127.0.0.1")