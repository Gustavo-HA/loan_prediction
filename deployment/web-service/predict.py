from typing import Literal

import fastapi
import joblib
import pandas as pd
from pydantic import BaseModel, Field
import uvicorn

app = fastapi.FastAPI()

with open("./model.pkl", "rb") as model_file:
    model = joblib.load(model_file)

with open("./preprocessor.pkl", "rb") as preprocessor_file:
    preprocessor = joblib.load(preprocessor_file)

class PredictionRequest(BaseModel):
    Gender: Literal["Male", "Female"]
    Married: Literal["No", "Yes"]
    Dependents: Literal["0", "1", "2", "3+"]
    Education: Literal["Graduate", "Not Graduate"]
    Self_Employed: Literal["No", "Yes"]
    Property_Area: Literal["Urban", "Rural", "Semiurban"]
    ApplicantIncome: float | int = Field(..., description="Annual income of the applicant", ge=0.0)
    CoapplicantIncome: float | int = Field(..., description="Annual income of the co-applicant", ge=0.0)
    LoanAmount: float | int = Field(..., description="Loan amount in thousands", ge=9.0)
    Loan_Amount_Term: float | int = Field(..., description="Term of loan in months", gt=0.0, le=480.0)
    Credit_History: Literal[0, 1]


class PredictionResponse(BaseModel):
    prediction: Literal["Approved", "Rejected"]

# Hello world
@app.get("/")
def read_root():
    return {"message": "Welcome to the Loan Prediction API"}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Predicts loan approval based on the provided features.
    """
    
    df_request = pd.DataFrame([request.model_dump()])
    df_request = preprocessor.transform(df_request)
    prediction = model.predict(df_request)
    prediction = ["Approved" if pred == 1 else "Rejected" for pred in prediction]
    
    return {"prediction": prediction[0]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)