from .FormElement import FormElement, calc_offset, check_count_element
from ....helper import FuckingBrackets
from ....ext_exception import ExtException


class Decoration(FormElement):
    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (1, 1), (2, 0)], raw_data)

    # @classmethod
    # def decode(cls, form, path, raw_data):
    #     # _version = raw_data[0]
    #     result = super().decode(form, path, raw_data)
    #     return result

    # @classmethod
    # def decode_5(cls, form, raw_data):
    #
    #     try:
    #         size = check_count_element([
    #             (3, 1), (1, 1), (15, 1)
    #         ], raw_data)
    #     except TypeError:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     except Exception as err:
    #         raise ExtException(parent=err)
    #     if size != 34:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     result = super().decode(form, raw_data)
    #     return result
    #
    # @classmethod
    # def decode_11(cls, form, raw_data):
    #     try:
    #         size = check_count_element([
    #             (3, 1), (1, 1), (15, 1), (5, 1)
    #         ], raw_data)
    #     except TypeError:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     except Exception as err:
    #         raise ExtException(parent=err)
    #     if size != 33:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     result = super().decode(form, raw_data)
    #     return result
    #
    # @classmethod
    # def decode_12(cls, form, raw_data):
    #     try:
    #         size = check_count_element([
    #             (3, 1), (1, 1), (15, 1), (5, 1)
    #         ], raw_data)
    #     except TypeError:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     except Exception as err:
    #         raise ExtException(parent=err)
    #     if size != 34:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     result = super().decode(form, raw_data)
    #     return result
    #
    # @classmethod
    # def _decode(cls, form, raw_data):
    #     try:
    #         size = check_count_element([
    #             (3, 1), (1, 1), (15, 1), (5, 1)
    #         ], raw_data)
    #     except TypeError:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     except Exception as err:
    #         raise ExtException(parent=err)
    #     if size != 34:
    #         raise FuckingBrackets(detail=cls.__name__)
    #     result = super().decode(form, raw_data)
    #     return result
