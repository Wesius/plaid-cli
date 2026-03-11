"""Show liabilities (credit, mortgage, student loans)."""

from __future__ import annotations

import sys

from plaid.model.liabilities_get_request import LiabilitiesGetRequest

from plaid_cli.client import get_access_token, get_client, output


def run() -> None:
    client = get_client()
    access_token = get_access_token()

    request = LiabilitiesGetRequest(access_token=access_token)

    try:
        response = client.liabilities_get(request)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    accts = {a["account_id"]: a for a in response["accounts"]}
    liabs = response["liabilities"]
    results = []

    credit = liabs.get("credit") or []
    if credit:
        print("  CREDIT CARDS")
        print("  " + "-" * 75)
        for c in credit:
            acct = accts.get(c["account_id"], {})
            name = acct.get("name", "Unknown")
            bal = acct.get("balances", {}).get("current", 0)
            apr = c["aprs"][0]["apr_percentage"] if c.get("aprs") else None
            min_pay = c.get("minimum_payment_amount")
            due = c.get("next_payment_due_date")
            overdue = c.get("is_overdue", False)

            print(f"  {name}")
            print(f"    Balance:     ${bal or 0:>10,.2f}")
            if apr is not None:
                print(f"    APR:         {apr}%")
            if min_pay is not None:
                print(f"    Min payment: ${min_pay:>10,.2f}")
            if due:
                print(f"    Due:         {due}")
            if overdue:
                print("    *** OVERDUE ***")
            print()

            results.append(
                {
                    "type": "credit",
                    "name": name,
                    "balance": bal,
                    "apr": apr,
                    "minimum_payment": min_pay,
                    "next_due": str(due) if due else None,
                    "is_overdue": overdue,
                }
            )

    mortgage = liabs.get("mortgage") or []
    if mortgage:
        print("  MORTGAGES")
        print("  " + "-" * 75)
        for m in mortgage:
            acct = accts.get(m["account_id"], {})
            name = acct.get("name", "Unknown")
            bal = acct.get("balances", {}).get("current", 0)
            rate = m.get("interest_rate", {})
            pct = rate.get("percentage") if rate else None
            loan_type = m.get("loan_type_description", "")
            term = m.get("loan_term", "")
            origination = m.get("origination_date")
            orig_amt = m.get("origination_principal_amount")
            monthly = m.get("next_monthly_payment")
            due = m.get("next_payment_due_date")
            ytd_int = m.get("ytd_interest_paid")
            ytd_prin = m.get("ytd_principal_paid")

            print(f"  {name} ({loan_type} {term})")
            print(f"    Balance:     ${bal or 0:>12,.2f}")
            if orig_amt:
                print(f"    Original:    ${orig_amt:>12,.2f}")
            if pct is not None:
                print(f"    Rate:        {pct}%")
            if monthly:
                print(f"    Monthly:     ${monthly:>12,.2f}")
            if due:
                print(f"    Next due:    {due}")
            if origination:
                print(f"    Originated:  {origination}")
            if ytd_int:
                print(f"    YTD interest:${ytd_int:>12,.2f}")
            if ytd_prin:
                print(f"    YTD principal:${ytd_prin:>11,.2f}")
            print()

            results.append(
                {
                    "type": "mortgage",
                    "name": name,
                    "balance": bal,
                    "rate": pct,
                    "loan_type": loan_type,
                    "term": term,
                    "monthly_payment": monthly,
                    "next_due": str(due) if due else None,
                    "origination_amount": orig_amt,
                }
            )

    student = liabs.get("student") or []
    if student:
        print("  STUDENT LOANS")
        print("  " + "-" * 75)
        for s in student:
            acct = accts.get(s["account_id"], {})
            name = acct.get("name", "Unknown")
            bal = acct.get("balances", {}).get("current", 0)
            rate = s.get("interest_rate_percentage")
            loan_name = s.get("loan_name", "")
            min_pay = s.get("minimum_payment_amount")
            due = s.get("next_payment_due_date")
            orig_amt = s.get("origination_principal_amount")
            payoff = s.get("expected_payoff_date")
            status = s.get("loan_status", {})
            status_type = status.get("type", "") if status else ""
            overdue = s.get("is_overdue", False)
            outstanding_int = s.get("outstanding_interest_amount")

            label = loan_name or name
            print(f"  {label}")
            print(f"    Balance:     ${bal or 0:>12,.2f}")
            if outstanding_int:
                print(f"    Accrued int: ${outstanding_int:>12,.2f}")
            if orig_amt:
                print(f"    Original:    ${orig_amt:>12,.2f}")
            if rate is not None:
                print(f"    Rate:        {rate}%")
            if min_pay is not None:
                print(f"    Min payment: ${min_pay:>12,.2f}")
            if due:
                print(f"    Next due:    {due}")
            if payoff:
                print(f"    Payoff date: {payoff}")
            if status_type:
                print(f"    Status:      {status_type}")
            if overdue:
                print("    *** OVERDUE ***")
            print()

            results.append(
                {
                    "type": "student",
                    "name": label,
                    "balance": bal,
                    "rate": rate,
                    "minimum_payment": min_pay,
                    "next_due": str(due) if due else None,
                    "origination_amount": orig_amt,
                    "status": status_type,
                    "is_overdue": overdue,
                }
            )

    if not results:
        print("  No liabilities found.")

    output(results)
