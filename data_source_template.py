#!/usr/bin/env python3
from typing import List, Dict
import requests
import sys
import os


URL = "http://localhost:8000"


def set_header_from_env(headers: Dict[str, str], key: str):
    """
    Reads values from Yoda Executor's environment variables
    Args:
        headers: header
    """
    value = os.environ.get(key)
    if value is not None:
        headers[key] = value


def set_request_verification_headers(existing_headers: Dict[str, str]) -> Dict[str, str]:
    """
    Create request verification info as HTTP headers
    Args:
        existing_headers: existing headers
    Returns:
        request header
    """
    new_headers = existing_headers.copy()
    set_header_from_env(new_headers, "BAND_CHAIN_ID")
    set_header_from_env(new_headers, "BAND_VALIDATOR")
    set_header_from_env(new_headers, "BAND_REQUEST_ID")
    set_header_from_env(new_headers, "BAND_EXTERNAL_ID")
    set_header_from_env(new_headers, "BAND_DATA_SOURCE_ID")
    set_header_from_env(new_headers, "BAND_REPORTER")
    set_header_from_env(new_headers, "BAND_SIGNATURE")
    return new_headers


def get_prices(symbols: List[str]) -> str:
    """
    Call the Gateway's URL with symbols to get the prices of symbols
    Args:
        symbols: symbols that we want to get the prices
    Returns:
        prices field from Gateway's response
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
