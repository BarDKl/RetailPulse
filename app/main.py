from fastapi import FastAPI
from pydantic import BaseModel
from app.services import run_model
app = FastAPI(title = 'Retail Prediction API')


class CustomerInput(BaseModel):
    recency: int
    frequency: float
    monetary: float

@app.get("/")
def home():
    model_status = "Active" if run_model.model else "Inactive"
    return {'message':'System is online'}

@app.post("/predict")
def predict_segment(data: CustomerInput):
    segment = run_model.predict(
        data.recency,
        data.frequency,
        data.monetary
    )

    return {
        "customer_data": data,
        "predicted_segment": segment,
        "predicted_spend": f"This customer is a {segment}"
    }