from .FormElement import FormElement, FormItemTypes
from ..Form803Elements.FormElement import calc_offset
from .... import helper
from ....ext_exception import ExtException


class Panel(FormElement):
    def __init__(self):
        self.elements_tree = []
        self.pages = []
        self._elements_tree_index = {}
        self.elements_data = {}

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
        self.elements_data[elem_id] = elem_raw_data
        return parent['child'][-1], elem_id

    @classmethod
    def decode(cls, form, path, elem_raw_data):
        try:
            self = cls()
            tree = {}
            root = 0 if isinstance(elem_raw_data[1], list) else 1
            if root:
                elem, elem_id = super().decode(form, path, elem_raw_data)
                self.decode_pages(elem_id, elem_raw_data[1 + root][1])
                self.decode_elements(elem_id, elem_raw_data[-1])
                elem['child'] = self.elements_tree
                form.elements_data.update(self.elements_data)
            else:
                self.decode_pages(path, elem_raw_data[1 + root][1])
                self.decode_elements('', elem_raw_data[2])
            return self.elements_tree, self.elements_data
        except Exception as err:
            pass

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
        try:
            pages_offset = calc_offset([[3, 1], [1, 1], [1, 1], [1, 1], [1, 1], [3, 0]], raw_data)
        except Exception as err:
            raise ExtException(message='Не смогли найти описание страниц элементов формы')
        if raw_data[pages_offset] != '1':
            raise ExtException(message=f"Неизвестный формат элементов формы",
                               detail=f"Количество элементов описывающих страницы не равно 1 "
                                      f"({raw_data[pages_offset]}) ")
        try:
            pages_raw_data = raw_data[pages_offset + 1]
            format_version = pages_raw_data[0]
            if format_version != '1':
                print(f'Неизвестный формат страниц. {format_version} != 1')
            page_count = int(pages_raw_data[1])
            self.pages = []
            for i in range(page_count):
                raw_page = pages_raw_data[i + 2]
                page_format_version = raw_page[0]
                if page_format_version != '3':
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

            del pages_raw_data[2:2 + page_count]
        except Exception as err:
            raise ExtException(parent=err)
