from .FormElement import FormElement, FormItemTypes
from ..Form803Elements.FormElement import calc_offset
from .... import helper
from ....ext_exception import ExtException


class Panel(FormElement):
    def __init__(self):
        self.elements_tree = []
        self.pages = []
        self.form = None
        self._elements_tree_index = {}
        self.elements_types_index = {}
        self.auto_include = False
        self.elements_data = {}
        self.props_index = {}
        self.last_elem_id = 1
        self.field_data_source = []

    @staticmethod
    def calc_id(path, page, name):
        id = []
        if path:
            id.append(path)
        if page:
            id.append(page)
        if name:
            id.append(name)
        return '/'.join(id)

    def add_elem(self, page, path, name, elem_data, elem_raw_data):
        def get_page_name():
            if page and self.pages:
                if page != str(int(page)):
                    raise ExtException(message='Не удалось определить номер страницы элемента формы',
                                       detail=f'{path} {name}')
                return self.pages[int(page)]
            return None

        page_name = get_page_name()
        page_id = self.calc_id(path, page_name, None)
        elem_tree = dict(name=elem_data['name'], type=elem_data['type'])
        if self.auto_include:
            elem_id = self.calc_id(path, page_name, name)
            parent = self.elements_tree[self._elements_tree_index[page_id]]
            parent['child'].append(elem_tree)
        else:
            elem_id = self.calc_id(path, None, name)
            elem_tree['page'] = page_name
            self.elements_tree.append(elem_tree)

        self.elements_data[elem_id] = {
            'id': elem_data['id'],
            'ver': 802,
            'page': page_id,
            'raw': elem_raw_data,
        }

        type_index = self.elements_types_index.get(elem_data['id'])
        if type_index:
            self.elements_data[elem_id]['type_index'] = type_index

        if self.form:
            prop = self.form.props_index.get(elem_data['id'])
            if prop:
                self.elements_data[elem_id]['prop'] = prop['name']

        return elem_tree, elem_id

    @classmethod
    def decode(cls, form, path, elem_raw_data):
        try:
            self = cls()
            self.auto_include = form.auto_include
            is_child = 0 if isinstance(elem_raw_data[1], list) else 1
            if is_child:
                self.form = form
                self.form.props_index = form.form.props_index
                elem, elem_id = super().decode(form, path, elem_raw_data)
                new_path = elem_id.replace('includr_', 'include_')
                self.decode_pages(new_path, elem_raw_data[1 + is_child][1])
                self.decode_elements(new_path, elem_raw_data[-1])
                elem['child'] = self.elements_tree
                form.elements_data.update(self.elements_data)
            else:
                self.form = form
                self.decode_pages(path, elem_raw_data[1 + is_child][1])
                self.decode_elements('', elem_raw_data[2])
            return self.elements_tree, self.elements_data
        except Exception as err:
            raise ExtException(parent=err)

    def decode_elements(self, path, raw_data):
        try:
            result = []
            element_count = int(raw_data[0])
            if not element_count:
                return

            for i in range(element_count):
                elem_raw_data = raw_data[i + 1]
                metadata_type_uuid = elem_raw_data[0]
                try:
                    metadata_type_name = FormItemTypes(metadata_type_uuid)
                except ValueError:
                    raise ExtException(
                        message='Неизвестный тип элемента формы',
                        detail=f'{self.__class__.__name__}: {metadata_type_uuid}'
                    )
                try:
                    handler = self.get_class_form_elem(metadata_type_name.name)
                except Exception as err:
                    raise ExtException(
                        parent=err,
                        message='Проблема с парсером элемента формы',
                        detail=f'{metadata_type_name} - {err}'
                    )

                try:
                    res = handler.decode(self, path, elem_raw_data)
                except helper.FuckingBrackets as err:
                    raise err from err
                except Exception as err:
                    raise ExtException(
                        parent=err,
                        detail=f'{metadata_type_name} - {err}',
                        message='Ошибка разбора элемента формы'
                    )

                result.append(res)

            raw_data[0] = 'Дочерние элементы отдельно'
            del raw_data[1:1 + element_count]
            return result
        except Exception as err:
            raise ExtException(parent=err)

    def decode_pages(self, path, raw_data):
        def element_index():
            self.elements_types_index = {}
            type_offset = 2
            for types in range(1, 5):
                type_count = int(raw_data[type_offset])
                for elem in range(type_count):
                    _elem_data = raw_data[type_offset + 1 + elem]
                    _elem_id = _elem_data[1]
                    if _elem_id not in self.elements_types_index:
                        self.elements_types_index[_elem_id] = {}
                    if types not in self.elements_types_index[_elem_id]:
                        self.elements_types_index[_elem_id][types] = []
                    self.elements_types_index[_elem_id][types] += [[_elem_data[0], _elem_data[2]]]
                raw_data[type_offset] = '0'
                del raw_data[type_offset + 1: type_offset + 1 + type_count]
                type_offset += 1

        def decode_info():
            pages_info_offset = pages_offset + 4

            pages_info_count = int(raw_data[pages_info_offset])
            if page_count * 4 != pages_info_count:
                raise NotImplementedError()

            for i in range(page_count):
                offset = i * 4 + 1 + pages_info_offset
                page_info = raw_data[offset: offset + 4]
                elem_id = self.calc_id(path, self.pages[i], None)
                self.elements_data[elem_id]['info'] = page_info

            del raw_data[pages_info_offset + 1: pages_info_offset + 1 + pages_info_count]
            raw_data[pages_info_offset] = 'в отдельном файле'

        pages_offset = self.pages_offset(raw_data)
        try:
            pages_raw_data = raw_data[pages_offset]
            format_version = pages_raw_data[0]
            if format_version != '1':
                print(f'Неизвестный формат страниц. {format_version} != 1')
            page_count = int(pages_raw_data[1])
            self.pages = []
            for i in range(page_count):
                raw_page = pages_raw_data[i + 2]
                page_format_version = raw_page[0]
                # if page_format_version not in ['3', '4']:
                #     print(f'Неизвестный формат страницы. {page_format_version} != 3')
                page_name = helper.str_decode(raw_page[6])
                if self.auto_include:
                    self.elements_tree.append({
                        "name": page_name,
                        "type": "Page",
                        "child": []
                    })
                elem_id = self.calc_id(path, page_name, None)

                self._elements_tree_index[elem_id] = len(self.elements_tree) - 1
                self.pages.append(page_name)

                self.elements_data[elem_id] = {
                    "ver": 802,
                    "page_format_version": page_format_version,
                    "raw": raw_page
                }
            del pages_raw_data[1:1 + 2 + page_count]
            self.elements_data[self.calc_id(path, '-pages-', None)] = self.pages

            decode_info()
            element_index()

        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def encode(cls, form, path, elem_tree, elem_data):
        try:
            self = cls()
            self.form = form
            self.auto_include = form.auto_include
            self.props_index = form.props_index
            elem_raw_data = elem_data['raw']
            is_child = 0 if isinstance(elem_raw_data[1], list) else 1
            if is_child:
                super().encode(form, path, elem_tree, elem_data)
                self.last_elem_id = form.last_elem_id
                path = f"{path}/{elem_tree['name']}" if path else elem_tree['name']
                self.elements_tree = elem_tree['child']
                self.elements_data = form.elements_data
                elem_raw_data[1 + is_child][1] = self.encode_pages(path, elem_raw_data[1 + is_child][1])
                self.encode_elements(path, elem_raw_data[-1])
                elem_raw_data[1 + is_child][1] = self.encode_elements_types(elem_raw_data[1 + is_child][1])
                form.last_elem_id = self.last_elem_id
                pass
                # return elem_raw_data
                # elem['child'] = self.elements_tree
                # form.elements_data.update(self.elements_data)
            else:
                self.elements_tree = form.elements_tree
                self.elements_data = form.elements_data
                elem_raw_data[1 + is_child][1] = self.encode_pages(path, elem_raw_data[1 + is_child][1])
                self.encode_elements('', elem_raw_data[2])
                elem_raw_data[1 + is_child][1] = self.encode_elements_types(elem_raw_data[1 + is_child][1])
                # super().encode(form, path, raw_data)
            form.field_data_source += self.field_data_source
            return elem_raw_data
        except Exception as err:
            raise ExtException(parent=err)

    @staticmethod
    def pages_offset(raw_data):
        try:
            return calc_offset([[2, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [4, 0]], raw_data)
        except Exception as err:
            raise ExtException(message='Не смогли найти описание страниц элементов формы')

    def encode_pages(self, path, raw_data):
        def encode_page(_name):
            elem_id = '/'.join([_path, _name]) if path else _name
            page = self.elements_data[elem_id]
            pages.append(page['raw'])
            return page['info']
        _path = path
        _path = path.replace('includr_', 'include_')
        pages_offset = self.pages_offset(raw_data)
        try:
            pages_raw_data = raw_data[pages_offset]
            format_version = pages_raw_data[0]
            if format_version != '1':
                print(f'Неизвестный формат страниц. {format_version} != 1')
            pages = []
            pages_info = []

            if self.auto_include:
                page_count = len(self.elements_tree)
                pages.append(str(page_count))
                for elem in self.elements_tree:
                    pages_info += encode_page(elem['name'])

            else:
                _pages = self.elements_data[self.calc_id(_path, '-pages-', None)]
                page_count = len(_pages)
                pages.append(str(page_count))
                for name in _pages:
                    pages_info += encode_page(name)

            raw_data[pages_offset] = pages_raw_data[:1] + pages + pages_raw_data[1:]

            pages_info_offset = pages_offset + 4
            raw_data = raw_data[:pages_info_offset + 1] + pages_info + raw_data[pages_info_offset + 1:]
            raw_data[pages_info_offset] = str(page_count * 4)
            return raw_data
        except Exception as err:
            raise ExtException(parent=err)

    def encode_elements_types(self, raw_data):
        try:
            result = []
            for types in range(1, 5):
                type_index = self.elements_types_index[str(types)]
                type_index.sort(key=lambda row: row[1])
                result += [str(len(type_index))]
                if type_index:
                    result += type_index
            raw_data = raw_data[:2] + result + raw_data[6:]
            return raw_data
        except Exception as err:
            raise ExtException(parent=err)

    def encode_element(self, page_id, elem, key, result):
        try:
            try:
                handler = self.get_class_form_elem(elem['type'])
            except Exception as err:
                raise ExtException(
                    parent=err,
                    message='Проблема с парсером элемента формы',
                    detail=f"{elem['type']} - {err}"
                )

            try:
                try:
                    elem_data = self.elements_data[key]
                except KeyError as err:
                    raise ExtException(message='Остутствуют данные элемента формы', detail=key)
                res = handler.encode(self, page_id, elem, elem_data)
            except ExtException as err:
                raise ExtException(
                    parent=err,
                    message='Проблема с парсером элемента формы',
                    detail=f"{elem['type']} - {err}"
                )

            result.append(res)
        except Exception as err:
            raise ExtException(parent=err)

    def encode_elements(self, path, raw_data):

        try:
            _path = path.replace('includr_', 'include_')
            _id = [_path] if _path else []
            self.elements_types_index = {'1': [], '2': [], '3': [], '4': []}
            result = []
            if self.auto_include:
                for i, page in enumerate(self.elements_tree):
                    page_id = '/'.join(_id + [page['name']])
                    if page['child']:
                        for elem in page['child']:
                            key = f"{page_id}/{elem['name']}"
                            self.encode_element(page_id, elem, key, result)
            else:
                for elem in self.elements_tree:
                    page_id = '/'.join(_id)
                    key = f"{_path}/{elem['name']}" if _path else elem['name']
                    self.encode_element(page_id, elem, key, result)

            raw_data[0] = str(len(result))
            raw_data += result
        except Exception as err:
            raise ExtException(parent=err)
