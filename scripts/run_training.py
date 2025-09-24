"""Script to run the training pipeline."""

import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent))

from src.pipeline.training_pipeline import TrainingPipeline
from src.core.logger import logger


def main() -> None:
    """Run training pipeline and display results.

    Executes the complete training pipeline and prints
    formatted results to console.
    """
    logger.info("Starting training script")

    pipeline: TrainingPipeline = TrainingPipeline()
    metrics: Dict[str, float] = pipeline.run()

    print("\n" + "=" * 50)
    print("Training Complete!")
    print("=" * 50)
    print(f"RMSE: {metrics['rmse']:.4f}")
    print(f"MAPE: {metrics['mape']:.4f}")
    print(f"MAE:  {metrics['mae']:.0f}")


if __name__ == "__main__":
    main()
