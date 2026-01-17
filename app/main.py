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
    model_status = "Active" if run_model.rfm_model else "Inactive"
    return {'message':'System is online'}

@app.post("/predict")
def predict_segment(data: CustomerInput):
    predicted_segment = run_model.predict_rfm(
        data.recency,
        data.frequency,
        data.monetary
    )
    predicted_spend = run_model.predict_clv(
        data.recency,
        data.frequency,
        data.monetary)

    return {
        "customer_id": data.customer_id,
        "segment": predicted_segment,
        "predicted_future_spend": f"${predicted_spend}", # Return as a formatted string
    }