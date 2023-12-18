from .FormElement import FormProps
from .Panel import Panel
from .... import helper
from ....ext_exception import ExtException


class Form27:
    version = '802'

    def __init__(self, form):
        self.form = form
        self.props_index = None

    def decode(self, raw_data):
        try:
            self.form.props = FormProps.decode_list(self.form, raw_data[2][2])
            self.form.elements_tree, self.form.elements_data = self.decode_elements(raw_data)
            a = 1
        except Exception as err:
            raise ExtException(parent=err)

    def decode_elements(self, form_data):
        try:
            meta_type = form_data[1][2][0]
            if meta_type != '09ccdc77-ea1a-4a6d-ab1c-3435eada2433':
                raise ExtException(message=f"Неизвестный формат элементов формы",
                                   detail=f"Новый тип элементов формы {meta_type}, "
                                          f"просьба передать файл формы {self.form.header.get('name')} разработчикам")
            self.create_prop_index_by_elem_id(form_data[2][3])

            elements_tree, elements_data = Panel.decode(self, '', form_data[1][2])
            form_version = form_data[1][10]
            element_count_all = form_data[1][1][
                1]  # хз что это, +3 к количеству элементов (может дополнительно количество панелей по количеству страниц плюсуется
            element_count_by_pages = form_data[2][1]  # дальше идут пачками по типам
            return elements_tree, elements_data
        except Exception as err:
            raise ExtException(parent=err)

    def create_prop_index_by_elem_id(self, raw_data):
        self.props_index = {}
        _props = {}
        for prop in self.form.props:
            _props[prop['id']] = prop

        element_count = int(raw_data[0])
        if not element_count:
            return

        for i in range(element_count):
            elem_raw_data = raw_data[i + 1]
            elem_id = elem_raw_data[0]
            if elem_raw_data[1][0] == '1':
                prop_id = elem_raw_data[1][1][0]
                self.props_index[elem_id] = {'name': _props[prop_id]['name'], 'index': elem_raw_data[1]}
            else:
                raise NotImplementedError('prop index  > 1')

    def create_prop_index_by_name(self):
        self.props_index = {}
        if self.form.props:
            for prop in self.form.props:
                self.props_index[prop['name']] = prop['id']
                childs = prop.get('child', [])
                for child in childs:
                    self.props_index[f"{prop['name']}.{child['name']}"] = prop['id'], child['id']

    @classmethod
    def encode(cls, form, src_dir, file_name, version, raw_data, path=''):
        try:
            # index_element_count = 0
            # if raw_data[index_element_count] == 'Дочерние элементы отдельно':
            elements = helper.json_read(src_dir, f'{file_name}.elements802.json')
            form.props = elements['props']
            form.elements_data = elements['data']
            form.elements_tree = elements['tree']
            FormProps.encode_list(form, raw_data[2][2])
            result = Panel.encode(form, '', None, raw_data[1][2])
            return result
        except Exception as err:
            raise ExtException(parent=err)
