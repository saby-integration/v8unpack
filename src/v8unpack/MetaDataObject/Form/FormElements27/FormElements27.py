from .FormElement import FormProps
from .Panel import Panel
from v8unpack import helper
from v8unpack.ext_exception import ExtException


class FormElements27:
    FormProps = FormProps
    Panel = Panel

    def __init__(self, form):
        self.form = form
        self.props_index = {}
        self.last_elem_id = 1
        self.field_data_source = []

    @property
    def options(self):
        return self.form.options

    @property
    def auto_include(self):
        if self.form.options:
            return self.form.options.get('auto_include')
        return False

    @property
    def elements_data(self):
        return self.form.elements_data

    @property
    def elements_tree(self):
        return self.form.elements_tree

    def decode(self, src_dir, dest_dir, dest_path, raw_data):
        try:
            self.form.props = self.FormProps.decode_list(self.form, raw_data[2][2])
            self.form.elements_tree, self.form.elements_data = self.decode_elements(raw_data)
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

            elements_tree, elements_data, elements_id = self.Panel.decode(self, '', form_data[1][2])
            return elements_tree, elements_data
        except Exception as err:
            raise ExtException(parent=err)

    def create_prop_index_by_elem_id(self, raw_data):
        try:
            self.props_index = {}
            _props = {}
            if not self.form.props:
                return
            for prop in self.form.props:
                _props[prop['id']] = prop

            element_count = int(raw_data[0])
            if not element_count:
                return

            for i in range(element_count):
                elem_raw_data = raw_data[i + 1]
                elem_id = elem_raw_data[0]
                # if elem_raw_data[1][0] == '1':
                prop_id = elem_raw_data[1][1][0]
                try:
                    self.props_index[elem_id] = {'name': _props[prop_id]['name'], 'index': elem_raw_data[1]}
                except KeyError:
                    pass
                # else:
                #     raise NotImplementedError('prop index  > 1')
        except Exception as err:
            raise ExtException(parent=err)

    def create_prop_index_by_name(self):
        try:
            self.props_index = {}
            if self.form.props:
                for prop in self.form.props:
                    self.props_index[prop['name']] = prop['id']
        except Exception as err:
            raise ExtException(parent=err)

    def fill_datasource(self, raw_data):
        raw_data.append(str(len(self.field_data_source)))
        for elem_id, prop_id in self.field_data_source:
            raw_data.append(
                [str(elem_id), ['1', [str(prop_id)]]]
            )

    def encode(self, src_dir, file_name, version, raw_data, path=''):
        try:
            # index_element_count = 0
            # if raw_data[index_element_count] == 'Дочерние элементы отдельно':
            # elements = helper.json_read(src_dir, f'{file_name}.elements802.json')
            elements = helper.json_read(src_dir, f'{file_name}.elem.json')
            self.form.props = elements['props']
            self.form.elements_data = elements['data']
            self.form.elements_tree = elements['tree']
            self.FormProps.encode_list(self.form, raw_data[2][2])
            self.create_prop_index_by_name()
            self.Panel.encode(self, '', None, dict(raw=raw_data[1][2]))
            if self.auto_include:
                raw_data[2][3] = []
                self.fill_datasource(raw_data[2][3])
            return raw_data
        except Exception as err:
            raise ExtException(parent=err)
