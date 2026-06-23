"""
main.py
Entry point for the Fraud Detection app.

Flow (matches the architecture diagram):
1. Load transactions from S3
2. Run each transaction through the fraud rules engine
3. Write every result to DynamoDB
4. If fraud is detected, publish an alert to SNS
"""

import json
import os
import boto3
from fraud_rules import evaluate_transaction

# ---- Configuration (pulled from environment variables, set later) ----
S3_BUCKET = os.environ.get("S3_BUCKET", "your-bucket-name")
S3_KEY = os.environ.get("S3_KEY", "transactions.json")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "fraud_results")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# ---- AWS clients ----
s3 = boto3.client("s3", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

table = dynamodb.Table(DYNAMODB_TABLE)


def load_transactions_from_s3(bucket: str, key: str) -> list:
    """Downloads and parses the transactions JSON file from S3."""
    print(f"Loading transactions from s3://{bucket}/{key} ...")
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    transactions = json.loads(content)
    print(f"Loaded {len(transactions)} transactions.")
    return transactions


def save_result_to_dynamodb(result: dict):
    """Writes a single evaluation result to DynamoDB."""
    item = {
        "transaction_id": result["transaction_id"],
        "is_fraud": result["is_fraud"],
        "reasons": result["reasons"],
    }
    table.put_item(Item=item)


def send_fraud_alert(result: dict):
    """Publishes an SNS alert for a flagged transaction."""
    if not SNS_TOPIC_ARN:
        print("SNS_TOPIC_ARN not set, skipping alert.")
        return

    message = (
        f"FRAUD ALERT\n"
        f"Transaction ID: {result['transaction_id']}\n"
        f"Reasons: {', '.join(result['reasons'])}"
    )
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"Fraud Alert: {result['transaction_id']}",
        Message=message,
    )
    print(f"Sent SNS alert for transaction {result['transaction_id']}")


def run():
    transactions = load_transactions_from_s3(S3_BUCKET, S3_KEY)

    fraud_count = 0
    for transaction in transactions:
        result = evaluate_transaction(transaction)
        save_result_to_dynamodb(result)

        if result["is_fraud"]:
            fraud_count += 1
            send_fraud_alert(result)
            print(f"FLAGGED: {result['transaction_id']} -> {result['reasons']}")
        else:
            print(f"OK: {result['transaction_id']}")

    print(f"\nDone. {fraud_count} of {len(transactions)} transactions flagged as fraud.")


if __name__ == "__main__":
    run()
