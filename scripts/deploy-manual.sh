
# Model artifacts bucket
export MODEL_BUCKET

# Get latest MODEL_ID from latest S3 partition.
# NOT FOR PRODUCTION!
# In practice, this is generally picked up from you experiment tracking tool
# such as MLflow or a DB.
export MODEL_ID=$(aws s3api list-objects-v2 --bucket "gus-mlflow-artifacts" \
    --query "sort_by(Contents, &LastModified)[-1].Key" --output=text | cut -f3 -d/)