from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from models.requestmodels import ComparisonRequest
import pandas as pd
import plotly.graph_objects as go
import state
import io

router = APIRouter()

@router.post("/forecast-comparison")
async def forecast_comparison(request: ComparisonRequest):
    """Compare historical data for a specific month across multiple years with optional forecast"""
    
    if state.global_daily_sales is None:
        raise HTTPException(status_code=400, detail="Please upload data first")
    
    try:
        fig = go.Figure()
        
        colors = ['blue', 'green', 'orange', 'purple', 'red', 'brown', 'pink', 'gray']
        line_styles = ['solid', 'dash', 'dot', 'dashdot']
        
        combined_data = []
        
        # Process historical years
        for i, year in enumerate(request.years):
            start_date = f"{year}-{request.month:02d}-01"
            end_date = pd.to_datetime(start_date) + relativedelta(months=1) - timedelta(days=1)
            
            # Filter data for this month/year
            month_data = state.global_daily_sales[
                (state.global_daily_sales['transaction_date'] >= start_date) & 
                (state.global_daily_sales['transaction_date'] <= end_date.strftime('%Y-%m-%d'))
            ].copy()
            
            if len(month_data) > 0:
                month_data['day'] = month_data['transaction_date'].dt.day
                month_data['year'] = str(year)
                combined_data.append(month_data)
                
                fig.add_trace(go.Scatter(
                    x=month_data['day'],
                    y=month_data['spend'],
                    mode='lines+markers',
                    name=str(year),
                    line=dict(
                        color=colors[i % len(colors)], 
                        dash=line_styles[i % len(line_styles)], 
                        width=2
                    ),
                    marker=dict(size=6),
                    hovertemplate=f'Day %{{x}}<br>Sales: €%{{y:,.0f}}<extra>{year}</extra>'
                ))
        
        # Add forecast year if specified and model is available
        if request.include_forecast_year and state.global_model is not None:
            forecast_year = request.include_forecast_year
            start_date = f"{forecast_year}-{request.month:02d}-01"
            end_date = pd.to_datetime(start_date) + relativedelta(months=1) - timedelta(days=1)
            
            future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
            future_df = pd.DataFrame({'ds': future_dates})
            forecast = state.global_model.predict(future_df)
            
            forecast_data = pd.DataFrame({
                'transaction_date': forecast['ds'],
                'spend': forecast['yhat'],
                'day': forecast['ds'].dt.day,
                'year': f'{forecast_year} (Forecast)'
            })
            
            combined_data.append(forecast_data)
            
            fig.add_trace(go.Scatter(
                x=forecast_data['day'],
                y=forecast_data['spend'],
                mode='lines+markers',
                name=f'{forecast_year} (Forecast)',
                line=dict(color='red', dash='dashdot', width=3),
                marker=dict(size=8, symbol='diamond'),
                hovertemplate=f'Day %{{x}}<br>Forecast: €%{{y:,.0f}}<extra>{forecast_year} (Forecast)</extra>'
            ))
        
        # Update layout
        month_name = pd.to_datetime(f"2000-{request.month:02d}-01").strftime('%B')
        fig.update_layout(
            title=f"📊 Daily Sales Comparison - {month_name}",
            xaxis_title="Day of Month",
            yaxis_title="Sales (€)",
            xaxis=dict(tickmode='linear', tick0=1, dtick=1),
            template='plotly_white',
            legend_title="Year",
            hovermode="x unified",
            width=1000,
            height=500
        )
        
        # Calculate summary statistics
        summary = {}
        for data in combined_data:
            year = data['year'].iloc[0]
            summary[year] = {
                "total_sales": float(data['spend'].sum()),
                "average_daily_sales": float(data['spend'].mean()),
                "max_daily_sales": float(data['spend'].max()),
                "min_daily_sales": float(data['spend'].min()),
                "days_with_data": len(data)
            }
        
        html = fig.to_html(full_html=True, include_plotlyjs='cdn')
        html_bytes = io.BytesIO(html.encode("utf-8"))
        return StreamingResponse(
            html_bytes,
            media_type="text/html",
            headers={
                "Content-Disposition": f'attachment; filename="forecast_comparison.html"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating comparison: {str(e)}")