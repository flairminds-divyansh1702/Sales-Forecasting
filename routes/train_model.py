from fastapi import APIRouter, HTTPException
from models.responsemodels import ModelTrainingResponse
from prophet import Prophet
import pandas as pd
import numpy as np
import state
from sklearn.metrics import mean_absolute_error, mean_squared_error


router = APIRouter()

@router.post("/train-model", response_model=ModelTrainingResponse)
async def train_model():
    """Train the Prophet forecasting model"""
    
    if state.global_daily_sales is None:
        raise HTTPException(status_code=400, detail="Please upload data first")
    
    try:
        # Filter last 2 years for training
        cutoff_date = state.global_daily_sales['transaction_date'].max() - pd.DateOffset(years=2)
        df_two_years = state.global_daily_sales[state.global_daily_sales['transaction_date'] >= cutoff_date]
        
        # Train-test split
        train_end = pd.to_datetime('2022-12-31')
        train = df_two_years[df_two_years['transaction_date'] <= train_end]
        test = df_two_years[df_two_years['transaction_date'] > train_end]
        
        # Prepare for Prophet
        train_df = train[['transaction_date', 'spend']].rename(columns={'transaction_date': 'ds', 'spend': 'y'})
        test_df = test[['transaction_date', 'spend']].rename(columns={'transaction_date': 'ds', 'spend': 'y'})
        
        # Create and train Prophet model
        state.global_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.1,
            seasonality_prior_scale=10.0,
            interval_width=0.8,
            mcmc_samples=0
        )
        
        # Add custom seasonalities
        state.global_model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Fit the model
        state.global_model.fit(train_df)
        
        # Evaluate model if test data exists
        mae, rmse, mape = 0, 0, 0
        if len(test_df) > 0:
            future = state.global_model.make_future_dataframe(periods=len(test_df), freq='D')
            forecast = state.global_model.predict(future)
            test_forecast = forecast[forecast['ds'] > train_end].copy()
            
            merged_df = pd.merge(test_df, test_forecast[['ds', 'yhat']], on='ds', how='inner')
            if len(merged_df) > 0:
                mae = mean_absolute_error(merged_df['y'], merged_df['yhat'])
                rmse = np.sqrt(mean_squared_error(merged_df['y'], merged_df['yhat']))
                mape = np.mean(np.abs((merged_df['y'] - merged_df['yhat']) / merged_df['y'])) * 100
        
        return ModelTrainingResponse(
            message="Model trained successfully",
            training_days=len(train_df),
            test_days=len(test_df),
            mae=float(mae),
            rmse=float(rmse),
            mape=float(mape),
            model_trained=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")