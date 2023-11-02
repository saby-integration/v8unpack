from .FormElement import FormElement, calc_offset


class ItemAddition(FormElement):
    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (3, 0)], raw_data)
