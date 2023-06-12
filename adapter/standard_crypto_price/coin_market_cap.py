import os
from datetime import datetime, timezone
from typing import Dict

import httpx

from adapter.standard_crypto_price.base import StandardCryptoPrice, Input, Output


class CoinMarketCap(StandardCryptoPrice):
    api_url: str = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    api_key: str
    symbols_map: Dict[str, str] = None

    def __init__(self):
        self.api_key = os.getenv("API_KEY", None)

        self.symbols_map = {
            "1INCH": "1inch",
            "AAVE": "aave",
            "ABBC": "abbc-coin",
            "ABYSS": "abyss",
            "ACH": "alchemy-pay",
            "ADA": "cardano",
            "AGIX": "singularitynet",
            "AKRO": "akropolis",
            "ALCX": "alchemix",
            "ALGO": "algorand",
            "ALI": "alethea-artificial-liquid-intelligence-token",
            "ALPHA": "alpha-finance-lab",
            "AMP": "amp",
            "AMPL": "ampleforth",
            "ANC": "anchor-protocol",
            "ANKR": "ankr",
            "ANT": "aragon",
            "APE": "apecoin-ape",
            "API3": "api3",
            "APOLLO": "apollo-dao",
            "APT": "aptos",
            "AR": "arweave",
            "ARAW": "araw",
            "ARB": "arbitrum",
            "ARPA": "arpa-chain",
            "AST": "airswap",
            "ASTR": "astar",
            "ASTRAFER": "astrafer",
            "ASTRO": "astroport",
            "ATOM": "cosmos",
            "AUDIO": "audius",
            "AUTO": "auto",
            "AVAX": "avalanche",
            "AXL": "axelar",
            "AXS": "axie-infinity",
            "BABYDOGE": "baby-doge-coin",
            "BAL": "balancer",
            "BAND": "band-protocol",
            "BAT": "basic-attention-token",
            "BCH": "bitcoin-cash",
            "BDX": "beldex",
            "BEL": "bella-protocol",
            "BETA": "beta-finance",
            "BGB": "bitget-token-new",
            "BICO": "biconomy",
            "BIT": "bitdao",
            "BLUR": "blur-token",
            "BLZ": "bluzelle",
            "BNB": "bnb",
            "BNT": "bancor",
            "BNX": "binaryx-new",
            "BOBA": "boba-network",
            "BONE": "bone-shibaswap",
            "BORA": "bora",
            "BRISE": "bitrise-token",
            "BSV": "bitcoin-sv",
            "BTC": "bitcoin",
            "BTCB": "bitcoin-bep2",
            "BTG": "bitcoin-gold",
            "BTM": "bytom",
            "BTRST": "braintrust",
            "BTS": "bitshares",
            "BTT": "bittorrent-new",
            "BTTOLD": "bittorrent",
            "BUSD": "binance-usd",
            "BZRX": "bzx-protocol",
            "C98": "coin98",
            "CAKE": "pancakeswap",
            "CELO": "celo",
            "CELR": "celer-network",
            "CFX": "conflux-network",
            "CHR": "chromia",
            "CHSB": "swissborg",
            "CHZ": "chiliz",
            "CKB": "nervos-network",
            "CNNC": "cannation",
            "CNX": "cryptonex",
            "COMBO": "combo-network",
            "COMP": "compound",
            "CORE": "core-dao",
            "CREAM": "cream-finance",
            "CRO": "cronos",
            "CRV": "curve-dao-token",
            "CSPR": "casper",
            "CTSI": "cartesi",
            "CUSD": "celo-dollar",
            "CVC": "civic",
            "CVX": "convex-finance",
            "DAI": "multi-collateral-dai",
            "DAO": "dao-maker",
            "DASH": "dash",
            "DCR": "decred",
            "DEL": "decimal",
            "DENT": "dent",
            "DERO": "dero",
            "DESO": "deso",
            "DEXE": "dexe",
            "DFI": "defichain",
            "DGB": "digibyte",
            "DIA": "dia",
            "DKA": "dkargo",
            "DOGE": "dogecoin",
            "DOT": "polkadot-new",
            "DPI": "defi-pulse-index",
            "DYDX": "dydx",
            "EDGT": "edgecoin",
            "EDU": "open-campus",
            "EGLD": "multiversx-egld",
            "ELF": "aelf",
            "ELON": "dogelon",
            "ENJ": "enjin-coin",
            "ENS": "ethereum-name-service",
            "EOS": "eos",
            "ERG": "ergo",
            "ESCE": "escroco-emerald",
            "ETC": "ethereum-classic",
            "ETH": "ethereum",
            "ETHW": "ethereum-pow",
            "EURS": "stasis-euro",
            "EVER": "everscale",
            "EWT": "energy-web-token",
            "FET": "fetch",
            "FGC": "fantasygold",
            "FIL": "filecoin",
            "FLEX": "flex",
            "FLOKI": "floki-inu",
            "FLOW": "flow",
            "FLR": "flare",
            "FLUX": "zel",
            "FNSA": "finschia",
            "FNX": "finnexus",
            "FOR": "the-force-protocol",
            "FRAX": "frax",
            "FTM": "fantom",
            "FTT": "ftx-token",
            "FXS": "frax-share",
            "GAL": "galxe",
            "GALA": "gala",
            "GCR": "global-currency-reserve",
            "GLM": "golem-network-tokens",
            "GLMR": "moonbeam",
            "GLOW": "glow-token",
            "GMT": "green-metaverse-token",
            "GMX": "gmx",
            "GNO": "gnosis-gno",
            "GNS": "gains-network",
            "GRT": "the-graph",
            "GT": "gatetoken",
            "GUSD": "gemini-dollar",
            "HBAR": "hedera",
            "HBTC": "huobi-btc",
            "HEGIC": "hegic",
            "HEX": "hex",
            "HFT": "hashflow",
            "HIVE": "hive-blockchain",
            "HNT": "helium",
            "HOT": "holo",
            "HT": "huobi-token",
            "ICP": "internet-computer",
            "ICX": "icon",
            "ID": "space-id",
            "ILV": "illuvium",
            "IMX": "immutable-x",
            "INJ": "injective",
            "IOST": "iostoken",
            "IOTX": "iotex",
            "JASMY": "jasmy",
            "JOE": "joe",
            "JST": "just",
            "KAI": "kardiachain",
            "KAS": "kaspa",
            "KAVA": "kava",
            "KCS": "kucoin-token",
            "KDA": "kadena",
            "KEEP": "keep-network",
            "KEY": "selfkey",
            "KLAY": "klaytn",
            "KMD": "komodo",
            "KNC": "kyber-network-crystal-v2",
            "KP3R": "keep3rv1",
            "KSM": "kusama",
            "KUJI": "kujira",
            "LDO": "lido-dao",
            "LEO": "unus-sed-leo",
            "LINA": "linear",
            "LINK": "chainlink",
            "LOOM": "loom-network",
            "LPT": "livepeer",
            "LQTY": "liquity",
            "LRC": "loopring",
            "LSK": "lisk",
            "LTC": "litecoin",
            "LUNA": "terra-luna-v2",
            "LUNC": "terra-luna",
            "LUSD": "liquity-usd",
            "LYXE": "lukso",
            "MAGIC": "magic-token",
            "MANA": "decentraland",
            "MASK": "mask-network",
            "MATIC": "polygon",
            "MC": "merit-circle",
            "MED": "medibloc",
            "METIS": "metisdao",
            "MIM": "magic-internet-money",
            "MINA": "mina",
            "MINE": "pylon-protocol",
            "MIOTA": "iota",
            "MIR": "mirror-protocol",
            "MKR": "maker",
            "MLK": "milk-alliance",
            "MLN": "enzyme",
            "MOB": "mobilecoin",
            "MOVR": "moonriver",
            "MRS": "metars-genesis",
            "MTA": "meta",
            "MTL": "metal",
            "MVL": "mvl",
            "MX": "mx-token",
            "NEAR": "near-protocol",
            "NEO": "neo",
            "NEXO": "nexo",
            "NFT": "apenft",
            "NKN": "nkn",
            "NMR": "numeraire",
            "NYM": "nym",
            "OCEAN": "ocean-protocol",
            "OGN": "origin-protocol",
            "OKB": "okb",
            "OMG": "omg",
            "ONE": "harmony",
            "ONG": "ontology-gas",
            "ONT": "ontology",
            "ONUS": "onus",
            "OP": "optimism-ethereum",
            "ORDI": "ordinals",
            "ORION": "orion-money",
            "OSMO": "osmosis",
            "PAXG": "pax-gold",
            "PENDLE": "pendle",
            "PEOPLE": "constitutiondao",
            "PEPE": "pepe",
            "PERP": "perpetual-protocol",
            "PICKLE": "pickle-finance",
            "PLA": "playdapp",
            "PLR": "pillar",
            "PNK": "kleros",
            "PNT": "pnetwork",
            "POLY": "polymath-network",
            "POLYX": "polymesh",
            "POWR": "power-ledger",
            "PROM": "prom",
            "PSI": "nexus-protocol",
            "PUNDIX": "pundix-new",
            "PYR": "vulcan-forged-pyr",
            "QKC": "quarkchain",
            "QNT": "quant",
            "QTUM": "qtum",
            "RAD": "radicle",
            "RBN": "ribbon-finance",
            "RBTC": "rsk-smart-bitcoin",
            "RDNT": "radiant-capital",
            "REN": "ren",
            "REP": "augur",
            "REQ": "request",
            "RIF": "rsk-infrastructure-framework",
            "RLC": "rlc",
            "RNDR": "render-token",
            "RON": "ronin",
            "ROSE": "oasis-network",
            "RPL": "rocket-pool",
            "RSR": "reserve-rights",
            "RSV": "reserve",
            "RUNE": "thorchain",
            "RVN": "ravencoin",
            "SAND": "the-sandbox",
            "SC": "siacoin",
            "SCRT": "secret",
            "SFI": "saffron-finance",
            "SFP": "safepal",
            "SHIB": "shiba-inu",
            "SKL": "skale-network",
            "SLP": "smooth-love-potion",
            "SNT": "status",
            "SNX": "synthetix",
            "SOL": "solana",
            "SPEC": "spectrum-token",
            "SPELL": "spell-token",
            "SRM": "serum",
            "SSV": "ssv-network",
            "STEEM": "steem",
            "STETH": "steth",
            "STG": "stargate-finance",
            "STMX": "stormx",
            "STORJ": "storj",
            "STPT": "standard-tokenization-protocol",
            "STRK": "strike",
            "STT": "starterra",
            "STX": "stacks",
            "SUI": "sui",
            "SURE": "insure",
            "SUSD": "susd",
            "SUSHI": "sushiswap",
            "SXP": "sxp",
            "SYN": "synapse-2",
            "SYS": "syscoin",
            "T": "threshold",
            "TEL": "telcoin",
            "TFUEL": "theta-fuel",
            "THETA": "theta-network",
            "TNC": "tnc-coin",
            "TOMI": "tominet",
            "TOMO": "tomochain",
            "TON": "toncoin",
            "TRAC": "origintrail",
            "TRB": "tellor",
            "TRIBE": "tribe",
            "TRX": "tron",
            "TUSD": "trueusd",
            "TWD": "terra-world-token",
            "TWT": "trust-wallet-token",
            "UBT": "unibright",
            "UMA": "uma",
            "UNI": "uniswap",
            "UPP": "sentinel-protocol",
            "USDC": "usd-coin",
            "USDD": "usdd",
            "USDJ": "usdj",
            "USDP": "paxos-standard",
            "USDT": "tether",
            "USDX": "usdx-kava",
            "UST": "terrausd",
            "USTC": "terrausd",
            "VBG": "vibing",
            "VET": "vechain",
            "VIDT": "vidt-datalink",
            "VKR": "valkyrie-protocol",
            "VVS": "vvs-finance",
            "WAN": "wanchain",
            "WAVES": "waves",
            "WAXP": "wax",
            "WBETH": "wrapped-beacon-eth",
            "WBNB": "wbnb",
            "WBTC": "wrapped-bitcoin",
            "WEMIX": "wemix",
            "WEOS": "wrapped-eos",
            "WHALE": "white-whale",
            "WHBAR": "wrapped-hedera",
            "WILD": "wilder-world",
            "WKAVA": "wrapped-kava",
            "WNXM": "wrapped-nxm",
            "WOO": "wootrade",
            "WRX": "wazirx",
            "WTRX": "wrapped-tron",
            "XAUT": "tether-gold",
            "XCH": "chia-network",
            "XDC": "xinfin",
            "XDEFI": "xdefi",
            "XEC": "ecash",
            "XEM": "nem",
            "XLM": "stellar",
            "XMR": "monero",
            "XNO": "nano",
            "XPLA": "xpla",
            "XPR": "proton",
            "XRD": "radix-protocol",
            "XRP": "xrp",
            "XTZ": "tezos",
            "XVS": "venus",
            "XYM": "symbol",
            "YAM": "yamv1",
            "YAMV2": "yam-v2",
            "YFI": "yearn-finance",
            "YFII": "yearn-finance-ii",
            "YGG": "yield-guild-games",
            "ZEC": "zcash",
            "ZEN": "horizen",
            "ZIL": "zilliqa",
            "ZRX": "0x",
        }

    async def call(self, input_: Input) -> Output:
        client = httpx.AsyncClient()
        response = await client.request(
            "GET",
            self.api_url,
            params={"slug": ",".join([self.symbols_map.get(symbol, symbol) for symbol in input_["symbols"]])},
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

        return Output(prices=prices)
