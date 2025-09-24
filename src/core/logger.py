"""
Logging configuration for monitoring and debugging.

TODO: Future improvements:
- [ ] Add log aggregation with ELK stack
- [ ] Implement structured logging with correlation IDs
- [ ] Add log rotation and archival
"""

import logging
import sys
from datetime import datetime
import json
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Converts log records to JSON format for better parsing
    and analysis in production environments.
    """

    def format(self, record):
        """Format log record as JSON.

        Args:
            record: LogRecord instance containing log information

        Returns:
            str: JSON formatted log string
        """
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        if hasattr(record, "prediction_id"):
            log_obj["prediction_id"] = record.prediction_id
        if hasattr(record, "api_key"):
            log_obj["api_key"] = record.api_key

        return json.dumps(log_obj)


def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup logger with JSON formatting.

    Args:
        name: Logger name, defaults to module name

    Returns:
        logging.Logger: Configured logger instance with JSON formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


logger: logging.Logger = setup_logger("property_friends")
