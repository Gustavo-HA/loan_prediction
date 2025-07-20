```bash
docker build -t loan-stream:v1 .

docker run -it --rm \                                                                                                        
    -p 8080:8080 \
    -v ~/.aws:/root/.aws:ro \
    -e PREDICTIONS_STREAM_NAME="loan_predictions" \
    -e MODEL_ID="m-37d3c61eabaa4dc68607887b2f440b4a" \
    -e TEST_RUN="True" \
    -e AWS_DEFAULT_REGION="us-east-2" \
    loan-stream:v1
```


```
{
    "Records": [
        {
            "kinesis": {
                "kinesisSchemaVersion": "1.0",
                "partitionKey": "1",
                "sequenceNumber": "49590338271490256608559692538361571095921575989136588898",
                "data": "ewogICAgImlucHV0IiA6IHsKICAgICAgICAiR2VuZGVyIjogIk1hbGUiLAogICAgICAgICJNYXJyaWVkIjogIlllcyIsCiAgICAgICAgIkRlcGVuZGVudHMiOiAiMiIsCiAgICAgICAgIkVkdWNhdGlvbiI6ICJHcmFkdWF0ZSIsCiAgICAgICAgIlNlbGZfRW1wbG95ZWQiOiAiTm8iLAogICAgICAgICJBcHBsaWNhbnRJbmNvbWUiOiA1MDAwLAogICAgICAgICJDb2FwcGxpY2FudEluY29tZSI6IDI1MDAuMCwKICAgICAgICAiTG9hbkFtb3VudCI6IDIwMC4wLAogICAgICAgICJMb2FuX0Ftb3VudF9UZXJtIjogMzYwLjAsCiAgICAgICAgIkNyZWRpdF9IaXN0b3J5IjogMS4wLAogICAgICAgICJQcm9wZXJ0eV9BcmVhIjogIlVyYmFuIgogICAgfSwKICAgICJyZXF1ZXN0X2lkIjogIjEyMzQ1Igp9Cg==",
                "approximateArrivalTimestamp": 1545084650.987
            },
            "eventSource": "aws:kinesis",
            "eventVersion": "1.0",
            "eventID": "shardId-000000000006:49590338271490256608559692538361571095921575989136588898",
            "eventName": "aws:kinesis:record",
            "invokeIdentityArn": "arn:aws:iam::111122223333:role/lambda-kinesis-role",
            "awsRegion": "us-east-2",
            "eventSourceARN": "arn:aws:kinesis:us-east-2:111122223333:stream/lambda-stream"
        }
    ]
}
```

Test event
```
{
    "input" : {
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

ewogICAgImlucHV0IiA6IHsKICAgICAgICAiR2VuZGVyIjogIk1hbGUiLAogICAgICAgICJNYXJyaWVkIjogIlllcyIsCiAgICAgICAgIkRlcGVuZGVudHMiOiAiMiIsCiAgICAgICAgIkVkdWNhdGlvbiI6ICJHcmFkdWF0ZSIsCiAgICAgICAgIlNlbGZfRW1wbG95ZWQiOiAiTm8iLAogICAgICAgICJBcHBsaWNhbnRJbmNvbWUiOiA1MDAwLAogICAgICAgICJDb2FwcGxpY2FudEluY29tZSI6IDI1MDAuMCwKICAgICAgICAiTG9hbkFtb3VudCI6IDIwMC4wLAogICAgICAgICJMb2FuX0Ftb3VudF9UZXJtIjogMzYwLjAsCiAgICAgICAgIkNyZWRpdF9IaXN0b3J5IjogMS4wLAogICAgICAgICJQcm9wZXJ0eV9BcmVhIjogIlVyYmFuIgogICAgfSwKICAgICJyZXF1ZXN0X2lkIjogIjEyMzQ1Igp9Cg==
```