from typing import List


class UnsupportedDsException(Exception):
    def __init__(self, allowed_data_source_ids: List[int], data_source_id: str):
        self.allowed_data_source_ids = allowed_data_source_ids
        self.data_source_id = data_source_id
