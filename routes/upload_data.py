from fastapi import APIRouter, HTTPException, UploadFile, File
import state
import pandas as pd
import io

router = APIRouter()

@router.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """Upload CSV data with 'transaction_date' and 'spend' columns"""
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        if 'transaction_date' not in df.columns or 'spend' not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail="CSV must contain 'transaction_date' and 'spend' columns"
            )
        
        # Convert date column
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df = df.sort_values(by='transaction_date')
        
        # Outlier detection
        Q1 = df['spend'].quantile(0.15)
        Q3 = df['spend'].quantile(0.85)
        IQR = Q3 - Q1
        lower_bound = Q1 - 2.0 * IQR
        upper_bound = Q3 + 2.0 * IQR
        
        outliers = df[(df['spend'] < lower_bound) | (df['spend'] > upper_bound)]
        df_clean = df[(df['spend'] >= lower_bound) & (df['spend'] <= upper_bound)]
        
        # Create daily aggregation
        state.global_daily_sales = df_clean.groupby('transaction_date')['spend'].sum().reset_index()
        state.global_data = df_clean
        
        return {
            "message": "Data uploaded successfully",
            "total_records": len(df),
            "outliers_removed": len(outliers),
            "clean_records": len(df_clean),
            "daily_records": len(state.global_daily_sales),
            "date_range": {
                "start": df_clean['transaction_date'].min().isoformat(),
                "end": df_clean['transaction_date'].max().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")