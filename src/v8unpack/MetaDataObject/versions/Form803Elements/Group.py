from .FormElement import FormElement, check_count_element, calc_offset
from ....helper import FuckingBrackets
from ....ext_exception import ExtException


class Group(FormElement):
    pass

    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (1, 1), (2, 0)], raw_data)

    @classmethod
    def decode(cls, form, raw_data):
        try:
            size = check_count_element([
                (3, 1), (1, 1), (17, 2)
            ], raw_data)
        except Exception as err:
            raise ExtException(parent=err)
        if raw_data[0] == '22' and size != 30:
            raise FuckingBrackets()

        data = super().decode(form, raw_data)
        index = calc_offset([(3, 1), (1, 1), (17, 0)], raw_data)
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
        index = calc_offset([(3, 1), (1, 1), (17, 0)], data['raw'])
        cls.encode_list(form, child, data['raw'], index)
        return data['raw']
