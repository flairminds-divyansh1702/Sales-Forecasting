from fastapi import FastAPI
from routes.upload_data import router as upload_router
from routes.train_model import router as train_router
from routes.forecast import router as forecast_router
from routes.forecast_comparison import router as comparison_router

app = FastAPI(
    title="Sales Forecasting API",
    description="Advanced time series forecasting API using Prophet with dynamic forecasting capabilities",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint that provides basic API information"""
    return {"message": "Sales Forecasting", "docs": "/docs"}

app.include_router(upload_router, prefix="/upload-data", tags=["Upload Data"])
app.include_router(train_router, prefix="/train-model", tags=["Train Model"])
app.include_router(forecast_router, prefix="/forecast", tags=["Forecast"])
app.include_router(comparison_router, prefix="/compare", tags=["Forecast Comparison"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)