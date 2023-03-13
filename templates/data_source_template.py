#!/usr/bin/env python3
import os
import sys
from typing import List, Dict

import requests

URL = "http://localhost:8000"


def set_header_from_env(headers: Dict[str, str], key: str) -> None:
    """Reads values from Yoda Executor's environment variables

    Args:
        key: Key to set from env.
        headers: Header.
    """
    value = os.environ.get(key)
    if value is not None:
        headers[key] = value


def set_request_verification_headers(existing_headers: Dict[str, str]) -> Dict[str, str]:
    """Sets a request verification info as HTTP headers.

    Args:
        existing_headers: Existing headers.

    Returns:
        Request header.
    """
    new_headers = existing_headers.copy()

    band_keys = [
        "BAND_CHAIN_ID",
        "BAND_VALIDATOR",
        "BAND_REQUEST_ID",
        "BAND_EXTERNAL_ID",
        "BAND_DATA_SOURCE_ID",
        "BAND_REPORTER",
        "BAND_SIGNATURE",
    ]
    for band_key in band_keys:
        set_header_from_env(new_headers, band_key)

    return new_headers


def get_prices(symbols: List[str]) -> str:
    """Calls the Gateway's URL along with the requested symbols to retrieve its prices.

    Args:
        symbols: Symbols to get the price of.

    Returns:
        Prices field from the gateway's response.
    """
    headers = set_request_verification_headers({})
    r = requests.get(f"{URL}", headers=headers, params={"symbols": ",".join(symbols)})
    r.raise_for_status()
    response = r.json()
    prices = {price["symbol"]: price["price"] for price in response["prices"]}

    if len(symbols) != len(prices):
        raise Exception("INPUT_AND_OUTPUT_LENGTH_ARE_NOT_MATCH")

    return ",".join([prices[symbol] for symbol in symbols])


def main(symbols: List[str]) -> str:
    return get_prices(symbols)


# python data_source_template.py BAND ALPHA
if __name__ == "__main__":
    try:
        print(main(sys.argv[1:]))
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
