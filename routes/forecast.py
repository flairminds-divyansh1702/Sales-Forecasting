from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from models.responsemodels import ForecastResponse
from models.requestmodels import ForecastRequest
import pandas as pd
import plotly.graph_objects as go
import state

router = APIRouter()

@router.post("/forecast", response_model=ForecastResponse)
async def generate_forecast(request: ForecastRequest):
    """Generate forecasts for any specified date range"""
    
    if state.global_model is None:
        raise HTTPException(status_code=400, detail="Please train the model first")
    
    try:
        start_date = pd.to_datetime(request.start_date)
        end_date = pd.to_datetime(request.end_date)
        
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Start date must be before end date")
        
        # Create future dataframe
        future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        future_df = pd.DataFrame({'ds': future_dates})
        
        # Generate forecast
        forecast = state.global_model.predict(future_df)
        
        # Prepare response data
        forecast_data = []
        for _, row in forecast.iterrows():
            entry = {
                "date": row['ds'].strftime('%Y-%m-%d'),
                "forecast": float(row['yhat']),
                "day_of_week": row['ds'].strftime('%A'),
                "month": row['ds'].strftime('%B'),
                "year": int(row['ds'].year)
            }
            
            if request.include_uncertainty:
                entry.update({
                    "lower_bound": float(row['yhat_lower']),
                    "upper_bound": float(row['yhat_upper'])
                })
            
            forecast_data.append(entry)
        
        # Summary statistics
        summary = {
            "total_days": len(forecast_data),
            "average_daily_forecast": float(forecast['yhat'].mean()),
            "total_forecast": float(forecast['yhat'].sum()),
            "min_forecast": float(forecast['yhat'].min()),
            "max_forecast": float(forecast['yhat'].max()),
            "std_forecast": float(forecast['yhat'].std())
        }
        
        # Create visualization data for Plotly
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='green', width=2),
            marker=dict(size=4),
            hovertemplate='Date: %{x}<br>Forecast: €%{y:,.0f}<extra></extra>'
        ))
        
        if request.include_uncertainty:
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat_upper'],
                fill=None,
                mode='lines',
                line_color='rgba(0,100,80,0)',
                showlegend=False,
                hoverinfo='skip'
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat_lower'],
                fill='tonexty',
                mode='lines',
                line_color='rgba(0,100,80,0)',
                name='Prediction Interval',
                fillcolor='rgba(0,100,80,0.2)',
                hovertemplate='Lower: €%{y:,.0f}<extra></extra>'
            ))
        
        fig.update_layout(
            title=f"Sales Forecast: {request.start_date} to {request.end_date}",
            xaxis_title="Date",
            yaxis_title="Forecasted Sales (€)",
            template='plotly_white',
            hovermode="x unified",
            width=1000,
            height=500
        )

        # Append forecast data to global_daily_sales
        forecast_append_df = forecast[['ds', 'yhat']].copy()
        forecast_append_df.rename(columns={'ds': 'transaction_date', 'yhat': 'spend'}, inplace=True)

        # Ensure no overlap with existing transaction dates
        forecast_append_df['transaction_date'] = pd.to_datetime(forecast_append_df['transaction_date'])
        state.global_daily_sales['transaction_date'] = pd.to_datetime(state.global_daily_sales['transaction_date'])

        # Append forecasted rows (avoid duplicates)
        state.global_daily_sales = pd.concat(
            [state.global_daily_sales, forecast_append_df]
        ).drop_duplicates(subset=['transaction_date'], keep='last').reset_index(drop=True)

        # At the end of generate_forecast:
        html = fig.to_html(full_html=True, include_plotlyjs='cdn')
        return HTMLResponse(content=html)

        
        # return ForecastResponse(
        #     forecast_data=forecast_data,
        #     summary=summary,
        #     visualization_data=visualization_data
        # )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")