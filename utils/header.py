def get_bandchain_params(headers: object) -> object:

    params = {k.lower()[5:]: v for k, v in headers.items() if k.lower().startswith("band_")}

    return params
