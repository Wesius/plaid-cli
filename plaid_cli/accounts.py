"""List linked accounts."""

from __future__ import annotations

from plaid.model.accounts_get_request import AccountsGetRequest

from plaid_cli.client import get_access_token, get_client, output


def run() -> None:
    client = get_client()
    access_token = get_access_token()

    request = AccountsGetRequest(access_token=access_token)
    response = client.accounts_get(request)

    accounts = []
    for acct in response["accounts"]:
        bal = acct["balances"]
        accounts.append(
            {
                "id": acct["account_id"],
                "name": acct["name"],
                "type": str(acct["type"]),
                "subtype": str(acct["subtype"]),
                "current": bal["current"],
                "available": bal["available"],
                "mask": acct.get("mask", ""),
            }
        )
        print(
            f"  {acct['name']:30s}  {str(acct['type']):12s}  "
            f"{str(acct['subtype']):12s}  "
            f"${bal['current'] or 0:>10,.2f}  (****{acct.get('mask', '')})"
        )

    output(accounts)
