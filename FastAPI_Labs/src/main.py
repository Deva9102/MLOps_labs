from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, conlist
from predict import predict_data

app = FastAPI(title="Digits Classifier API")

class DigitData(BaseModel):
    features: conlist(float, min_length=64, max_length=64)

class DigitResponse(BaseModel):
    prediction: int

@app.get("/", status_code=status.HTTP_200_OK)
async def health_ping():
    return {"status": "healthy"}

@app.post("/predict", response_model=DigitResponse)
async def predict_digit(payload: DigitData):
    try:
        pred = predict_data(payload.features)
        return DigitResponse(prediction=int(pred[0]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

