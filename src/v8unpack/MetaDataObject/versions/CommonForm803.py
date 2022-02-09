from .Form803 import Form803


class CommonForm803(Form803):

    @classmethod
    def get_decode_obj_header(cls, header):
        return header[0][1]

    def encode_header(self):
        return [[
            "1",
            [
                "4",
                self.encode_header_title(),
                self.header.get('Расширенное представление', ['0']),
                self.header.get('Пояснение', ['0']),
                self.header['Использовать стандартные команды']
            ],
            "0"
        ]]
