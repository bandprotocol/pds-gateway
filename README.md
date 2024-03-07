# Premium Data Sources Gateway

The gateway for data sources on BandChain that require an API key for access. However, to prevent exposing the key on the chain, our solution allows secure access to the API without revealing the key. Only validators assigned to retrieve data for BandChain requests have the capability to obtain price data from these data sources.

## Requirements

### Environment Variables

Utilize the `.env` file by running:

```bash
cp .env.example .env
```

Ensure to update the environment variables for the Gateway and your chosen adapter.

## Running the Application

> Note: You have the option to set the environment variable `MODE=development` to facilitate testing your API locally. This allows you to make requests without the necessity of verifying that the requests originate from validators assigned to retrieve data for BandChain.

### Docker Compose

To run the application using Docker Compose:

```bash
docker-compose up
```

## Testing

Execute tests with:

```bash
pytest
```

## Supported Adapters

### StandardCryptoPrice

This adapter type retrieves the current price of each cryptocurrency symbol. Below are the specifications for the request, response, adapter input, and adapter output.

#### [GET] Request

Parameters:

- `symbols`: str (e.g., "BAND,ALPHA")

#### Response

```python
prices: []{symbol: str, price: float, timestamp: integer}
```

Example:

```python
[{symbol: "BAND", price: 99999, timestamp: 161111111111}, {symbol: "ALPHA", price: 99999, timestamp: 161111111111}]
```

#### Set Environment Valuables

- CoinMarketCap:

  - `ADAPTER_TYPE = "standard_crypto_price"`
  - `ADAPTER_NAME = "coin_market_cap"`
  - `API_KEY = <YOUR_COIN_MARKET_CAP_API_KEY>`

- CryptoCompare:

  - `ADAPTER_TYPE = "standard_crypto_price"`
  - `ADAPTER_NAME = "crypto_compare"`
  - `API_KEY = <YOUR_CRYPTO_COMPARE_API_KEY>`

- CoinGecko:
  - `ADAPTER_TYPE = "standard_crypto_price"`
  - `ADAPTER_NAME = "coin_gecko"`
  - `API_KEY = <YOUR_COIN_GECKO_API_KEY>`

## VerifiableAI

This VerifiableAI adapter type is used to request the AI API.

### OpenAI

#### [POST] Request

Body:

```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    { "role": "user", "content": "What is the best French cheese?" }
  ],
  "temperature": 0.7,
  "top_p": 1,
  "max_tokens": 25,
  "stream": false,
  "seed": 1
}
```

#### Response

```json
{
  "answer": "It is subjective and depends on personal preference, but some popular French cheeses include Brie, Camembert, Roquefort"
}
```

#### Set Environment Valuables

- `ADAPTER_TYPE = "verifiable_ai"`
- `ADAPTER_NAME = "openai"`
- `API_KEY = <YOUR_OPEN_AI_API_KEY>`

### Mistral

#### [POST] Request

Body:

```json
{
  "model": "mistral-tiny",
  "messages": [
    { "role": "user", "content": "What is the best French cheese?" }
  ],
  "temperature": 0.7,
  "top_p": 1,
  "max_tokens": 16,
  "stream": false,
  "safe_prompt": false,
  "random_seed": 1
}
```

#### Response

```json
{
  "answer": "It is subjective and depends on personal preference, but some popular French cheeses include B"
}
```

#### Set Environment Valuables

- `ADAPTER_TYPE = "verifiable_ai"`
- `ADAPTER_NAME = "mistral"`
- `API_KEY = <YOUR_MISTRAL_API_KEY>`
