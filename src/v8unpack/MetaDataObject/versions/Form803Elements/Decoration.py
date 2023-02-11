from .FormElement import FormElement, calc_offset, check_count_element
from ....helper import FuckingBrackets
from ....ext_exception import ExtException


class Decoration(FormElement):
    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (4, 0)], raw_data)

    @classmethod
    def decode(cls, form, raw_data):
        try:
            size = check_count_element([
                (3, 1), (17, 1), (5, 1)
            ], raw_data)
        except TypeError:
            raise FuckingBrackets(detail=cls.__name__)
        except Exception as err:
            raise ExtException(parent=err)
        if (raw_data[0] == '11' and size != 34) or (raw_data[0] == '12' and size != 35):
            raise FuckingBrackets(detail=cls.__name__)
        result = super().decode(form, raw_data)
        return result
