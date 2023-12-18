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
        self.elements_data = {}
        self.props_index = None

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
        elem_id = self.calc_id(path, page_name, name)
        page_id = self.calc_id(path, page_name, None)
        parent = self.elements_tree[self._elements_tree_index[page_id]]
        parent['child'].append(elem_data)

        self.elements_data[elem_id] = {
            'raw': elem_raw_data,
            'id': elem_id,
        }
        if self.form:
            prop = self.form.props_index.get(elem_data['id'])
            if prop:
                self.elements_data[elem_id]['prop'] = prop['name']

        return parent['child'][-1], elem_id

    @classmethod
    def decode(cls, form, path, elem_raw_data):
        try:
            self = cls()
            is_child = 0 if isinstance(elem_raw_data[1], list) else 1
            if is_child:
                self.form = form
                self.form.props_index = form.form.props_index
                elem, elem_id = super().decode(form, path, elem_raw_data)
                self.decode_pages(elem_id, elem_raw_data[1 + is_child][1])
                self.decode_elements(elem_id, elem_raw_data[-1])
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
                if page_format_version not in ['3', '4']:
                    print(f'Неизвестный формат страницы. {page_format_version} != 3')
                page_name = helper.str_decode(raw_page[6])

                self.elements_tree.append({
                    "name": page_name,
                    "type": "Page",
                    "child": []
                })
                elem_id = self.calc_id(path, page_name, None)

                self._elements_tree_index[elem_id] = len(self.elements_tree) - 1
                self.pages.append(page_name)

                self.elements_data[elem_id] = {
                    "version": page_format_version,
                    "raw": raw_page
                }

            del pages_raw_data[1:1 + 2 + page_count]
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def encode(cls, form, path, elem_tree, elem_raw_data):
        try:
            self = cls()
            is_child = 0 if isinstance(elem_raw_data[1], list) else 1
            if is_child:
                super().encode(form, path, elem_tree, elem_raw_data)
                path = f"{path}/{elem_tree['name']}"
                self.elements_tree = elem_tree['child']
                self.elements_data = form.elements_data
                self.encode_pages(path, elem_raw_data[1 + is_child][1])
                self.encode_elements(path, elem_raw_data[-1])
                return elem_raw_data
                # elem['child'] = self.elements_tree
                # form.elements_data.update(self.elements_data)
            else:
                self.elements_tree = form.elements_tree
                self.elements_data = form.elements_data
                self.encode_pages(path, elem_raw_data[1 + is_child][1])
                self.encode_elements('', elem_raw_data[2])
                # super().encode(form, path, raw_data)
        except Exception as err:
            raise ExtException(parent=err)

    @staticmethod
    def pages_offset(raw_data):
        try:
            return calc_offset([[2, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [4, 0]], raw_data)
        except Exception as err:
            raise ExtException(message='Не смогли найти описание страниц элементов формы')

    def encode_pages(self, path, raw_data):
        pages_offset = self.pages_offset(raw_data)
        try:
            pages_raw_data = raw_data[pages_offset]
            format_version = pages_raw_data[0]
            if format_version != '1':
                print(f'Неизвестный формат страниц. {format_version} != 1')
            pages = []
            pages.append(str(len(self.elements_tree)))
            # self.pages = []
            for elem in self.elements_tree:
                name = elem['name']
                elem_id = '/'.join([path, name]) if path else name
                page = self.elements_data[elem_id]
                pages.append(page['raw'])
            raw_data[pages_offset] = pages_raw_data[:1] + pages + pages_raw_data[1:]
        except Exception as err:
            raise ExtException(parent=err)

    def encode_elements(self, path, raw_data):
        try:
            _id = [path] if path else []
            result = []
            for i, page in enumerate(self.elements_tree):
                page_id = '/'.join(_id + [page['name']])
                if page['child']:
                    for elem in page['child']:
                        # elem_id = '/'.join(page_id + [elem['name']])
                        # elem_data = self.elements_data[elem_id]
                        try:
                            handler = self.get_class_form_elem(elem['type'])
                        except Exception as err:
                            raise ExtException(
                                parent=err,
                                message='Проблема с парсером элемента формы',
                                detail=f"{elem['type']} - {err}"
                            )

                        try:
                            key = f"{page_id}/{elem['name']}"
                            try:
                                elem_raw_data = self.elements_data[key]['raw']
                            except KeyError as err:
                                raise ExtException(message='Остутствуют данные элемента формы', detail=key)
                            res = handler.encode(self, page_id, elem, elem_raw_data)
                        except ExtException as err:
                            raise ExtException(
                                parent=err,
                                message='Проблема с парсером элемента формы',
                                detail=f"{elem['type']} - {err}"
                            )

                        result.append(res)

            raw_data[0] = str(len(result))
            raw_data += result
        except Exception as err:
            raise ExtException(parent=err)
