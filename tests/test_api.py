"""API endpoint tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.api.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Property Friends API"


class TestPredictionEndpoint:
    """Test prediction endpoint."""
    
    def test_prediction_without_api_key(self):
        """Test that prediction requires API key."""
        response = client.post("/api/v1/predict", json={})
        assert response.status_code == 401
    
    def test_prediction_with_invalid_data(self):
        """Test prediction with invalid input."""
        response = client.post(
            "/api/v1/predict",
            headers={"X-API-Key": "dev-key-123"},
            json={"invalid": "data"}
        )
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.routers.predictions.MODEL_DATA')
    def test_prediction_with_valid_data(self, mock_model):
        """Test prediction with valid input."""
        # Mock model prediction
        mock_pipeline = MagicMock()
        mock_pipeline.predict.return_value = [100000.0]
        mock_model.__getitem__.return_value = mock_pipeline
        mock_model.get.return_value = ['type', 'sector', 'net_usable_area', 
                                       'net_area', 'n_rooms', 'n_bathroom', 
                                       'latitude', 'longitude']
        
        valid_data = {
            "type": "apartment",
            "sector": "Las Condes",
            "net_usable_area": 65.0,
            "net_area": 70.0,
            "n_rooms": 2,
            "n_bathroom": 1,
            "latitude": -33.45,
            "longitude": -70.65
        }
        
        response = client.post(
            "/api/v1/predict",
            headers={"X-API-Key": "dev-key-123"},
            json=valid_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "prediction_id" in data
        assert "predicted_price" in data