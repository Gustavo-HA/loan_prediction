export KINESIS_STREAM_INPUT="stg-events-stream_loan-prediction"
export KINESIS_STREAM_OUTPUT="stg-predictions-stream_loan-prediction"

SHARD_ID_WITH_QUOTES=$(aws kinesis put-record \
        --stream-name ${KINESIS_STREAM_INPUT}   \
        --partition-key 1  \
        --data '{
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
        }'  \
        --query 'ShardId'
    )

echo "SHARD_ID: ${SHARD_ID_WITH_QUOTES}"

SHARD_ID=$(echo $SHARD_ID_WITH_QUOTES | tr -d '"')

echo "Clean SHARD_ID: ${SHARD_ID}" # Verify it's clean

SHARD_ITERATOR=$(aws kinesis get-shard-iterator --shard-id ${SHARD_ID} --shard-iterator-type TRIM_HORIZON --stream-name ${KINESIS_STREAM_OUTPUT} --query 'ShardIterator')

aws kinesis get-records --shard-iterator $SHARD_ITERATOR