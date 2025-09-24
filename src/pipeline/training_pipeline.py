"""
Training pipeline orchestration.

TODO: Future improvements:
- [ ] Add Apache Airflow for scheduling
- [ ] Implement data validation steps
- [ ] Add model validation before deployment
- [ ] Integrate with CI/CD
"""

from typing import Dict, Any

from src.data.loader import CSVDataLoader
from src.models.trainer import ModelTrainer
from src.core.logger import logger


class TrainingPipeline:
    """Orchestrates the training pipeline.

    Attributes:
        data_loader: DataLoader instance for loading data
        trainer: ModelTrainer instance for training models
    """

    def __init__(self) -> None:
        """Initialize pipeline with data loader and trainer."""
        self.data_loader = CSVDataLoader()
        self.trainer = ModelTrainer()

    def run(self) -> Dict[str, float]:
        """Run the complete training pipeline.

        Executes the following steps:
        1. Load training and test data
        2. Train and evaluate model
        3. Save trained model

        Returns:
            Dict[str, float]: Dictionary containing evaluation metrics
                - rmse: Root Mean Squared Error
                - mape: Mean Absolute Percentage Error
                - mae: Mean Absolute Error

        Raises:
            Exception: If any step in the pipeline fails
        """
        logger.info("Starting training pipeline")

        try:
            # Step 1: Load data
            logger.info("Step 1: Loading data")
            train_df, test_df = self.data_loader.load()

            # TODO: Add data validation step
            # Step 2: Validate data quality
            # self.validate_data(train_df, test_df)

            # Step 2: Train model and evaluate
            logger.info("Step 2: Training and evaluating model")
            metrics: Dict[str, float] = self.trainer.train(train_df, test_df)

            # Step 3: Save model
            logger.info("Step 3: Saving model")
            self.trainer.save_model()

            # TODO: Add model validation
            # Step 4: Validate model performance
            # self.validate_model(metrics)

            logger.info("Pipeline completed successfully")
            logger.info(
                f"Final metrics: MAPE={metrics['mape']:.4f}, "
                f"RMSE={metrics['rmse']:.2f}, MAE={metrics['mae']:.2f}"
            )
            return metrics

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise


def main() -> None:
    """Entry point for training pipeline.

    Creates and runs a training pipeline, then prints the results.
    """
    pipeline: TrainingPipeline = TrainingPipeline()
    metrics: Dict[str, float] = pipeline.run()

    logger.info(f"Training complete. Metrics: {metrics}")


if __name__ == "__main__":
    main()
