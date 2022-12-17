from .FormElement import FormElement, calc_offset
from ....helper import FuckingBrackets


class Decoration(FormElement):
    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (3, 0)], raw_data)

    @classmethod
    def decode(cls, form, raw_data):
        if raw_data[0] in ['11', '12'] and len(raw_data) != 36:
            raise FuckingBrackets()
        result = super().decode(form, raw_data)
        return result
