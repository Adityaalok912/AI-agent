import datetime
import json

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_agent_action(agent_name: str, message: str):
    print(f"[{timestamp()}] [{agent_name}] {message}")

def format_json(data):
    try:
        return json.dumps(data, indent=4)
    except Exception:
        return str(data)
import logging

def get_logger(name: str) -> logging.Logger:
    """Create and return a configured logger for consistent app logging."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
