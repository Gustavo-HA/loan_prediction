import json

from deepdiff import DeepDiff
import requests

with open('event.json', 'rt') as f:
    event = json.load(f)

url = "http://localhost:8080/2015-03-31/functions/function/invocations"

actual_response = requests.post(url=url, json=event).json()

print("actual_response:")
print(json.dumps(actual_response, indent=2))

expected_response = {
    "predictions": [
        {
            "model": "loan_approval_prediction_model",
            "model_version": "Test123",
            "prediction": {"approved": True, "request_id": "12345"},
        }
    ]
}


diff = DeepDiff(actual_response, expected_response, significant_digits=1)
print(f"{diff=}")

assert "type_changes" not in diff
assert "values_changed" not in diff