from fastapi import FastAPI
from pydantic import BaseModel
from app.services import run_model
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan_models(app: FastAPI):
    run_model.load_models()
    yield

app = FastAPI(title = 'Retail Prediction API', lifespan = lifespan_models)


class CustomerInput(BaseModel):
    recency: int
    frequency: float
    monetary: float
    customer_id: int

@app.get("/")
def home():
    rfm_status = 'RFM Active' if run_model.rfm_model else 'RFM Inactive'
    clv_status = 'CLV Active' if run_model.clv_model else 'CLV Inactive'
    return {'status1': rfm_status, 'status2': clv_status}

@app.post("/predict")
async def predict_segment(data: CustomerInput):
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
        "predicted_future_spend": f"{predicted_spend}£", # Return as a formatted string
    }