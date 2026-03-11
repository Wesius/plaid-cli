"""Show real-time account balances."""

from __future__ import annotations

from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest

from plaid_cli.client import get_access_token, get_client, output


def run() -> None:
    client = get_client()
    access_token = get_access_token()

    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)

    total = 0.0
    results = []
    for acct in response["accounts"]:
        bal = acct["balances"]
        current = bal["current"] or 0
        available = bal["available"]
        limit = bal.get("limit")

        if str(acct["type"]) == "credit":
            total -= current
        else:
            total += current

        line = f"  {acct['name']:30s}  ${current:>10,.2f}"
        if available is not None:
            line += f"  (avail: ${available:,.2f})"
        if limit is not None:
            line += f"  (limit: ${limit:,.2f})"
        print(line)

        results.append(
            {
                "name": acct["name"],
                "type": str(acct["type"]),
                "current": current,
                "available": available,
                "limit": limit,
            }
        )

    print(f"\n  {'Net Worth':30s}  ${total:>10,.2f}")
    output(results)
