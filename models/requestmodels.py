from pydantic import BaseModel, Field
from typing import List, Optional

class ForecastRequest(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    include_uncertainty: bool = Field(default=True, description="Include prediction intervals")

class ComparisonRequest(BaseModel):
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    years: List[int] = Field(..., description="List of years to compare")
    include_forecast_year: Optional[int] = Field(None, description="Year to include as forecast")