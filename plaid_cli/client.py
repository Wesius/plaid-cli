"""Shared Plaid API client for the finance CLI."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import plaid
from dotenv import load_dotenv
from plaid.api import plaid_api
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.products import Products
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)

PROJECT_DIR = Path("/Users/wesgr/Projects/personal/assistant")
load_dotenv(PROJECT_DIR / ".env")

CACHE_PATH = Path.home() / ".cache" / "plaid-access-token.json"

SANDBOX_INSTITUTION = "ins_109508"

JSON_OUTPUT: bool = False


def output(data: list | dict) -> None:
    if JSON_OUTPUT:
        print(json.dumps(data, indent=2, default=str))


def _get_client() -> plaid_api.PlaidApi:
    client_id = os.environ.get("PLAID_CLIENT_ID", "")
    secret = os.environ.get("PLAID_SECRET", "")
    env = os.environ.get("PLAID_ENV", "sandbox")

    if not client_id or not secret:
        print(
            "Set PLAID_CLIENT_ID and PLAID_SECRET in .env",
            file=sys.stderr,
        )
        sys.exit(1)

    host = {
        "sandbox": plaid.Environment.Sandbox,
        "production": plaid.Environment.Production,
    }.get(env, plaid.Environment.Sandbox)

    configuration = plaid.Configuration(
        host=host,
        api_key={"clientId": client_id, "secret": secret},
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def get_client() -> plaid_api.PlaidApi:
    return _get_client()


def get_access_token() -> str:
    if CACHE_PATH.exists():
        data = json.loads(CACHE_PATH.read_text())
        return data["access_token"]

    print("No access token cached. Run 'plaid link' first.", file=sys.stderr)
    sys.exit(1)


def link_sandbox() -> str:
    """Create a sandbox item and cache the access token."""
    client = _get_client()

    pt_request = SandboxPublicTokenCreateRequest(
        institution_id=SANDBOX_INSTITUTION,
        initial_products=[
            Products("auth"),
            Products("transactions"),
        ],
    )

    try:
        pt_response = client.sandbox_public_token_create(pt_request)
        public_token = pt_response["public_token"]
    except plaid.ApiException as e:
        error = json.loads(e.body or "{}")
        print(f"Error creating sandbox token: {error['error_code']}", file=sys.stderr)
        sys.exit(1)

    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token: str = exchange_response["access_token"]

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(
            {
                "access_token": access_token,
                "item_id": exchange_response["item_id"],
                "institution_id": SANDBOX_INSTITUTION,
                "environment": "sandbox",
            }
        )
    )

    print(f"Linked sandbox account (item: {exchange_response['item_id']})")
    return access_token
