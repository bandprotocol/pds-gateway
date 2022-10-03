import json
import functools
from sanic.exceptions import SanicException


def collect_verify_data(func):
    @functools.wraps(func)
    async def wrapper_collect_verify_data(*args, **kwargs):
        try:
            for arg in args:
                print(arg)

            return await func(*args, **kwargs)

        except Exception as e:
            print(f"SanicException 1 {e}")
            raise e

    return wrapper_collect_verify_data


def collect_request_data(func):
    @functools.wraps(func)
    async def wrapper_collect_request_data(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except Exception as e:
            print("eoeo")
            raise SanicException("Something went wrong. aaaaaaa", status_code=500)

    return wrapper_collect_request_data
