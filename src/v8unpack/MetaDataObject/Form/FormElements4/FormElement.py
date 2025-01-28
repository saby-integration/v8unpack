from enum import Enum

from v8unpack import helper
from v8unpack.ext_exception import ExtException
from v8unpack.helper import calc_offset


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
    def get_prop_link_offset(cls, raw_data):
        return None

    @classmethod
    def set_name(cls, name, raw_data):
        name_offset = cls.get_name_node_offset(raw_data)
        raw_data[name_offset] = helper.str_encode(name)

    @classmethod
    def get_command_link_offset(cls, raw_data):
        return None

    @classmethod
    def decode(cls, form, path, raw_data):
        try:
            name_offset = cls.get_name_node_offset(raw_data)
            name = raw_data[name_offset]
            prop_link_offset = cls.get_prop_link_offset(raw_data)
            prop = ''
            if prop_link_offset is not None:
                prop_link = raw_data[prop_link_offset]
                if prop_link and int(prop_link[0]):
                    prop = []
                    prop_src = form.props_index
                    for i in range(int(prop_link[0])):
                        prop_id = prop_link[i + 1][0]
                        try:
                            prop_name = prop_src[prop_id]['name']
                            prop_src = prop_src[prop_id]['child']
                            prop.append(prop_name)
                        except KeyError:
                            prop = None
                            break
                    if prop:
                        prop = '.'.join(prop)

            command_link_offset = cls.get_command_link_offset(raw_data)
            command = []
            if command_link_offset is not None:
                command_link = raw_data[command_link_offset]
                if command_link and int(command_link[0]):
                    command = form.commands_index.get(command_link[0])

            if not isinstance(name, str) or not name:
                raise ExtException(message='form elem name not string')
            data = dict(raw=raw_data, ver=4)
            if prop:
                data['ПутьКДанным'] = prop
            if command:
                data['ИмяКоманды'] = command
            name = helper.str_decode(name)
            key = f'{path}/{name}' if path else name
            form.elements_data[key] = data
            return dict(
                name=name,
                type=cls.__name__,
            )
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def decode_list(cls, form, raw_data, index_element_count, path=''):
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
                        detail=f'{form.__class__.__name__} {form.header.get("name")} : {metadata_type_uuid}'
                    )
                elem_data = cls.decode_elem(metadata_type.name, form, path, elem_raw_data)
                result.append(elem_data)

            raw_data[index_element_count] = 'Дочерние элементы отдельно'
            del raw_data[index_element_count + 1:index_element_count + 1 + element_count * 2]
            return result
        except helper.FuckingBrackets as err:
            raise err
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def decode_elem(cls, metadata_type_name, form, path, elem_raw_data):
        try:
            handler = cls.get_class_form_elem(metadata_type_name)
        except Exception as err:
            raise ExtException(
                parent=err,
                message='Проблема с парсером элемента формы',
                detail=f'{metadata_type_name} - {err}'
            )
        try:
            return handler.decode(form, path, elem_raw_data)
        except helper.FuckingBrackets as err:
            raise err from err
        except Exception as err:
            raise ExtException(
                parent=err,
                detail=f'{metadata_type_name} - {err}',
                message='Ошибка разбора элемента формы'
            )

    @staticmethod
    def get_class_form_elem(name):
        return helper.get_class(f'v8unpack.MetaDataObject.Form.FormElements4.{name}.{name}')

    @classmethod
    def encode_list(cls, form, items, raw_data, index_element_count, path=''):
        try:
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
                elem_data = handler.encode(form, path, item)
                result.append(metadata_type.value)
                result.append(elem_data)
            raw_data[index_element_count] = str(len(items))
            raw_data[index_element_count + 1:index_element_count + 1] = result

            return result
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def encode(cls, form, path, data):
        try:
            key = f"{path}/{data['name']}" if path else data['name']
            try:
                elem_data = form.elements_data[key]
            except KeyError as err:
                raise ExtException(message='Остутствуют данные элемента формы', detail=err)
            includr_index = key.find('/includr_')
            if includr_index >= 0:
                handler = cls.get_class_form_elem(data['type'])
                name_offset = handler.get_name_node_offset(elem_data['raw'])
                elem_data['raw'][name_offset] = helper.str_encode(data['name'])
                return elem_data['raw']
            include_index = key.find('/include_')
            if include_index >= 0:
                prop = elem_data.get('ПутьКДанным')
                if prop:
                    raw_data = elem_data['raw']
                    prop_link_offset = cls.get_prop_link_offset(raw_data)
                    if prop_link_offset is not None:
                        prop_link = raw_data[prop_link_offset]
                        if prop_link:
                            prop_index = form.props_index.get(prop)
                            if prop_index:
                                count = int(prop_link[0])
                                if count == 1:
                                    prop_link[1] = [prop_index]
                                    pass
                                elif count == 2:
                                    prop_link[1] = [prop_index[0]]
                                    prop_link[2] = [prop_index[1]]
                                    pass
                                elif count == 0:
                                    pass
                                else:
                                    raise NotImplementedError()
                            else:
                                raise ExtException(message='Нет свойства', detail=f'{prop} форма {form.form.name}')
                    pass

                command = elem_data.get('ИмяКоманды')
                if command:
                    raw_data = elem_data['raw']
                    command_link_offset = cls.get_command_link_offset(raw_data)
                    if command_link_offset:
                        command_link = raw_data[command_link_offset]
                        if command_link:
                            command_index = form.commands_index.get(command)
                            if command_index:
                                raw_data[command_link_offset] = command_index
                            else:
                                raise ExtException(message='Нет команды', detail=f'{command} форма {form.form.name}')
                    pass
                return elem_data['raw']

            return elem_data['raw']
        except Exception as err:
            raise ExtException(parent=err)


