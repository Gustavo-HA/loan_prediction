import base64
import json
import os
from pickle import load

import boto3
import mlflow
import pandas as pd


def get_model_location(run_id):
    model_location = os.getenv("MODEL_LOCATION")
    
    if model_location is not None:
        return model_location
    
    model_bucket = os.getenv("MODEL_BUCKET", "stg-mlflow-models")
    experiment_id = os.getenv("EXPERIMENT_ID", "1")
    
    model_location = f"s3://{model_bucket}/1/{experiment_id}/artifacts/model"
    return model_location

def load_model(run_id):
    model_location = get_model_location()
    model = mlflow.pyfunc.load_model(model_location)
    return model

def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    input_record = json.loads(decoded_data)
    return input_record

class ModelService:
    def __init__(self, model, model_version=None, callbacks=None):
        self.model = model
        self.model_version = model_version
        self.callbacks = callbacks or []
    
    def prepare_features(self, input_record):
        # Implement feature preparation logic here
        preprocessor = load(open('preprocessor.pkl', 'rb'))
        features: pd.DataFrame = pd.DataFrame([input_record])
        features = preprocessor.transform(features)
        return features
    
    def predict(self, features):
        prediction = self.model.predict(features)
        return prediction
    
    def lambda_handler(self, event):
        predictions_events = []
        
        for record in event['Records']:
            encoded_data = record['kinesis']['data']
            input_record = base64_decode(encoded_data)
            
            request = input_record["input"]
            request_id = request.get("request_id", "unknown")
            
            features = self.prepare_features(request)
            prediction = self.predict(features)
            
            prediction_event = {
                'model': 'loan_approval_prediction_model',
                'model_version': self.model_version,
                'prediction': {'approved': bool(prediction[0]),
                               'request_id': request_id},
            }
            
            for callback in self.callbacks:
                callback(prediction_event)
            
            predictions_events.append(prediction_event)
            
        return {'predictions': predictions_events}
    
class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name
        
    def put_record(self, prediction_event):
        request_id = prediction_event['prediction']['request_id']
        
        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(request_id)
        )
        
def create_kinesis_client():
    endpoint_url = os.getenv("KINESIS_ENDPOINT_URL")
    
    if endpoint_url is None:
        return boto3.client('kinesis')
    
    return boto3.client('kinesis', endpoint_url=endpoint_url)

def init(prediction_stream_name: str,
         run_id: str,
         test_run: bool):
    model = load_model(run_id)
    
    callbacks = []
    
    if not test_run:
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)
        
    model_service = ModelService(model=model,
                                 model_version=run_id,
                                 callbacks=callbacks)
    
    return model_service