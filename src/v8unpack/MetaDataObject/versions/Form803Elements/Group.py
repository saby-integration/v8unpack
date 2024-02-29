from .FormElement import FormElement, check_count_element, calc_offset
from ....ext_exception import ExtException
from ....helper import FuckingBrackets


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
        new_path = f"{path}/{data['name']}" if path else data['name']
        new_path = new_path.replace('includr_', 'include_')
        data['child'] = cls.decode_list(form, raw_data, index, new_path)
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
            name_for_child = f"include_{data['name'][8:]}" if data['name'][:8] == 'includr_' else data['name']
            new_path = f"{path}/{name_for_child}" if path else name_for_child
            cls.encode_list(form, child, raw_data, index, new_path)
            return raw_data
        except Exception as err:
            raise ExtException(parent=err)
