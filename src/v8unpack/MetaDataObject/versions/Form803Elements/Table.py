from .FormElement import FormElement, check_count_element, calc_offset
from ....helper import FuckingBrackets
from ....ext_exception import ExtException


class Table(FormElement):

    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(4, 1), (1, 0)], raw_data)

    @classmethod
    def get_prop_link_offset(cls, raw_data):
        return calc_offset([(4, 1), (7, 0)], raw_data)

    @classmethod
    def decode(cls, form, path, raw_data):
        try:
            size = check_count_element([
                (4, 1), (50, 2), (7, 2)
            ], raw_data)
        except Exception as err:
            raise ExtException(parent=err)
        if raw_data[0] == '55' and size != 99:
            raise FuckingBrackets()
        data = super().decode(form, path, raw_data)
        cls.decode_columns(form, path, raw_data, data)
        return data

    @classmethod
    def decode_columns(cls, form, path, raw_data, data):
        try:
            index = calc_offset([
                (4, 1), (50, 2), (7, 0)
            ], raw_data)
            data['child'] = cls.decode_list(form, raw_data, index, f"{path}/{data['name']}" if path else data['name'])
        except Exception as err:
            raise ExtException(parent=err)

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
            cls.encode_columns(form, child, raw_data, data, f"{path}")
            return raw_data
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def encode_columns(cls, form, child, raw_data, data, path):
        try:
            index = calc_offset([
                (4, 1), (50, 2), (7, 0)
            ], raw_data)
            cls.encode_list(form, child, raw_data, index, f"{path}/{data['name']}" if path else data['name'])
        except Exception as err:
            raise ExtException(parent=err)