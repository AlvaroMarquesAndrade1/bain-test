"""
Configuration management for the application.

TODO: Future improvements:
- [ ] Use Pydantic Settings for environment validation
- [ ] Add configuration for multiple environments
- [ ] Implement secret management with HashiCorp Vault
"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml


class Config:
    """Simple configuration management.

    Attributes:
        BASE_DIR: Base directory of the project
        DATA_DIR: Directory for data files
        MODEL_DIR: Directory for model files
        CONFIG_DIR: Directory for configuration files
        API_HOST: API host address
        API_PORT: API port number
        API_KEYS: Set of valid API keys
        MODEL_NAME: Name of the model
        MODEL_VERSION: Version of the model
        TRAIN_TEST_SPLIT: Train/test split ratio
        RANDOM_STATE: Random seed for reproducibility
    """

    def __init__(self):
        """Initialize configuration with default values and environment variables."""
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.MODEL_DIR = self.BASE_DIR / "models"
        self.CONFIG_DIR = self.BASE_DIR / "configs"

        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.API_KEYS = set(os.getenv("API_KEYS", "dev-key-123").split(","))

        self.MODEL_NAME = "property_valuation_model"
        self.MODEL_VERSION = "1.0.0"

        self.TRAIN_TEST_SPLIT = 0.2
        self.RANDOM_STATE = 42

    def get_model_path(self) -> Path:
        """Get current model path.

        Returns:
            Path: Full path to the current model file
        """
        return self.MODEL_DIR / f"{self.MODEL_NAME}.joblib"

    def get_train_data_path(self) -> Path:
        """Get training data path.

        Returns:
            Path: Full path to the training data file
        """
        return self.DATA_DIR / "train.csv"

    def get_test_data_path(self) -> Path:
        """Get test data path.

        Returns:
            Path: Full path to the test data file
        """
        return self.DATA_DIR / "test.csv"


config = Config()
