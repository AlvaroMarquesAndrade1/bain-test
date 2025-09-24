"""
Model training module.

TODO: Future improvements:
- [ ] Add hyperparameter tuning with Optuna
- [ ] Implement cross-validation
- [ ] Add feature engineering pipeline
- [ ] Integrate MLflow for experiment tracking
"""

import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from category_encoders import TargetEncoder
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_percentage_error,
    mean_absolute_error,
)
import joblib
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Any

from src.core.config import config
from src.core.logger import logger


class ModelTrainer:
    """Model training handler following notebook specifications.

    Attributes:
        model: Trained sklearn Pipeline or None if not trained
        metrics: Dictionary containing evaluation metrics
        train_cols: List of column names used for training
    """

    def __init__(self):
        """Initialize ModelTrainer with empty state."""
        self.model: Optional[Pipeline] = None
        self.metrics: Dict[str, float] = {}
        self.train_cols: Optional[List[str]] = None

    def prepare_features(
        self, train_df: pd.DataFrame, test_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, List[str]]:
        """Prepare features exactly as in the notebook.

        Args:
            train_df: Training dataframe with features and target
            test_df: Test dataframe with features and target

        Returns:
            Tuple containing:
                - X_train: Training features
                - y_train: Training target
                - X_test: Test features
                - y_test: Test target
                - categorical_cols: List of categorical column names
        """
        self.train_cols = [
            col for col in train_df.columns if col not in ["id", "target", "price"]
        ]

        categorical_cols = ["type", "sector"]
        target = "price"

        logger.info(f"Training columns: {self.train_cols}")
        logger.info(f"Categorical columns: {categorical_cols}")

        X_train = train_df[self.train_cols]
        y_train = train_df[target]
        X_test = test_df[self.train_cols]
        y_test = test_df[target]

        return X_train, y_train, X_test, y_test, categorical_cols

    def create_pipeline(self, categorical_cols: List[str]) -> Pipeline:
        """Create pipeline exactly as in the notebook.

        Args:
            categorical_cols: List of categorical column names to encode

        Returns:
            Pipeline: Scikit-learn pipeline with preprocessing and model
        """
        categorical_transformer = TargetEncoder()

        preprocessor = ColumnTransformer(
            transformers=[("categorical", categorical_transformer, categorical_cols)]
        )

        steps: List[Tuple[str, Any]] = [
            ("preprocessor", preprocessor),
            (
                "model",
                GradientBoostingRegressor(
                    learning_rate=0.01,
                    n_estimators=300,
                    max_depth=5,
                    loss="absolute_error",
                    random_state=42,
                ),
            ),
        ]

        pipeline = Pipeline(steps)
        return pipeline

    def train(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, float]:
        """Train the model exactly as in the notebook.

        Args:
            train_df: Training dataframe with features and target
            test_df: Test dataframe with features and target

        Returns:
            Dict[str, float]: Dictionary containing evaluation metrics
                - rmse: Root Mean Squared Error
                - mape: Mean Absolute Percentage Error
                - mae: Mean Absolute Error

        Raises:
            Exception: If training fails for any reason
        """
        logger.info("Starting model training (notebook version)")
        logger.info(f"Train shape: {train_df.shape}, Test shape: {test_df.shape}")

        X_train, y_train, X_test, y_test, categorical_cols = self.prepare_features(
            train_df, test_df
        )

        self.model = self.create_pipeline(categorical_cols)

        try:
            logger.info("Fitting model...")
            self.model.fit(X_train, y_train)
            logger.info("Model fitted successfully")

            logger.info("Making predictions...")
            test_predictions = self.model.predict(X_test)

            rmse: float = np.sqrt(mean_squared_error(test_predictions, y_test))
            mape: float = mean_absolute_percentage_error(test_predictions, y_test)
            mae: float = mean_absolute_error(test_predictions, y_test)

            self.metrics = {"rmse": rmse, "mape": mape, "mae": mae}

            logger.info(
                f"Training complete. RMSE: {rmse:.2f}, MAPE: {mape:.4f}, MAE: {mae:.2f}"
            )

        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise

        return self.metrics

    def save_model(self, path: Optional[str] = None) -> None:
        """Save trained model and column information.

        Args:
            path: Optional custom path to save model. If None, uses
                  default path with timestamp.
        """
        if path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = config.MODEL_DIR / f"{config.MODEL_NAME}_{timestamp}.joblib"

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            "pipeline": self.model,
            "train_cols": self.train_cols,
            "metrics": self.metrics,
        }

        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")

        current_path = config.get_model_path()
        joblib.dump(model_data, current_path)
        logger.info(f"Model saved as current: {current_path}")