class _FormRoot:
    element_node_offset = [[2, 1], [3, 1], [4, 1]]
    name = ''
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
    def encode_list(cls, form, src_dir, file_name, version, raw_data):
        if len(raw_data) <= cls.index:
            return
        raw_data = raw_data[cls.index]
        result = []
        index_element_count = 1
        if raw_data[index_element_count] == 'Дочерние элементы отдельно':
            items = getattr(form.form, cls.name)  # helper.json_read(src_dir, f'{file_name}.{cls.name}{version}.json')
            if items:
                for item in items:
                    result.append(cls.encode(form, item))
                raw_data[index_element_count] = str(len(items))
                raw_data[index_element_count + 1:index_element_count + 1] = result
            else:
                raw_data[index_element_count] = '0'
            return items

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
    child_offset = 13

    @classmethod
    def decode(cls, raw_data):
        result = dict(
            name=helper.str_decode(raw_data[cls.index_name]),
            id=raw_data[1][0],
            raw=raw_data
        )
        child_count = int(raw_data[cls.child_offset])
        if child_count:
            result['child'] = []
            for i in range(child_count):
                child = raw_data[cls.child_offset + i + 1]
                result['child'].append(cls.decode_child(child))
            raw_data[cls.child_offset] = "отдельно"
            del raw_data[cls.child_offset + 1:cls.child_offset + 1 + child_count]

        return result

    @classmethod
    def decode_child(cls, raw_data):
        return dict(
            name=helper.str_decode(raw_data[cls.index_name]),
            id=raw_data[1],
            raw=raw_data
        )

    @classmethod
    def encode(cls, form, data):
        raw_data = data['raw']
        if data.get('child'):
            child_count = len(data['child'])
            raw_data[cls.child_offset] = str(child_count)
            childs = []
            for i in range(child_count):
                child = data['child'][i]
                childs.append(child['raw'])
            raw_data[cls.child_offset + 1: cls.child_offset + 1] = childs
        return raw_data


class FormCommands(_FormRoot):
    name = 'commands'
    index = 5
    index_name = 2

    @classmethod
    def decode(cls, raw_data):
        result = dict(
            name=helper.str_decode(raw_data[cls.index_name]),
            id=raw_data[1][0],
            raw=raw_data
        )
        return result
