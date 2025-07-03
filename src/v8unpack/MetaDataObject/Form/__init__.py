from v8unpack.MetaDataObject.core.Simple import SimpleNameFolder
from .Form5 import Form5
from .Form9 import Form9


class Form(SimpleNameFolder):
    versions = {
        '5': Form5,
        '7': Form5,
        '9': Form9,
        '12': Form9,
        '13': Form9,
        '14': Form9,
    }
    # @classmethod
    # def read_header(cls, src_dir, src_file_name, data_id):
    #     return super().read_header(src_dir, f"{data_id['type']}{src_file_name}", data_id)

    @classmethod
    def get_form_root(cls, header_data):
        # return header_data[0][1][1]
        obj_version = header_data[0][1][0]
        if obj_version == '0':
            return header_data[0][1]
        elif obj_version == '1':
            return header_data[0][1][1]
        raise NotImplementedError()

    @classmethod
    def get_decode_header(cls, header_data):
        return cls.get_form_root(header_data)[1][1]

    @classmethod
    def get_version(cls, header_data, options):
        form_root = cls.get_form_root(header_data)
        form_version = form_root[1][0]
        return form_version


class Form1(Form):
    @classmethod
    def get_form_root(cls, header_data):
        return header_data[0][1]


class Form0(Form):
    @classmethod
    def get_form_root(cls, header_data):
        return header_data[0]
