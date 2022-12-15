from .FormElement import FormElement, calc_offset
from ....ext_exception import ExtNotImplemented


class Group(FormElement):
    pass

    @classmethod
    def decode(cls, form, raw_data):
        data = super().decode(form, raw_data)
        index = calc_offset([[4, 1]], raw_data) + 16
        data['child'] = cls.decode_list(form, raw_data, index)
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
