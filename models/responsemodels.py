from pydantic import BaseModel
from typing import List, Dict, Any

class ModelTrainingResponse(BaseModel):
    message: str
    training_days: int
    test_days: int
    mae: float
    rmse: float
    mape: float
    model_trained: bool

class ForecastResponse(BaseModel):
    forecast_data: List[Dict[str, Any]]
    summary: Dict[str, Any]
    visualization_data: Dict[str, Any]