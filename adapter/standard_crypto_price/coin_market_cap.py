from adapter.standard_crypto_price import StandardCryptoPrice, Input, Output
from typing import Dict
from datetime import datetime, timezone
import httpx
import os


class CoinMarketCap(StandardCryptoPrice):
    api_url: str = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    api_key: str
    symbols_map: Dict[str, str] = None

    def __init__(self):
        self.api_key = os.getenv("COIN_MARKET_CAP_API_KEY", None)

        self.symbols_map = {
            "AAVE": "aave",
            "ABYSS": "abyss",
            "ADA": "cardano",
            "AKRO": "akropolis",
            "ALCX": "alchemix",
            "ALGO": "algorand",
            "ALPHA": "alpha-finance-lab",
            "AMPL": "ampleforth",
            "ANC": "anchor-protocol",
            "ANKR": "ankr",
            "ANT": "aragon",
            "ARPA": "arpa-chain",
            "AST": "airswap",
            "ASTRO": "astroport",
            "ATOM": "cosmos",
            "AUTO": "auto",
            "AVAX": "avalanche",
            "AXS": "axie-infinity",
            "BAL": "balancer",
            "BAND": "band-protocol",
            "BAT": "basic-attention-token",
            "BCH": "bitcoin-cash",
            "BEL": "bella-protocol",
            "BETA": "beta-finance",
            "BLZ": "bluzelle",
            "BNB": "binance-coin",
            "BNT": "bancor",
            "BOBA": "boba-network",
            "BORA": "bora",
            "BSV": "bitcoin-sv",
            "BTC": "bitcoin",
            "BTG": "bitcoin-gold",
            "BTM": "bytom",
            "BTS": "bitshares",
            "BTT": "bittorrent-new",
            "BUSD": "binance-usd",
            "BZRX": "bzx-protocol",
            "C98": "coin98",
            "CAKE": "pancakeswap",
            "CELO": "celo",
            "CKB": "nervos-network",
            "COMP": "compound",
            "CREAM": "cream-finance",
            "CRO": "crypto-com-coin",
            "CRV": "curve-dao-token",
            "CUSD": "celo-dollar",
            "CVC": "civic",
            "DAI": "multi-collateral-dai",
            "DASH": "dash",
            "DCR": "decred",
            "DGB": "digibyte",
            "DIA": "dia",
            "DOGE": "dogecoin",
            "DOT": "polkadot-new",
            "DPI": "defi-pulse-index",
            "DYDX": "dydx",
            "EGLD": "elrond-egld",
            "ELF": "aelf",
            "ENJ": "enjin-coin",
            "EOS": "eos",
            "ETC": "ethereum-classic",
            "ETH": "ethereum",
            "EURS": "stasis-euro",
            "EWT": "energy-web-token",
            "FET": "fetch",
            "FIL": "filecoin",
            "FNX": "finnexus",
            "FOR": "the-force-protocol",
            "FRAX": "frax",
            "FTM": "fantom",
            "FTT": "ftx-token",
            "GALA": "gala",
            "GNO": "gnosis-gno",
            "GRT": "the-graph",
            "HBAR": "hedera",
            "HEGIC": "hegic",
            "HNT": "helium",
            "HT": "huobi-token",
            "ICX": "icon",
            "IMX": "immutable-x",
            "INJ": "injective-protocol",
            "IOST": "iostoken",
            "IOTX": "iotex",
            "JOE": "joe",
            "JST": "just",
            "KAI": "kardiachain",
            "KAVA": "kava",
            "KDA": "kadena",
            "KEY": "selfkey",
            "KLAY": "klaytn",
            "KMD": "komodo",
            "KP3R": "keep3rv1",
            "KSM": "kusama",
            "KUJI": "kujira",
            "LEO": "unus-sed-leo",
            "LINA": "linear",
            "LINK": "chainlink",
            "LOOM": "loom-network",
            "LRC": "loopring",
            "LSK": "lisk",
            "LTC": "litecoin",
            "MANA": "decentraland",
            "MATIC": "polygon",
            "MIM": "magic-internet-money",
            "MINE": "pylon-protocol",
            "MIOTA": "iota",
            "MIR": "mirror-protocol",
            "MKR": "maker",
            "MLN": "enzyme",
            "MOVR": "moonriver",
            "MTA": "meta",
            "MTL": "metal",
            "MVL": "mvl",
            "NEAR": "near-protocol",
            "NEO": "neo",
            "NMR": "numeraire",
            "OCEAN": "ocean-protocol",
            "OGN": "origin-protocol",
            "OKB": "okb",
            "OMG": "omg",
            "ONE": "harmony",
            "ONT": "ontology",
            "OSMO": "osmosis",
            "PAXG": "pax-gold",
            "PERP": "perpetual-protocol",
            "PICKLE": "pickle-finance",
            "PLR": "pillar",
            "PNK": "kleros",
            "PNT": "pnetwork",
            "POLY": "polymath-network",
            "POWR": "power-ledger",
            "QKC": "quarkchain",
            "QNT": "quant",
            "QTUM": "qtum",
            "REN": "ren",
            "REP": "augur",
            "REQ": "request",
            "RLC": "rlc",
            "ROSE": "oasis-network",
            "RSR": "reserve-rights",
            "RSV": "reserve",
            "RUNE": "thorchain",
            "SAND": "the-sandbox",
            "SC": "siacoin",
            "SCRT": "secret",
            "SFI": "saffron-finance",
            "SKL": "skale-network",
            "SNT": "status",
            "SNX": "synthetix-network-token",
            "SOL": "solana",
            "SPELL": "spell-token",
            "SRM": "serum",
            "STMX": "stormx",
            "STORJ": "storj",
            "STRK": "strike",
            "STT": "starterra",
            "STX": "stacks",
            "SUSD": "susd",
            "SUSHI": "sushiswap",
            "SXP": "swipe",
            "THETA": "theta",
            "TOMO": "tomochain",
            "TRB": "tellor",
            "TRX": "tron",
            "TUSD": "trueusd",
            "TWT": "trust-wallet-token",
            "UBT": "unibright",
            "UMA": "uma",
            "UNI": "uniswap",
            "UPP": "sentinel-protocol",
            "USDC": "usd-coin",
            "USDP": "paxos-standard",
            "USDT": "tether",
            "UST": "terrausd",
            "VET": "vechain",
            "VIDT": "vidt-datalink",
            "VKR": "valkyrie-protocol",
            "WAN": "wanchain",
            "WAVES": "waves",
            "WBTC": "wrapped-bitcoin",
            "WEMIX": "wemix",
            "WHALE": "white-whale",
            "WRX": "wazirx",
            "XEM": "nem",
            "XLM": "stellar",
            "XMR": "monero",
            "XPR": "proton",
            "XRP": "xrp",
            "XTZ": "tezos",
            "XVS": "venus",
            "YAM": "yamv1",
            "YAMV2": "yam-v2",
            "YFI": "yearn-finance",
            "YFII": "yearn-finance-ii",
            "ZEC": "zcash",
            "ZIL": "zilliqa",
            "ZRX": "0x",
            "ILV": "illuvium",
            "YGG": "yield-guild-games",
            "AUDIO": "audius",
            "APOLLO": "apollo-dao",
            "GLOW": "glow-token",
            "ORION": "orion-money",
            "SPEC": "spectrum-token",
            "TWD": "terra-world-token",
            "XDEFI": "xdefi",
            "PSI": "nexus-protocol",
        }

    async def call(self, input: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "GET",
            self.api_url,
            params={"slug": ",".join([self.symbols_map.get(symbol, symbol) for symbol in input["symbols"]])},
            headers={
                "X-CMC_PRO_API_KEY": self.api_key,
            },
        )
        response.raise_for_status()
        response_json = response.json()

        if response_json["status"]["error_code"] != 0:
            raise Exception(f"{response_json['status']['error_message']}")

        prices = [
            {
                "symbol": data["symbol"],
                "price": float(data["quote"]["USD"]["price"]),
                "timestamp": int(
                    datetime.strptime(data["last_updated"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    .replace(tzinfo=timezone.utc)
                    .timestamp()
                ),
            }
            for data in response_json["data"].values()
        ]

        return Output(
            prices=prices,
        )
