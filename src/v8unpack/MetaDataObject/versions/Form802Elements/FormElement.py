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
    Indicator = 'b1db1f86-abbb-4cf0-8852-fe6ae21650c2'
    CalendarBox = 'e3c063d8-ef92-41be-9c89-b70290b5368b'
    TrackBar = '6c06cd5d-8481-4b6f-a90a-7a97a8bb8bef'
    TextDocumentField = '14c4a229-bfc3-42fe-9ce1-2da049fd0109'
    GraphicalSchemaField = '42248403-7748-49da-b782-e4438fd7bff3'
    GeographicalSchemaField = 'ad37194e-555e-4305-b718-5dca84baf145'
    Chart = 'a8b97779-1a4b-4059-b09c-807f86d2a461'
    GanttChart = 'e5fdc112-5c84-4a16-9728-72b85692b6e2'
    PivotChart = 'a26da99e-184a-4823-b0d6-62816d38dc4e'
    Dendrogram = '984981b1-622d-4ebc-94f7-885f0cdfb59a'


class FormElement:
    name = 'elements'

    @classmethod
    def get_class_form_elem(cls, name):
        index = ['Panel']
        if name in index:
            return helper.get_class(f'v8unpack.MetaDataObject.versions.Form802Elements.{name}.{name}')
        else:
            return FormElement

    @classmethod
    def decode(cls, form, path, elem_raw_data):
        metadata_type_uuid = elem_raw_data[0]
        name = helper.str_decode(elem_raw_data[-2][1])
        try:
            metadata_type = FormItemTypes(metadata_type_uuid)
        except ValueError:
            raise ExtException(
                message='Неизвестный тип элемента формы',
                detail=f'{metadata_type_uuid} {name} - {form.__class__.__name__} {form.header["name"]}',
                action='Form802Element.decode'
            )
        page = elem_raw_data[-3][-5]
        elem_data = dict(
            name=name,
            type=metadata_type.name,
            ver=802
        )
        return form.add_elem(page, path, name, elem_data, elem_raw_data)

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
    def encode_list(cls, form, src_dir, file_name, version, raw_data, path=''):
        try:
            result = []
            index_element_count = 0
            if raw_data[index_element_count] == 'Дочерние элементы отдельно':
                elements = helper.json_read(src_dir, f'{file_name}.elements_tree{version}.json')
                items = elements['tree']
                form.elements_data = elements['data']
                if items:
                    for item in items:
                        result.append(cls.encode(form, path, item))
                    raw_data[index_element_count] = str(len(items))
                    raw_data[index_element_count + 1:index_element_count + 1] = result
                else:
                    raw_data[index_element_count] = '0'
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def encode(cls, form, path, data):
        key = f"{path}/{data['name']}"
        try:
            return form.elements_data[key]
        except KeyError as err:
            # detail = err
            # if key.startswith('/includr_'):
            #     try:
            #         key = f'/include_{key[9:]}'
            #         elem_data = form.elements_data[key]
            #         elem_data[-2][1] = helper.str_encode(data['name'])
            #         return elem_data
            #     except KeyError as err:
            #         detail = err
            raise ExtException(message='Остутствуют данные элемента формы', detail=detail)


class FormProps(FormElement):
    name = 'props'

    @classmethod
    def decode(cls, form, path, elem_raw_data):
        elem_data = dict(
            name=helper.str_decode(elem_raw_data[4]),
            raw=elem_raw_data
        )
        return elem_data

    @classmethod
    def encode(cls, form, path, data):
        return data['raw']

    @classmethod
    def encode_list(cls, form, src_dir, file_name, version, raw_data, path=''):
        result = []
        index_element_count = 0
        if raw_data[index_element_count] == 'Дочерние элементы отдельно':
            items = helper.json_read(src_dir, f'{file_name}.{cls.name}{version}.json')
            if items:
                for item in items:
                    result.append(cls.encode(form, path, item))
                raw_data[index_element_count] = str(len(items))
                raw_data[index_element_count + 1:index_element_count + 1] = result
            else:
                raw_data[index_element_count] = '0'
