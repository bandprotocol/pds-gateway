# Requirement

## Environment variables

- You can use .env file by running "cp .env.example .env" and update the environment variables of Gateway and your adapter.

# Run application

## Run by Docker Compose

- run "docker-compose up"

## Run by Sanic directly

- sanic main:app

# Testing

- run "pytest"

# Supported adapters

## StandardCryptoPrice

- This standard of adapter type is used for getting current price of each crypto symbols. Here are the spec of request, response, adapter input and adapter output.
  - Request:
    - symbols: str (e.g. "BAND,ALPHA")
  - Response:
    - prices: []{symbol: str, price: float, timestamp: integer} (e.g. [{symbol: “BAND”, price: 99999, timestamp: 161111111111}, {symbol: “ALPHA”, price: 99999, timestamp: 161111111111}])
  - Adapter input:
    - symbols: List[str] (e.g. ["BAND", "ALPHA"])
  - Adapter output:
    - prices: []{symbol: str, price: float, timestamp: integer} (e.g. [{symbol: “BAND”, price: 99999, timestamp: 161111111111}, {symbol: “ALPHA”, price: 99999, timestamp: 161111111111}]

### CoinMarketCap

- To setup gateway for CoinmarketCap price API, you have to setup these environments:
  - ADAPTER_TYPE = "standard_crypto_price"
  - ADAPTER_NAME = "coin_market_cap"
  - COIN_MARKET_CAP_API_KEY = <YOUR_API_KEY>

### CryptoCompare

- To setup gateway for CryptoCompare price API, you have to setup these environments:
  - ADAPTER_TYPE = "standard_crypto_price"
  - ADAPTER_NAME = "crypto_compare"
  - CRYPTO_COMPARE_API_KEY = <YOUR_API_KEY>
