from .FormElement import FormElement, check_count_element, calc_offset
from ....helper import FuckingBrackets, str_decode
from ....ext_exception import ExtException


class Group(FormElement):
    pass

    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (1, 1), (2, 0)], raw_data)

    @classmethod
    def decode(cls, form, path, raw_data):
        try:
            size = check_count_element([
                (3, 1), (1, 1), (17, 2)
            ], raw_data)
        except Exception as err:
            raise ExtException(parent=err)
        if raw_data[0] == '22' and size < 20:
            raise FuckingBrackets(detail=cls.__name__)

        data = super().decode(form, path, raw_data)
        index = calc_offset([(3, 1), (1, 1), (17, 0)], raw_data)
        data['child'] = cls.decode_list(form, raw_data, index, f"{path}/{data['name']}")
        return data

    @classmethod
    def encode(cls, form, path, data):
        try:
            try:
                child = data['child']
            except KeyError:
                child = []
            raw_data = super().encode(form, path, data)
            if not child:
                return raw_data
            index = calc_offset([(3, 1), (1, 1), (17, 0)], raw_data)
            cls.encode_list(form, child, raw_data, index, f"{path}/{data['name']}")
            return raw_data
        except Exception as err:
            raise ExtException(parent=err)
