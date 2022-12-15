from .FormElement import FormElement
from ....ext_exception import ExtNotImplemented


class FormGroup(FormElement):
    pass

    @classmethod
    def decode(cls, form, raw_data):
        data = super().decode(form, raw_data)
        if raw_data[20] != '1':
            raise ExtNotImplemented(
                message='предоставьте образец формы разработчикам',
                detail=f'Форма {form.header["name"]}, элемент {data["name"]}')
        data['child'] = cls.decode_list(form, raw_data, 22)
        return data

    @classmethod
    def encode(cls, form, data):
        try:
            child = data['child']
        except KeyError:
            child = []
        if not child:
            return super().encode(form, data)
        cls.encode_list(form, child, data['raw'], 22)
        return data['raw']
