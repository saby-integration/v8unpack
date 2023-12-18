from .FormElement import FormProps, FormParams, FormCommands, calc_offset, FormElement
from ... import helper
from ....ext_exception import ExtException


class Form4:
    version = '803'

    def __init__(self, form):
        self.form = form
        self.props_index = None
        self.commands_index = None

    @property
    def elements_data(self):
        return self.form.elements_data

    @property
    def elements_tree(self):
        return self.form.elements_tree

    def decode(self, src_dir, dest_dir, dest_path, raw_data):
        try:
            self.form.props = FormProps.decode_list(self, raw_data)
            self.form.commands = FormCommands.decode_list(self, raw_data)
            self.decode_elements(raw_data)
            self.form.params = FormParams.decode_list(self, raw_data)
        except Exception as err:
            raise ExtException(parent=err)

    def create_prop_index_by_id(self):
        self.props_index = {}
        if self.form.props:
            for prop in self.form.props:
                self.props_index[prop['id']] = {'name': prop['name'], 'child': {}}
                childs = prop.get('child', [])
                for child in childs:
                    self.props_index[prop['id']]['child'][child['id']] = {'name': child['name'], 'child': {}}

    def create_commands_index_by_id(self):
        self.commands_index = {}
        if self.form.commands:
            for command in self.form.commands:
                self.commands_index[command['id']] = command['name']

    def create_prop_index_by_name(self):
        self.props_index = {}
        if self.form.props:
            for prop in self.form.props:
                self.props_index[prop['name']] = prop['id']
                childs = prop.get('child', [])
                for child in childs:
                    self.props_index[f"{prop['name']}.{child['name']}"] = prop['id'], child['id']

    def create_commands_index_by_name(self):
        self.commands_index = {}
        if self.form.commands:
            for command in self.form.commands:
                self.commands_index[command['name']] = command['raw'][1]

    def decode_elements(self, raw_data):
        try:
            index = self.get_form_elem_index(raw_data)
            root_data = raw_data[1]
            self.create_prop_index_by_id()
            self.create_commands_index_by_id()
            # index_panel_count = index[1]
            # form_panels_count = int(root_data[index_panel_count])
            # if form_panels_count:
            #     self.command_panels = [root_data[index_panel_count + 1]]
            #     root_data[index_panel_count] = 'В отдельном файле'
            #     del root_data[index_panel_count + 1]

            index_root_element_count = index[0]
            form_items_count = int(root_data[index_root_element_count])
            if form_items_count:
                self.form.elements_tree = FormElement.decode_list(self, root_data, index_root_element_count)
                self.form.elements_data = dict(sorted(self.form.elements_data.items()))
            pass
        except Exception as err:
            raise ExtException(parent=err)

    def get_form_elem_index(self, raw_data):
        try:
            root_data = raw_data[1]
            index_command_panel_count = calc_offset([(18, 2), (3, 0)], root_data)
            command_panel_count = int(root_data[index_command_panel_count])
            index_root_elem_count = index_command_panel_count + command_panel_count + 1
            return index_root_elem_count, index_command_panel_count
        except Exception as err:
            raise ExtException(
                message='случай требующий анализа, предоставьте образец формы разработчикам',
                detail=f'{self.form.name}, {err}')

    def encode(self, src_dir, file_name, dest_dir, raw_data):
        try:
            elements = helper.json_read(src_dir, f'{file_name}.elements{self.version}.json')
            try:
                self.form.elements_tree = elements.get('tree')
                self.form.elements_data = elements.get('data')
                self.form.props = elements.get('props')
                self.form.params = elements.get('params')
                self.form.commands = elements.get('commands')
            except (KeyError, TypeError):
                raise ExtException(message='Форма разобрана старым сборщиком (<0.16), разберите её новым сборщиком',
                                   action='Form803.encode_elements')

            self.form.commands = FormCommands.encode_list(self, src_dir, file_name, self.version, raw_data)
            self.form.props = FormProps.encode_list(self, src_dir, file_name, self.version, raw_data)

            self.create_prop_index_by_name()
            self.create_commands_index_by_name()

            self.encode_elements(src_dir, file_name, dest_dir, raw_data)
            FormParams.encode_list(self, src_dir, file_name, self.version, raw_data)
        except Exception as err:
            raise ExtException(parent=err)

    def encode_elements(self, src_dir, file_name, dest_dir, raw_data):
        try:
            index = self.get_form_elem_index(raw_data)
            root_data = raw_data[1]

            # index_panel_count = index[1]
            # form_panels_count = int(root_data[index_panel_count])
            # if form_panels_count == 'В отдельном файле':
            #     self.command_panels = helper.json_read(src_dir, f'{file_name}.panels{version}.json')

            index_root_element_count = index[0]
            if root_data[index_root_element_count] == 'Дочерние элементы отдельно':
                # root_data[index_root_element_count] = str(len(self.elements_tree))
                FormElement.encode_list(self, self.form.elements_tree, root_data, index_root_element_count)
        except Exception as err:
            raise ExtException(parent=err)
