"""Show identity info for linked accounts."""

from __future__ import annotations

import sys

from plaid.model.identity_get_request import IdentityGetRequest

from plaid_cli.client import get_access_token, get_client, output


def run() -> None:
    client = get_client()
    access_token = get_access_token()

    request = IdentityGetRequest(access_token=access_token)

    try:
        response = client.identity_get(request)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    results = []
    for acct in response["accounts"]:
        owners = acct.get("owners", [])
        for owner in owners:
            names = owner.get("names", [])
            emails = [e["data"] for e in owner.get("emails", [])]
            phones = [p["data"] for p in owner.get("phone_numbers", [])]
            addrs = []
            for a in owner.get("addresses", []):
                d = a.get("data", {})
                parts = [
                    d.get("street"),
                    d.get("city"),
                    d.get("region"),
                    d.get("postal_code"),
                ]
                addrs.append(", ".join(p for p in parts if p))

            print(f"  Account: {acct['name']}")
            if names:
                print(f"    Name:    {', '.join(names)}")
            if emails:
                print(f"    Email:   {', '.join(emails)}")
            if phones:
                print(f"    Phone:   {', '.join(phones)}")
            for addr in addrs:
                print(f"    Address: {addr}")
            print()

            results.append(
                {
                    "account": acct["name"],
                    "names": names,
                    "emails": emails,
                    "phones": phones,
                    "addresses": addrs,
                }
            )

    output(results)
