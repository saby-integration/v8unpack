from .Form803 import Form803


class CommonForm803(Form803):

    @classmethod
    def get_decode_obj_header(cls, header):
        return header[0][1]

    def decode_data(self, src_dir, uuid):
        super(CommonForm803, self).decode_data(src_dir, uuid)
        _header_obj = self.get_decode_obj_header(self.header['data'])
        self.header['Пояснение'] = _header_obj[3]
        self.header['Использовать стандартные команды'] = _header_obj[4]

    def encode_header(self):
        return [[
            "1",
            [
                "4",
                self.encode_header_title(),
                self.header['Расширенное представление'],
                self.header['Пояснение'],
                self.header['Использовать стандартные команды']
            ],
            "0"
        ]]
