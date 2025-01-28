from .FormElement import FormElement
from v8unpack.helper import calc_offset


class Field(FormElement):
    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (1, 1), (2, 0)], raw_data)

    @classmethod
    def get_prop_link_offset(cls, raw_data):
        return calc_offset([(3, 1), (1, 1), (7, 0)], raw_data)
