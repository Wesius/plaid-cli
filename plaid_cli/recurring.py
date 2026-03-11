"""Show recurring transactions (subscriptions, bills)."""

from __future__ import annotations

import sys

from plaid.model.transactions_recurring_get_request import (
    TransactionsRecurringGetRequest,
)

from plaid_cli.client import get_access_token, get_client, output


def run() -> None:
    client = get_client()
    access_token = get_access_token()

    request = TransactionsRecurringGetRequest(access_token=access_token)

    try:
        response = client.transactions_recurring_get(request)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    results = []

    outflows = response.get("outflow_streams") or []
    inflows = response.get("inflow_streams") or []

    if outflows:
        total_monthly = 0.0
        print("  RECURRING EXPENSES")
        print(
            f"  {'Name':30s}  {'Frequency':12s}  {'Avg Amount':>12s}  "
            f"{'Category':20s}  {'Next':>12s}"
        )
        print("  " + "-" * 92)

        for s in outflows:
            name = s.get("merchant_name") or s.get("description", "Unknown")
            freq = str(s.get("frequency", ""))
            avg = s["average_amount"]["amount"]
            pfc = s.get("personal_finance_category")
            cat = pfc["primary"] if pfc and pfc.get("primary") else ""
            nxt = s.get("predicted_next_date")
            status = str(s.get("status", ""))

            print(
                f"  {name:30s}  {freq:12s}  ${avg:>11,.2f}  "
                f"{cat:20s}  {str(nxt) if nxt else '':>12s}"
            )

            if freq == "MONTHLY":
                total_monthly += avg
            elif freq == "WEEKLY":
                total_monthly += avg * 4.33
            elif freq == "BIWEEKLY":
                total_monthly += avg * 2.17

            results.append(
                {
                    "direction": "outflow",
                    "name": name,
                    "frequency": freq,
                    "average_amount": avg,
                    "category": cat,
                    "status": status,
                    "next_date": str(nxt) if nxt else None,
                    "active": s.get("is_active", True),
                }
            )

        print("  " + "-" * 92)
        print(f"  Est. monthly recurring:  ${total_monthly:>11,.2f}")
        print()

    if inflows:
        print("  RECURRING INCOME")
        print(
            f"  {'Name':30s}  {'Frequency':12s}  {'Avg Amount':>12s}  "
            f"{'Category':20s}  {'Next':>12s}"
        )
        print("  " + "-" * 92)

        for s in inflows:
            name = s.get("merchant_name") or s.get("description", "Unknown")
            freq = str(s.get("frequency", ""))
            avg = s["average_amount"]["amount"]
            pfc = s.get("personal_finance_category")
            cat = pfc["primary"] if pfc and pfc.get("primary") else ""
            nxt = s.get("predicted_next_date")
            status = str(s.get("status", ""))

            print(
                f"  {name:30s}  {freq:12s}  ${avg:>11,.2f}  "
                f"{cat:20s}  {str(nxt) if nxt else '':>12s}"
            )

            results.append(
                {
                    "direction": "inflow",
                    "name": name,
                    "frequency": freq,
                    "average_amount": avg,
                    "category": cat,
                    "status": status,
                    "next_date": str(nxt) if nxt else None,
                    "active": s.get("is_active", True),
                }
            )

        print()

    if not results:
        print("  No recurring transactions found.")

    output(results)
