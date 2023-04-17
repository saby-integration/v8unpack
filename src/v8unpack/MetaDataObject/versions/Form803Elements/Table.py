from .FormElement import FormElement, check_count_element, calc_offset
from ....helper import FuckingBrackets
from ....ext_exception import ExtException


class Table(FormElement):
    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(4, 1), (1, 0)], raw_data)

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
        return super().decode(form, path, raw_data)