from enum import Enum

from .... import helper
from ....ext_exception import ExtException


def calc_offset(counters, raw_data):
    # counters - позиции указывающие на счетчики, если не 0 то за ним идет столько записей размера size
    index = 0
    for counter_index, size in counters:
        index += counter_index
        if size:
            value = int(raw_data[index])
            index += value * size
    return index


def check_count_element(counters, raw_data):
    # counters - позиции указывающие на счетчики, если не 0 то за ним идет столько записей размера size
    index = 0
    var_len = 0
    for counter_index, size in counters:
        index += counter_index
        if size:
            value = int(raw_data[index])
            index += value * size
            var_len += value * size
    return len(raw_data) - var_len


class FormItemTypes(Enum):
    Field = '77ffcc29-7f2d-4223-b22f-19666e7250ba'
    Button = 'a9f3b1ac-f51b-431e-b102-55a69acdecad'
    Decoration = '3d3cb80c-508b-41fa-8a18-680cdf5f1712'
    Group = 'cd5394d0-7dda-4b56-8927-93ccbe967a01'
    Table = '143c00f7-a42d-4cd7-9189-88e4467dc768'
    ItemAddition = 'c5259a1d-518a-4afd-b98d-0176027e4feb'


class FormElement:

    @classmethod
    def get_name_node_offset(cls, raw_data):
        return calc_offset([(3, 1), (1, 0)], raw_data)

    @classmethod
    def decode(cls, form, raw_data):
        offset = cls.get_name_node_offset(raw_data)
        name = raw_data[offset]
        if not isinstance(name, str) or not name:
            raise ExtException(message='form elem name not string')
        return dict(
            name=helper.str_decode(name),
            type=cls.__name__,
            raw=raw_data
        )

    @classmethod
    def encode(cls, form, data):
        return data['raw']

    @classmethod
    def decode_list(cls, form, raw_data, index_element_count):
        try:
            result = []
            element_count = int(raw_data[index_element_count])
            if not element_count:
                return

            for i in range(element_count):
                metadata_type_uuid = raw_data[index_element_count + i * 2 + 1]
                elem_raw_data = raw_data[index_element_count + i * 2 + 2]
                try:
                    metadata_type = FormItemTypes(metadata_type_uuid)
                except ValueError:
                    raise ExtException(
                        message='Неизвестный тип элемента формы',
                        detail=f'{form.__class__.__name__} {form.header["name"]} : {metadata_type_uuid}'
                    )
                try:
                    handler = cls.get_class_form_elem(metadata_type.name)
                except Exception as err:
                    raise ExtException(
                        parent=err,
                        message='Проблема с парсером элемента формы',
                        detail=f'{metadata_type.name} - {err}'
                    )
                try:
                    elem_data = handler.decode(form, elem_raw_data)
                except helper.FuckingBrackets as err:
                    raise err from err
                except Exception as err:
                    raise ExtException(
                        parent=err,
                        detail=f'{metadata_type.name} - {err}',
                        message='Ошибка разбора элемента формы'
                    )
                result.append(elem_data)

            raw_data[index_element_count] = 'Дочерние элементы отдельно'
            del raw_data[index_element_count + 1:index_element_count + 1 + element_count * 2]
            return result
        except helper.FuckingBrackets as err:
            raise err
        except Exception as err:
            raise ExtException(parent=err)

    @staticmethod
    def get_class_form_elem(name):
        return helper.get_class(f'v8unpack.MetaDataObject.versions.Form803Elements.{name}.{name}')

    @classmethod
    def encode_list(cls, form, items, raw_data, index_element_count):
        result = []
        for item in items:
            try:
                metadata_type = FormItemTypes[item['type']]
            except ValueError:
                raise ExtException(
                    message='Неизвестный тип элемента формы',
                    detail=f'{form.__class__.__name__} {form.header["name"]} : {item["type"]}'
                )
            try:
                handler = cls.get_class_form_elem(metadata_type.name)
            except Exception as err:
                raise ExtException(
                    message='Проблема с парсером элемента формы',
                    detail=f'{metadata_type.name} - {err}'
                )
            elem_data = handler.encode(form, item)
            result.append(metadata_type.value)
            result.append(elem_data)
        raw_data[index_element_count] = str(len(items))
        raw_data[index_element_count + 1:index_element_count + 1] = result

        return result


class _FormRoot:
    element_node_offset = [[2, 1], [3, 1], [4, 1]]
    name = 0
    index = 0
    index_name = 0

    @classmethod
    def decode(cls, raw_data):
        return dict(
            name=helper.str_decode(raw_data[cls.index_name]),
            raw=raw_data
        )

    @classmethod
    def decode_list(cls, form, raw_data):
        try:
            if len(raw_data) <= cls.index:
                return
            items = raw_data[cls.index]
            index_element_count = 1
            element_count = int(items[index_element_count])
            if not element_count:
                return

            result = []
            for i in range(element_count):
                result.append(cls.decode(items[i + index_element_count + 1]))
            items[index_element_count] = 'Дочерние элементы отдельно'
            del items[index_element_count + 1:index_element_count + 1 + element_count]
            return result
        except Exception as err:
            pass

    @classmethod
    def encode_list(cls, form, src_dir, file_name, version):
        raw_data = form.form[0][0]

        if len(raw_data) <= cls.index:
            return
        raw_data = raw_data[cls.index]
        result = []
        index_element_count = 1
        if raw_data[index_element_count] == 'Дочерние элементы отдельно':
            items = helper.json_read(src_dir, f'{file_name}.{cls.name}{version}.json')
            if items:
                for item in items:
                    result.append(cls.encode(form, item))
                raw_data[index_element_count] = str(len(items))
                raw_data[index_element_count + 1:index_element_count + 1] = result
            else:
                raw_data[index_element_count] = '0'

    @classmethod
    def encode(cls, form, data):
        return data['raw']


class FormParams(_FormRoot):
    name = 'params'
    index = 4
    index_name = 1


class FormProps(_FormRoot):
    name = 'props'
    index = 3
    index_name = 3


class FormCommands(_FormRoot):
    name = 'commands'
    index = 5
    index_name = 2
