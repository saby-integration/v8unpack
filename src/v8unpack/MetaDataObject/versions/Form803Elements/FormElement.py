from enum import Enum

from .... import helper
from ....ext_exception import ExtException


class FormItemTypes(Enum):
    FormField = '77ffcc29-7f2d-4223-b22f-19666e7250ba'
    FormButton = 'a9f3b1ac-f51b-431e-b102-55a69acdecad'
    FormDecoration = '3d3cb80c-508b-41fa-8a18-680cdf5f1712'
    FormGroup = 'cd5394d0-7dda-4b56-8927-93ccbe967a01'
    FormTable = '143c00f7-a42d-4cd7-9189-88e4467dc768'
    FormItemAddition = 'c5259a1d-518a-4afd-b98d-0176027e4feb'


class FormElement:
    @classmethod
    def decode_header(cls, raw_data):
        return dict(
            name=raw_data[7],
            type=cls.__name__,
            raw=raw_data
        )

    @classmethod
    def decode(cls, form, raw_data):
        data = cls.decode_header(raw_data)
        return data

    @classmethod
    def encode(cls, form, data):
        return data['raw']

    @classmethod
    def decode_list(cls, form, raw_data, index_element_count):
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
                    detail=f'Форма {form.__class__.__name__} {form.header["name"]} : {metadata_type_uuid}'
                )
            try:
                handler = cls.get_class_form_elem(metadata_type.name)
            except Exception as err:
                raise ExtException(
                    message='Проблема с парсером элемента формы',
                    detail=f'{metadata_type.name} - {err}'
                )
            elem_data = handler.decode(form, elem_raw_data)
            result.append(elem_data)

        raw_data[index_element_count] = 'Дочерние элементы отдельно'
        del raw_data[index_element_count + 1:index_element_count + 1 + element_count * 2]
        return result

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
                    detail=f'Форма {form.__class__.__name__} {form.header["name"]} : {item["type"]}'
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
        if len(raw_data) < cls.index:
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
        del items[index_element_count + 1:index_element_count + 1 + element_count ]
        return result

    @classmethod
    def encode_list(cls, form, src_dir, file_name, version):
        raw_data = form.form[0][0]

        if len(raw_data) < cls.index:
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
