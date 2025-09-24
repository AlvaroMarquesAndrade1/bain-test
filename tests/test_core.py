"""Basic unit tests for core functionality."""

import pytest
from pathlib import Path
import pandas as pd
import numpy as np

from src.core.config import config
from src.core.logger import logger
from src.data.loader import CSVDataLoader
from src.models.trainer import ModelTrainer


class TestConfig:
    """Test configuration management."""
    
    def test_config_loads(self):
        """Test that config loads successfully."""
        assert config is not None
        assert config.MODEL_NAME == "property_valuation_model"
        assert config.API_PORT == 8000
    
    def test_paths_exist(self):
        """Test that required paths are configured."""
        assert config.BASE_DIR.exists()
        assert isinstance(config.get_model_path(), Path)


class TestDataLoader:
    """Test data loading functionality."""
    
    def test_csv_loader_initialization(self):
        """Test CSVDataLoader can be initialized."""
        loader = CSVDataLoader()
        assert loader is not None
    
    def test_abstract_loader_interface(self):
        """Test abstract base class has required methods."""
        from src.data.loader import DataLoader
        
        # Should not be able to instantiate abstract class
        with pytest.raises(TypeError):
            DataLoader()


class TestModelTrainer:
    """Test model training functionality."""
    
    def test_trainer_initialization(self):
        """Test ModelTrainer can be initialized."""
        trainer = ModelTrainer()
        assert trainer.model is None
        assert trainer.metrics == {}
    
    def test_prepare_features(self):
        """Test feature preparation with dummy data."""
        trainer = ModelTrainer()
        
        # Create dummy data
        dummy_data = pd.DataFrame({
            'type': ['apartment'] * 10,
            'sector': ['Centro'] * 10,
            'net_usable_area': np.random.uniform(50, 100, 10),
            'net_area': np.random.uniform(60, 110, 10),
            'n_rooms': np.random.randint(1, 4, 10),
            'n_bathroom': np.random.randint(1, 3, 10),
            'latitude': np.random.uniform(-33.5, -33.4, 10),
            'longitude': np.random.uniform(-70.7, -70.6, 10),
            'price': np.random.uniform(50000, 200000, 10)
        })
        
        X_train, y_train, X_test, y_test, cat_cols = trainer.prepare_features(
            dummy_data, dummy_data
        )
        
        assert len(X_train) == len(y_train)
        assert 'price' not in X_train.columns
        assert cat_cols == ['type', 'sector']