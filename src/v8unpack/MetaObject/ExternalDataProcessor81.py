from .ExternalDataProcessor import ExternalDataProcessor


class ExternalDataProcessor81(ExternalDataProcessor):
    version = '81'
    pass

    def encode_version(self):
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
