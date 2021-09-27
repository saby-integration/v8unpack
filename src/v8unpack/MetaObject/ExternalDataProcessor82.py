from .ExternalDataProcessor83 import ExternalDataProcessor83


class ExternalDataProcessor82(ExternalDataProcessor83):
    version = '82'

    @classmethod
    def encode_version(cls):
        return [[
            [
                "216",
                "0"
            ]
        ]]
