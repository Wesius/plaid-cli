"""Spending summary by category."""

from __future__ import annotations

import sys
from collections import defaultdict
from datetime import date, timedelta

from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import (
    TransactionsGetRequestOptions,
)

from plaid_cli.client import get_access_token, get_client, output


def run(days: int = 30) -> None:
    client = get_client()
    access_token = get_access_token()

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    all_txns: list = []
    offset = 0
    total = 1

    while offset < total:
        options = TransactionsGetRequestOptions()
        options.count = 500
        options.offset = offset

        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=options,
        )

        try:
            response = client.transactions_get(request)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        all_txns.extend(response["transactions"])
        total = response["total_transactions"]
        offset = len(all_txns)

    by_category: dict[str, float] = defaultdict(float)
    total_spent = 0.0

    for txn in all_txns:
        amt = txn["amount"]
        if amt <= 0:
            continue
        cat = (
            txn["category"][0]
            if txn.get("category") and len(txn["category"]) > 0
            else "Other"
        )
        by_category[cat] += amt
        total_spent += amt

    sorted_cats = sorted(by_category.items(), key=lambda x: x[1], reverse=True)

    print(f"  Spending summary ({days} days)\n")
    print(f"  {'Category':25s}  {'Amount':>10s}  {'%':>6s}")
    print("  " + "-" * 45)

    results = []
    for cat, amt in sorted_cats:
        pct = (amt / total_spent * 100) if total_spent > 0 else 0
        print(f"  {cat:25s}  ${amt:>10,.2f}  {pct:5.1f}%")
        results.append({"category": cat, "amount": amt, "percent": round(pct, 1)})

    print("  " + "-" * 45)
    print(f"  {'TOTAL':25s}  ${total_spent:>10,.2f}")
    print(f"\n  {len(all_txns)} transactions across {len(by_category)} categories")

    output(results)
