from ..MetaDataObject.core.Container import Container


class SettingsStorage(Container):
    ext_code = {
        'mgr': 8,
    }
    # help_file_number = 5

    @classmethod
    def get_decode_header(cls, header):
        return header[0][1][1][1]
