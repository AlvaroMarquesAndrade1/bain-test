"""
Predictions endpoint for property valuation.

TODO: Future improvements:
- [ ] Add batch prediction endpoint
- [ ] Implement async predictions
- [ ] Add prediction explanations
- [ ] Store predictions for monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
import uuid
from pydantic import BaseModel, Field
import joblib
from pathlib import Path
import traceback

from src.core.config import config
from src.core.logger import logger

router = APIRouter(prefix="/api/v1")

MODEL_PATH = config.get_model_path()
MODEL_DATA = None

if MODEL_PATH.exists():
    MODEL_DATA = joblib.load(MODEL_PATH)
    logger.info(f"Model loaded from {MODEL_PATH}")
    if isinstance(MODEL_DATA, dict):
        logger.info(
            f"Model metadata loaded. Train cols: {MODEL_DATA.get('train_cols')}"
        )
else:
    logger.warning("No model found")


class PropertyInput(BaseModel):
    """Property information for prediction.

    Attributes:
        type: Property type (apartment, house, etc.)
        sector: Location sector in Santiago
        net_usable_area: Usable area in square meters
        net_area: Total area in square meters
        n_rooms: Number of rooms
        n_bathroom: Number of bathrooms
        latitude: Geographic latitude
        longitude: Geographic longitude
    """

    type: str = Field(..., example="apartment", description="Property type")
    sector: str = Field(..., example="Santiago Centro", description="Location sector")
    net_usable_area: float = Field(
        ..., gt=0, example=65.0, description="Usable area in m²"
    )
    net_area: float = Field(..., gt=0, example=70.0, description="Total area in m²")
    n_rooms: int = Field(..., ge=1, le=10, example=2, description="Number of rooms")
    n_bathroom: int = Field(
        ..., ge=1, le=5, example=1, description="Number of bathrooms"
    )
    latitude: float = Field(..., ge=-56, le=-17, example=-33.45, description="Latitude")
    longitude: float = Field(
        ..., ge=-76, le=-66, example=-70.65, description="Longitude"
    )


class PredictionResponse(BaseModel):
    """Response model for predictions.
    
    Attributes:
        prediction_id: Unique identifier for this prediction
        predicted_price: Predicted property price in CLP
        model_version: Version of the model used
        metrics: Optional model performance metrics
    """

    prediction_id: str = Field(..., description="Unique prediction identifier")
    predicted_price: float = Field(..., description="Predicted price in CLP")
    model_version: str = Field(..., description="Model version used")
    metrics: Optional[Dict[str, float]] = Field(None, description="Model metrics")


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key for authentication.
    
    Args:
        x_api_key: API key from request header
        
    Returns:
        str: Validated API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not x_api_key or x_api_key not in config.API_KEYS:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    property_data: PropertyInput,
    api_key: str = Depends(verify_api_key)
) -> PredictionResponse:
    """Make a property price prediction.
    
    Args:
        property_data: Property information for prediction
        api_key: Validated API key from dependency
        
    Returns:
        PredictionResponse: Prediction result with price and metadata
        
    Raises:
        HTTPException: 
            - 503: If model is not available
            - 500: If prediction fails
            
    Example:
        >>> POST /api/v1/predict
        >>> Headers: {"X-API-Key": "dev-key-123"}
        >>> Body: {
        ...   "type": "apartment",
        ...   "sector": "Las Condes",
        ...   "net_usable_area": 65,
        ...   "net_area": 70,
        ...   "n_rooms": 2,
        ...   "n_bathroom": 1,
        ...   "latitude": -33.45,
        ...   "longitude": -70.65
        ... }
    """
    prediction_id: str = str(uuid.uuid4())

    if MODEL_DATA is None:
        logger.error("Model not loaded")
        raise HTTPException(status_code=503, detail="Model not available")

    if isinstance(MODEL_DATA, dict):
        pipeline = MODEL_DATA["pipeline"]
        train_cols: List[str] = MODEL_DATA["train_cols"]
        metrics: Dict[str, float] = MODEL_DATA.get("metrics", {})
    else:
        pipeline = MODEL_DATA
        train_cols = [
            "type", "sector", "net_usable_area", "net_area",
            "n_rooms", "n_bathroom", "latitude", "longitude"
        ]
        metrics = {}

    logger.info(
        f"Prediction request received. ID: {prediction_id}",
        extra={"prediction_id": prediction_id, "api_key": api_key[:8] + "***"},
    )

    try:
        input_dict: Dict[str, Any] = property_data.model_dump()
        input_data: pd.DataFrame = pd.DataFrame([input_dict])
        
        input_data = input_data[train_cols]
        
        logger.info(f"Input columns: {input_data.columns.tolist()}")

        prediction: np.ndarray = pipeline.predict(input_data)
        predicted_price: float = float(prediction[0])

        response = PredictionResponse(
            prediction_id=prediction_id,
            predicted_price=predicted_price,
            model_version=config.MODEL_VERSION,
            metrics={
                "model_mape": metrics.get("mape", 0.4),
                "model_mae": metrics.get("mae", 5859),
            },
        )

        logger.info(
            f"Prediction successful: ${predicted_price:,.2f}",
            extra={"prediction_id": prediction_id},
        )

        return response

    except Exception as e:
        logger.error(
            f"Prediction failed: {str(e)}", 
            extra={"prediction_id": prediction_id}
        )
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction failed: {str(e)}"
        )