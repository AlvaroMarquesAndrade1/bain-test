"""
Data loading abstraction for future database integration.

TODO: Future improvements:
- [ ] Add data validation with Great Expectations
- [ ] Implement incremental data loading
- [ ] Add data versioning with DVC
- [ ] Cache processed data in Redis
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Tuple, Optional
from pathlib import Path

from src.core.config import config
from src.core.logger import logger


class DataLoader(ABC):
    """Abstract base class for data loading.

    Provides interface for different data sources (CSV, Database, API, etc.)
    to ensure consistent data loading across the application.
    """

    @abstractmethod
    def load(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load train and test data.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Training and test dataframes
        """
        pass

    @abstractmethod
    def save(self, df: pd.DataFrame, path: str) -> None:
        """Save data to storage.

        Args:
            df: DataFrame to save
            path: Destination path
        """
        pass


class CSVDataLoader(DataLoader):
    """CSV file data loader implementation.

    Attributes:
        train_path: Path to training data CSV file
        test_path: Path to test data CSV file
    """

    def __init__(
        self, train_path: Optional[str] = None, test_path: Optional[str] = None
    ) -> None:
        """Initialize CSV data loader.

        Args:
            train_path: Optional path to training data, defaults to config
            test_path: Optional path to test data, defaults to config
        """
        self.train_path: Path = (
            Path(train_path) if train_path else config.get_train_data_path()
        )
        self.test_path: Path = (
            Path(test_path) if test_path else config.get_test_data_path()
        )

    def load(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load train and test data from CSV files.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Training and test dataframes

        Raises:
            FileNotFoundError: If CSV files are not found
            pd.errors.ParserError: If CSV files are malformed
        """
        logger.info(f"Loading data from {self.train_path} and {self.test_path}")

        # TODO: Add data validation
        # - Check for missing values
        # - Validate data types
        # - Check for outliers

        if not self.train_path.exists():
            raise FileNotFoundError(f"Training data not found: {self.train_path}")
        if not self.test_path.exists():
            raise FileNotFoundError(f"Test data not found: {self.test_path}")

        train_df = pd.read_csv(self.train_path)
        test_df = pd.read_csv(self.test_path)

        logger.info(f"Loaded train: {train_df.shape}, test: {test_df.shape}")
        return train_df, test_df

    def save(self, df: pd.DataFrame, path: str) -> None:
        """Save dataframe to CSV.

        Args:
            df: DataFrame to save
            path: Destination file path
        """
        df.to_csv(path, index=False)
        logger.info(f"Data saved to {path}")


# Future implementations:
class DatabaseDataLoader(DataLoader):
    """
    Database data loader - TO BE IMPLEMENTED.

    Example implementation:
    def __init__(self, connection_string: str):
        self.connection = create_engine(connection_string)

    def load(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        train_query = "SELECT * FROM property_train"
        test_query = "SELECT * FROM property_test"
        return pd.read_sql(train_query, self.connection), pd.read_sql(test_query, self.connection)

    Note:
        This is a placeholder for future database integration.
        Implementation will depend on specific database requirements.
    """

    def load(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Not implemented yet."""
        raise NotImplementedError("Database loader will be implemented in Phase 2")

    def save(self, df: pd.DataFrame, path: str) -> None:
        """Not implemented yet."""
        raise NotImplementedError("Database save will be implemented in Phase 2")
