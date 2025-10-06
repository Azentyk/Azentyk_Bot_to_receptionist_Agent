import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.getcwd(), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.txt")

def setup_logging():
    """Configure logging with rotating .txt file handler (works for FastAPI/Azure)."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

    # Rotating text log file (app.txt, app.txt.1, etc.)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,             # Keep last 5 rotated files
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    # Console output (important for Azure & Docker logs)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Define log format
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format)

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )

    logging.getLogger().info("✅ Logging initialized. Logs will be written to %s", LOG_FILE)

    return logging.getLogger("app_logger")  # Return named logger