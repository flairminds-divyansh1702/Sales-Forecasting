# Sales-Forecasting
This repository is to create time series sales forecasting for the given dataset.

**To run this repository:**

Step 1: Install the requirements from requirements.txt using the command "pip install -r requirements.txt".
Step 2: To start the server enter the command "uvicorn app:app --reload".

**Workflow of the code is:**

upload-data -> train-model -> forecast -> forecast-comparison

**cURL for the APIs are:**

Upload Data:

curl --location 'http://127.0.0.1:8000/upload-data/upload-data' \
--form 'file=@"/C:/Users/HP/Downloads/dataset.csv"'

Train Model:

curl --location --request POST 'http://127.0.0.1:8000/train-model/train-model'

Forecast:

curl --location 'http://127.0.0.1:8000/forecast/forecast' \
--header 'Content-Type: application/json' \
--data '{
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
}'

Forecast Comparison:

curl --location 'http://127.0.0.1:8000/compare/forecast-comparison' \
--header 'Content-Type: application/json' \
--data '{
    "month": 1,
    "years": [2022, 2023, 2024]
}'

To look for the visual results of Forecast and Forecast Comparison in postman, instead of pressing send press "Send and Download".
This will download the html file which when opened, will show the charts of the forecast.