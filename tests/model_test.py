import json

import deployment.model as model_module
import joblib
import pandas as pd


def test_prepare_features():
    input_record = {
        "input": {
            "Gender": "Male",
            "Married": "Yes",
            "Dependents": "2",
            "Education": "Graduate",
            "Self_Employed": "No",
            "ApplicantIncome": 5000,
            "CoapplicantIncome": 2500.0,
            "LoanAmount": 200.0,
            "Loan_Amount_Term": 360.0,
            "Credit_History": 1.0,
            "Property_Area": "Urban"
        },
        "request_id": "12345"
    }

    preprocessor = joblib.load(
        open("./models/preprocessor.pkl", "rb")
    )
    
    actual_features_str = preprocessor.transform(
        pd.DataFrame([input_record["input"]])
        ).to_json(orient="records")[1:-1]

    actual_features = json.loads(actual_features_str)
    
    expected_features = {
        "binary__Gender": 1.0,
        "binary__Married": 1.0,
        "binary__Education": 0.0,
        "binary__Self_Employed": 0.0,
        "binary__Credit_History": 1.0,
        "categorical__Property_Area_Rural": 0.0,
        "categorical__Property_Area_Semiurban": 0.0,
        "categorical__Property_Area_Urban": 1.0,
        "ordinal__Dependents": 2.0,
        "ordinal__Loan_Amount_Term": 8.0,
        "numerical__ApplicantIncome": -0.0660968212,
        "numerical__CoapplicantIncome": 0.3005454644,
        "numerical__LoanAmount": 0.6381859306
    }

    # We shall compare everything but the strictly numerical values
    # as their distribution may change (standardization) in the future and thus the 
    # exact values may not match.
    
    for key in expected_features:
        if key.startswith("numerical__"):
            continue
        assert key in actual_features, f"Key {key} not found in actual features"
        assert abs(actual_features[key] - expected_features[key]) < 1e-6, \
            f"Value mismatch for {key}: expected {expected_features[key]}, got {actual_features[key]}"

def test_base64_decode():
    data = "ewogICAgImlucHV0IiA6IHsKICAgICAgICAiR2VuZGVyIjogIk1hbGUiLAogICAgICAgICJNYXJyaWVkIjogIlllcy" +\
        "IsCiAgICAgICAgIkRlcGVuZGVudHMiOiAiMiIsCiAgICAgICAgIkVkdWNhdGlvbiI6ICJHcmFkdWF0ZSIsCiAgICAgICAg" +\
        "IlNlbGZfRW1wbG95ZWQiOiAiTm8iLAogICAgICAgICJBcHBsaWNhbnRJbmNvbWUiOiA1MDAwLAogICAgICAgICJDb2FwcG"+\
        "xpY2FudEluY29tZSI6IDI1MDAuMCwKICAgICAgICAiTG9hbkFtb3VudCI6IDIwMC4wLAogICAgICAgICJMb2FuX0Ftb3Vud"+\
        "F9UZXJtIjogMzYwLjAsCiAgICAgICAgIkNyZWRpdF9IaXN0b3J5IjogMS4wLAogICAgICAgICJQcm9wZXJ0eV9BcmVhIjo"+\
        "gIlVyYmFuIgogICAgfSwKICAgICJyZXF1ZXN0X2lkIjogIjEyMzQ1Igp9Cg=="
    
    actual_result = model_module.base64_decode(data)
    
    expected_result = {
        "input": {
            "Gender": "Male",
            "Married": "Yes",
            "Dependents": "2",
            "Education": "Graduate",
            "Self_Employed": "No",
            "ApplicantIncome": 5000,
            "CoapplicantIncome": 2500.0,
            "LoanAmount": 200.0,
            "Loan_Amount_Term": 360.0,
            "Credit_History": 1.0,
            "Property_Area": "Urban"
        },
        "request_id": "12345"
    }
    
    assert expected_result == actual_result, f"Expected {expected_result}, but got {actual_result}"

class ModelMock:
    def __init__(self, value):
        self.value = value
    
    def predict(self, X):
        n = len(X)
        return [self.value] * n

def test_predict():
    model_mock = ModelMock(10)
    preprocessor = joblib.load(
        open("./models/preprocessor.pkl", "rb")
    )
    model_service = model_module.ModelService(model=model_mock, preprocessor=preprocessor)

    features = {
        "binary__Gender": 1.0,
        "binary__Married": 1.0,
        "binary__Education": 0.0,
        "binary__Self_Employed": 0.0,
        "binary__Credit_History": 1.0,
        "categorical__Property_Area_Rural": 0.0,
        "categorical__Property_Area_Semiurban": 0.0,
        "categorical__Property_Area_Urban": 1.0,
        "ordinal__Dependents": 2.0,
        "ordinal__Loan_Amount_Term": 8.0,
        "numerical__ApplicantIncome": -0.0660968212,
        "numerical__CoapplicantIncome": 0.3005454644,
        "numerical__LoanAmount": 0.6381859306
    }
    features = pd.DataFrame([features])
    prediction = model_service.predict(features)[0]
    
    assert prediction == 10, f"Expected 10, but got {prediction}"
    
def test_lambda_handler():
    model_mock = ModelMock(10)
    model_version = "Test123"
    preprocessor = joblib.load(
        open("./models/preprocessor.pkl", "rb")
    )
    model_service = model_module.ModelService(model=model_mock,
                                              preprocessor=preprocessor,
                                              model_version=model_version)
    
    data = "ewogICAgImlucHV0IiA6IHsKICAgICAgICAiR2VuZGVyIjogIk1hbGUiLAogICAgICAgICJNYXJyaWVkIjogIlllcy" +\
        "IsCiAgICAgICAgIkRlcGVuZGVudHMiOiAiMiIsCiAgICAgICAgIkVkdWNhdGlvbiI6ICJHcmFkdWF0ZSIsCiAgICAgICAg" +\
        "IlNlbGZfRW1wbG95ZWQiOiAiTm8iLAogICAgICAgICJBcHBsaWNhbnRJbmNvbWUiOiA1MDAwLAogICAgICAgICJDb2FwcG"+\
        "xpY2FudEluY29tZSI6IDI1MDAuMCwKICAgICAgICAiTG9hbkFtb3VudCI6IDIwMC4wLAogICAgICAgICJMb2FuX0Ftb3Vud"+\
        "F9UZXJtIjogMzYwLjAsCiAgICAgICAgIkNyZWRpdF9IaXN0b3J5IjogMS4wLAogICAgICAgICJQcm9wZXJ0eV9BcmVhIjo"+\
        "gIlVyYmFuIgogICAgfSwKICAgICJyZXF1ZXN0X2lkIjogIjEyMzQ1Igp9Cg=="
    
    event = {
        "Records": [
            {
                "kinesis": {
                    "data": data
                }
            },
        ]
    }
    
    actual_predictions = model_service.lambda_handler(event)
    
    expected_predictions = {
        "predictions": [
            {
                "model": "loan_approval_prediction_model",
                "model_version": model_version,
                "prediction": {
                    "approved": True, 
                    "request_id": "12345"
                    },
            }
        ]
    }
    
    assert actual_predictions == expected_predictions, \
        f"Expected {expected_predictions}, but got {actual_predictions}"
    