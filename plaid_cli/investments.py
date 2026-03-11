"""Show investment holdings."""

from __future__ import annotations

import sys

from plaid.model.investments_holdings_get_request import (
    InvestmentsHoldingsGetRequest,
)

from plaid_cli.client import get_access_token, get_client, output


def run() -> None:
    client = get_client()
    access_token = get_access_token()

    request = InvestmentsHoldingsGetRequest(access_token=access_token)

    try:
        response = client.investments_holdings_get(request)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    secs = {s["security_id"]: s for s in response["securities"]}
    accts = {a["account_id"]: a["name"] for a in response["accounts"]}

    total_value = 0.0
    total_cost = 0.0
    results = []

    print(
        f"  {'Security':30s}  {'Ticker':8s}  {'Qty':>10s}  "
        f"{'Price':>10s}  {'Value':>12s}  {'Cost':>12s}  {'G/L':>10s}"
    )
    print("  " + "-" * 98)

    for h in response["holdings"]:
        sec = secs.get(h["security_id"], {})
        name = sec.get("name") or "Unknown"
        ticker = sec.get("ticker_symbol") or ""
        qty = h["quantity"]
        price = h["institution_price"]
        value = h["institution_value"]
        cost = h.get("cost_basis")
        gain = (value - cost) if cost is not None else None

        total_value += value
        if cost is not None:
            total_cost += cost

        gain_str = f"${gain:>9,.2f}" if gain is not None else "       N/A"

        print(
            f"  {name:30s}  {ticker:8s}  {qty:>10g}  "
            f"${price:>9,.2f}  ${value:>11,.2f}  "
            f"{'$' + f'{cost:>11,.2f}' if cost is not None else '        N/A'}  "
            f"{gain_str}"
        )

        results.append(
            {
                "name": name,
                "ticker": ticker,
                "type": str(sec.get("type", "")),
                "quantity": qty,
                "price": price,
                "value": value,
                "cost_basis": cost,
                "gain_loss": gain,
                "account": accts.get(h["account_id"], ""),
            }
        )

    print("  " + "-" * 98)
    total_gain = total_value - total_cost
    print(
        f"  {'TOTAL':30s}  {'':8s}  {'':>10s}  "
        f"{'':>10s}  ${total_value:>11,.2f}  "
        f"${total_cost:>11,.2f}  ${total_gain:>9,.2f}"
    )

    output(results)
