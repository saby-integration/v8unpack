from .ExternalDataProcessor803 import ExternalDataProcessor803


class ExternalDataProcessor802(ExternalDataProcessor803):
    version = '802'

    def encode_version(self):
        return [[
            [
                "216",
                "0"
            ]
        ]]
