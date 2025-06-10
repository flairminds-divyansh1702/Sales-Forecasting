from .forecast import router as forecast_router
from .forecast import router as quick_forecast_router
from .upload_data import router as upload_router
from .train_model import router as train_router
from .forecast_comparison import router as comparison_router

__all__ = [
    "forecast_router",
    "quick_forecast_router",
    "upload_router",
    "train_router",
    "comparison_router"
]