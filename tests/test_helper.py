from genericpath import isdir
from sanic import Sanic
from app.utils import helper
from app import create_app
import unittest
from os import listdir
from os.path import isfile, join

app = create_app("test", {"VERIFY_REQUEST_URL": "http://localhost.example", "CACHE_SIZE": 5000, "TTL_TIME": "1m"})


class TestUtilsHelper(unittest.TestCase):
    def test_get_bandchain_params(self):
        params = helper.get_bandchain_params(
            {
                "BAND_CHAIN_ID": "bandchain",
                "BAND_VALIDATOR": "bandcoolvalidator",
                "BAND_EXTERNAL_ID": "2",
                "BAND_REPORTER": "bandcoolreporter",
                "BAND_SIGNATURE": "coolsignature",
                "BAND_REQUEST_ID": "1",
            }
        )

        self.assertEqual(
            params,
            {
                "chain_id": "bandchain",
                "validator": "bandcoolvalidator",
                "external_id": "2",
                "reporter": "bandcoolreporter",
                "signature": "coolsignature",
                "request_id": "1",
            },
        )

    def test_get_adapter(self):
        path = "./app/adapter"
        standards = [f for f in listdir(path) if isdir(join(path, f)) and not f.startswith("__")]
        for standard in standards:
            adapters = [
                f.replace(".py", "")
                for f in listdir(join(path, standard))
                if isfile(join(path, standard, f)) and not f.startswith("__")
            ]

            for adapter in adapters:
                helper.get_adapter(standard, adapter + "")

    def test_verify_data_source_id_success(self):
        app = Sanic.get_app()
        app.update_config({"MODE": "development", "ALLOWED_DATA_SOURCE_IDS": ["1", "2"]})
        result = helper.verify_data_source_id("1")
        self.assertTrue(result)

    def test_verify_data_source_id_fail(self):
        app = Sanic.get_app()
        app.update_config({"MODE": "development", "ALLOWED_DATA_SOURCE_IDS": ["1", "2"]})
        try:
            result = helper.verify_data_source_id("3")
            self.assertFalse(result)
        except:
            pass
