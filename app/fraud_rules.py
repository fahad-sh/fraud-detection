"""
fraud_rules.py
Contains the logic for flagging a transaction as fraudulent.
Each rule returns True if it is triggered, plus a human-readable reason.
"""

from datetime import datetime

# Tune these as needed
HIGH_AMOUNT_THRESHOLD = 10000  # £10k
SUSPICIOUS_COUNTRIES = {"North Korea", "Iran", "Syria"}  # example list
ODD_HOUR_START = 1
ODD_HOUR_END = 4
REQUIRED_FIELDS = ["transaction_id", "amount", "country", "timestamp", "customer_id"]


def check_missing_fields(transaction: dict) -> list:
    """Returns a list of missing required fields."""
    return [field for field in REQUIRED_FIELDS if field not in transaction or transaction[field] in (None, "")]


def check_high_amount(transaction: dict) -> bool:
    try:
        return float(transaction.get("amount", 0)) > HIGH_AMOUNT_THRESHOLD
    except (ValueError, TypeError):
        return False


def check_suspicious_country(transaction: dict) -> bool:
    return transaction.get("country") in SUSPICIOUS_COUNTRIES


def check_odd_hours(transaction: dict) -> bool:
    """Checks if the transaction timestamp falls between 1am and 4am."""
    timestamp_str = transaction.get("timestamp")
    if not timestamp_str:
        return False
    try:
        ts = datetime.fromisoformat(timestamp_str)
        return ODD_HOUR_START <= ts.hour < ODD_HOUR_END
    except ValueError:
        return False


def evaluate_transaction(transaction: dict) -> dict:
    """
    Runs all fraud rules against a single transaction.
    Returns a result dict with a fraud flag and the reasons why.
    """
    reasons = []

    missing = check_missing_fields(transaction)
    if missing:
        reasons.append("Missing fields: " + ", ".join(missing))

    if "amount" not in missing and check_high_amount(transaction):
        reasons.append("High amount (> £" + str(HIGH_AMOUNT_THRESHOLD) + ")")

    if "country" not in missing and check_suspicious_country(transaction):
        reasons.append("Suspicious country: " + str(transaction.get("country")))

    if "timestamp" not in missing and check_odd_hours(transaction):
        reasons.append("Transaction occurred during odd hours (1am-4am)")

    is_fraud = len(reasons) > 0

    return {
        "transaction_id": transaction.get("transaction_id", "UNKNOWN"),
        "is_fraud": is_fraud,
        "reasons": reasons,
    }
