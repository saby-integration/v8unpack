from .ExternalDataProcessor import ExternalDataProcessor


class ExternalDataProcessor81(ExternalDataProcessor):
    version = '81'
    pass

    @classmethod
    def encode_version(cls):
        return [[
            [
                "106",
                "0"
            ]
        ]]

    def encode_root(self):
        return [[
            "2",
            self.header["file_uuid"]
        ]]
