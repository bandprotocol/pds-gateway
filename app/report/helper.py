import json


def bytes_to_json(bytes_data):
    return json.loads(bytes_data.decode("utf-8").replace("'", '"'))
