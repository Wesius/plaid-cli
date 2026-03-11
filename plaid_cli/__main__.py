"""Plaid CLI entry point. Run with: python -m plaid_cli <command>"""

from __future__ import annotations

import sys

import plaid


def main() -> None:
    try:
        _dispatch()
    except KeyboardInterrupt:
        sys.exit(130)
    except plaid.ApiException as exc:
        import json

        err = json.loads(exc.body or "{}")
        print(
            f"Plaid error: {err.get('error_code', 'unknown')} - "
            f"{err.get('error_message', '')}",
            file=sys.stderr,
        )
        sys.exit(1)


def _dispatch() -> None:
    import plaid_cli.client as _client

    if "--json" in sys.argv:
        _client.JSON_OUTPUT = True
        sys.argv.remove("--json")

    commands = {
        "link": "Link a sandbox bank account",
        "accounts": "List linked accounts",
        "balances": "Show real-time account balances",
        "transactions": "List recent transactions [--days N] [--count N]",
        "spending": "Spending summary by category [--days N]",
        "identity": "Show identity info for linked accounts",
    }

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: plaid <command> [args]\n")
        print("Commands:")
        for cmd, desc in commands.items():
            print(f"  {cmd:16s} {desc}")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "link":
        _client.link_sandbox()
    elif cmd == "accounts":
        from plaid_cli.accounts import run

        run()
    elif cmd == "balances":
        from plaid_cli.balances import run

        run()
    elif cmd == "transactions":
        days = 30
        count = 50
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--days" and i + 1 < len(args):
                days = int(args[i + 1])
                i += 2
            elif args[i] == "--count" and i + 1 < len(args):
                count = int(args[i + 1])
                i += 2
            else:
                i += 1
        from plaid_cli.transactions import run

        run(days=days, count=count)
    elif cmd == "spending":
        days = 30
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--days" and i + 1 < len(args):
                days = int(args[i + 1])
                i += 2
            else:
                i += 1
        from plaid_cli.spending import run

        run(days=days)
    elif cmd == "identity":
        from plaid_cli.identity import run

        run()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
