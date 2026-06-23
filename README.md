# Fraud Detection Pipeline

A CI/CD-automated fraud detection system on AWS. Reads transactions from S3, flags fraud using a rules engine, logs results to DynamoDB, and sends email alerts via SNS — fully containerized and deployed through Jenkins.

## Architecture

Developer → GitHub → Jenkins (EC2)

│

Checkout → Test → Build → Push to ECR → Deploy → Cleanup

│

▼

ECR ──pull──▶ Docker Container (EC2)

│

S3 ──read──▶ Load Transactions

│

Fraud Rules Engine

(Amount / Country /

Hours / Missing Fields)

│

Fraud? ──Yes──▶ SNS Alert Email

│

▼

DynamoDB (fraud_results)

## Fraud Rules

| Rule | Condition |
|---|---|
| High Amount | > £10,000 |
| Suspicious Country | On watchlist |
| Odd Hours | 1:00–4:00 AM |
| Missing Fields | Required field absent |

## Stack

AWS (EC2, S3, DynamoDB, SNS, ECR, IAM) · Jenkins · Docker · Python (boto3) · GitHub

## Run Locally

```bash
export S3_BUCKET=your-bucket
export DYNAMODB_TABLE=fraud_results
export SNS_TOPIC_ARN=arn:aws:sns:region:account-id:topic
export AWS_REGION=us-east-1

cd app && pip install -r requirements.txt && python3 main.py
```

## Run with Docker

```bash
docker build -t fraud-detection-app .
docker run --rm -e S3_BUCKET -e DYNAMODB_TABLE -e SNS_TOPIC_ARN -e AWS_REGION fraud-detection-app
```

## CI/CD

`Jenkinsfile` runs: **Checkout → Test → Build → Push to ECR → Deploy → Cleanup**, producing a versioned image tag on every run plus a `latest` tag.

## Security

- No hardcoded AWS keys — EC2 IAM role handles all AWS access
- GitHub auth via Personal Access Token, stored in Jenkins credentials store
- `.gitignore` excludes SSH keys and local artifacts

## Notable Fixes

- Diagnosed Jenkins install failure to an expired GPG signing key
- Resolved Jenkins/Java version mismatch (needed Java 21+)
- Fixed Jenkins node going offline due to undersized `/tmp` tripping disk monitor
- Caught a stale Docker build cache silently skipping dependency installs

## Roadmap

- Least-privilege IAM policies
- GitHub webhook for auto-trigger on push
- Real test suite (pytest)
