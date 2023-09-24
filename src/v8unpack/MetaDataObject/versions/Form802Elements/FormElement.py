from enum import Enum

from .... import helper
from ....ext_exception import ExtException


class FormItemTypes(Enum):
    Field = '381ed624-9217-4e63-85db-c4c3cb87daae'
    CheckBox = '35af3d93-d7c7-4a2e-a8eb-bac87a1a3f26'
    RadioBtn = '782e569a-79a7-4a4f-a936-b48d013936ec'
    SelectField = '64483e7f-3833-48e2-8c75-2c31aac49f6e'
    CommandPanel = 'e69bf21d-97b2-4f37-86db-675aea9ec2cb'
    Button = '6ff79819-710e-4145-97cd-1618da79e3e2'
    Image = '151ef23e-6bb2-4681-83d0-35bc2217230c'
    Group = '90db814a-c75f-4b54-bc96-df62e554d67d'
    Table = 'ea83fe3a-ac3c-4cce-8045-3dddf35b28b1'
    TableField = '236a17b3-7f44-46d9-a907-75f9cdc61ab5'
    Panel = '09ccdc77-ea1a-4a6d-ab1c-3435eada2433'
    Label = '0fc7e20d-f241-460c-bdf4-5ad88e5474a5'
    ListField = '19f8b798-314e-4b4e-8121-905b2a7a03f5'
    Separator = '36e52348-5d60-4770-8e89-a16ed50a2006'
    FieldHtml = 'd92a805c-98ae-4750-9158-d9ce7cec2f20'


class FormElement:
    name = 'elements'

    @classmethod
    def decode_list(cls, form, raw_data, index_element_count=0):
        result = []
        element_count = int(raw_data[index_element_count])
        if not element_count:
            return

        for i in range(element_count):
            elem_raw_data = raw_data[index_element_count + i + 1]
            result.append(cls.decode(form, elem_raw_data))

        raw_data[index_element_count] = 'Дочерние элементы отдельно'
        del raw_data[index_element_count + 1:index_element_count + 1 + element_count]
        return result

    @classmethod
    def decode(cls, form, elem_raw_data):
        metadata_type_uuid = elem_raw_data[0]
        name = helper.str_decode(elem_raw_data[4][1])
        try:
            metadata_type = FormItemTypes(metadata_type_uuid)
        except ValueError:
            raise ExtException(
                message='Неизвестный тип элемента формы',
                detail=f'{metadata_type_uuid} {name} - {form.__class__.__name__} {form.header["name"]}',
                action='Form802Element.decode'
            )
        elem_data = dict(
            name=name,
            type=metadata_type.name,
            raw=elem_raw_data
        )
        return elem_data

    @classmethod
    def encode_list(cls, form, src_dir, file_name, version, raw_data):
        result = []
        index_element_count = 0
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


class FormProps(FormElement):
    name = 'props'

    @classmethod
    def decode(cls, form, elem_raw_data):
        elem_data = dict(
            name=helper.str_decode(elem_raw_data[4]),
            raw=elem_raw_data
        )
        return elem_data
