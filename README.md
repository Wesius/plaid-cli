# plaid-cli

CLI for Plaid financial data. Supports sandbox and production environments.

## Setup

```bash
# Install dependencies
uv sync

# Set credentials in .env (or parent project .env)
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox  # or production

# Link a sandbox account
uv run python -m plaid_cli link
```

## Commands

```
plaid link              Link a sandbox bank account
plaid accounts          List linked accounts
plaid balances          Show real-time account balances
plaid transactions      List recent transactions [--days N] [--count N]
plaid spending          Spending summary by category [--days N]
plaid identity          Show identity info for linked accounts
```

Add `--json` to any command for JSON output.
