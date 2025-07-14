import os

import model

PREDICTIONS_STREAM_NAME = os.getenv("PREDICTIONS_STREAM_NAME", "loan_predictions")
MODEL_ID = os.getenv("MODEL_ID", "m-37d3c61eabaa4dc68607887b2f440b4a")
TEST_RUN = os.getenv("TEST_RUN", "True") == "True"

model_service = model.init(
    prediction_stream_name=PREDICTIONS_STREAM_NAME, model_id=MODEL_ID, test_run=TEST_RUN
)

def lambda_handler(event, context):
    resultado = model_service.lambda_handler(event)
    print(resultado)
    return resultado