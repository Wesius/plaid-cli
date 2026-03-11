"""List recent transactions."""

from __future__ import annotations

import sys
from datetime import date, timedelta

from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import (
    TransactionsGetRequestOptions,
)

from plaid_cli.client import get_access_token, get_client, output


def run(days: int = 30, count: int = 50) -> None:
    client = get_client()
    access_token = get_access_token()

    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    options = TransactionsGetRequestOptions()
    options.count = count
    options.offset = 0

    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=options,
    )

    try:
        response = client.transactions_get(request)
    except Exception as e:
        print(f"Error fetching transactions: {e}", file=sys.stderr)
        sys.exit(1)

    txns = response["transactions"]
    results = []

    print(
        f"  {'Date':12s}  {'Merchant':35s}  {'Category':20s}  {'Amount':>10s}"
    )
    print("  " + "-" * 85)

    for txn in txns:
        pfc = txn.get("personal_finance_category")
        if pfc and pfc.get("primary"):
            cat = pfc["primary"]
        elif txn.get("category") and len(txn["category"]) > 0:
            cat = txn["category"][0]
        else:
            cat = ""
        name = txn.get("merchant_name") or txn["name"]
        amt = txn["amount"]

        print(
            f"  {str(txn['date']):12s}  {name:35s}  {cat:20s}  "
            f"${amt:>10,.2f}"
        )
        results.append(
            {
                "date": str(txn["date"]),
                "name": name,
                "category": cat,
                "amount": amt,
                "account_id": txn["account_id"],
            }
        )

    print(f"\n  Showing {len(txns)} of {response['total_transactions']} transactions")
    output(results)
