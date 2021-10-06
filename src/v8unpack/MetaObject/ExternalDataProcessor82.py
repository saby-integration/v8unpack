from .ExternalDataProcessor83 import ExternalDataProcessor83


class ExternalDataProcessor82(ExternalDataProcessor83):
    version = '82'

    def encode_version(self):
        return [[
            [
                "216",
                "0"
            ]
        ]]
