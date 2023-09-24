from .FormElement import FormElement, calc_offset


class Field(FormElement):
    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (1, 1), (1, 0)], raw_data)
