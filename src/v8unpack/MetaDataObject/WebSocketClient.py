from ..MetaDataObject.core.Simple import Simple


class WebSocketClient(Simple):
    pass

    def decode_header(self, header_data, *, id_in_separate_file=True):
        super().decode_header(header_data, id_in_separate_file=id_in_separate_file)
        self.header['url'] = header_data[0][1][3]
        self.header['user'] = header_data[0][1][4]
        self.header['password'] = header_data[0][1][5]
