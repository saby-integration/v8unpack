from .FormElement import FormElement, FormItemTypes
from v8unpack.helper import calc_offset
from v8unpack import helper
from v8unpack.ext_exception import ExtException


class Panel(FormElement):
    ver = 27

    def __init__(self):
        super().__init__()
        self.elements_tree = []
        self.pages = []
        self.form = None
        self._elements_tree_index = {}
        self.elements_index = {}
        self.anchor_index = [[], [], [], []]
        self.auto_include = False
        self.elements_data = {}
        self.props_index = {}
        self.last_elem_id = 1
        self.field_data_source = []

    @staticmethod
    def calc_id(path, page, name=None):
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

        try:
            page_name = get_page_name()
            page_id = self.calc_id(path, page_name, None)
            elem_tree = dict(name=elem_data['name'], type=elem_data['type'])
            if self.auto_include:
                elem_id = self.calc_id(path, page_name, name)
                parent = self.elements_tree[self._elements_tree_index[page_id]]
                parent['child'].append(elem_tree)
            else:
                elem_id = self.calc_id(path, page_name, name)
                elem_tree['page'] = page_name
                self.elements_tree.append(elem_tree)

            self.elements_index[elem_data['id']] = elem_id

            self.elements_data[elem_id] = {
                'id': elem_data['id'],
                'ver': self.ver,
                'page': page_id,
                'raw': elem_raw_data,
            }

            # anchored = self.anchored.get(elem_data['id'])
            # if anchored:
            #     self.elements_data[elem_id]['anchored'] = anchored

            if self.form:
                prop = self.form.props_index.get(elem_data['id'])
                if prop:
                    self.elements_data[elem_id]['prop'] = prop['name']

            return elem_tree, None, elem_id
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def decode(cls, form, path, elem_raw_data):
        try:
            self = cls()
            self.auto_include = form.auto_include
            is_child = 0 if isinstance(elem_raw_data[1], list) else 1
            elem_id = None
            if is_child:
                self.form = form
                self.form.props_index = form.form.props_index
                elem, elem_data, elem_id = super().decode(form, path, elem_raw_data)
                new_path = elem_id.replace('includr_', 'include_')
                self.decode_pages(new_path, elem_raw_data[1 + is_child][1])
                self.decode_elements(new_path, elem_raw_data[-1])
                elem['child'] = self.elements_tree
                form.elements_data.update(self.elements_data)
            else:
                self.form = form
                self.decode_pages(path, elem_raw_data[1 + is_child][1])
                self.decode_elements('', elem_raw_data[2])
            return self.elements_tree, self.elements_data, elem_id
        except Exception as err:
            raise ExtException(parent=err)

    def decode_elements(self, path, raw_data):
        try:
            # result = []
            element_count = int(raw_data[0])
            if not element_count:
                return
            panel_elements = []
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
                    elem_tree, elem_data, elem_id = handler.decode(self, path, elem_raw_data)
                    panel_elements.append(elem_id)
                except helper.FuckingBrackets as err:
                    raise err from err
                except Exception as err:
                    raise ExtException(
                        parent=err,
                        detail=f'{metadata_type_name} - {err}',
                        message='Ошибка разбора элемента формы'
                    )

                # result.append(res)
            raw_data[0] = 'Дочерние элементы отдельно'
            del raw_data[1:1 + element_count]

            if self.auto_include:
                # меняем ид элеменетов на названия полей
                for elem in panel_elements:
                    data = self.elements_data[elem]
                    try:
                        elem_id = data['id']
                    except (KeyError, TypeError):
                        continue
                    self.anchored_elem_id_to_elem_name(data['raw'][-3], path, elem)
                pass

        # записываем привязки по элементам
        # for elem in self.elements_data:
        #     data = self.elements_data[elem]
        #     try:
        #         elem_id = data['id']
        #     except:
        #         continue
        #     if elem_id in self.anchored:
        #         for anchor in self.anchored[elem_id]:
        #             if anchor['anchor'] in self.elements_index:
        #                 # меняем идентификаторы на имена полей
        #                 anchor['anchor'] = self.elements_index[anchor['anchor']]
        #         data['anchored'] = self.anchored[elem_id]

        # return result
        except Exception as err:
            raise ExtException(parent=err)

    def anchored_elem_id_to_elem_name(self, elem_raw_data, path, current_elem):
        try:
            offset = 6
            # к чему привязан этот элемент
            for anchor_border in range(6):
                for j in range(1, 3):
                    elem_id = elem_raw_data[offset][j][1]
                    if int(elem_id) > 0:
                        try:
                            elem_raw_data[offset][j][1] = self.elements_index[elem_id][
                                                          len(path):]  # нужно имя относительно панели
                        except KeyError:  # если такого индекса нет, то это сам элемент - но это не точно
                            elem_raw_data[offset][j][1] = current_elem[len(path):]
                offset += 1
            # кто привязан к этому элементу
            for anchor_border in range(4):
                count_anchor = int(elem_raw_data[offset])
                for j in range(count_anchor):
                    offset += 1
                    anchor_data = elem_raw_data[offset]
                    elem_id = anchor_data[1]
                    if int(elem_id) > 0:
                        try:
                            elem_name = self.elements_index[elem_id][len(path):]
                            anchor_data[1] = elem_name
                        except KeyError:
                            pass  # ошибка, привязан элемент с другой страницы - в интерфейсе такой возможности нет

                # elem_raw_data[offset] = '0'
                # del elem_raw_data[offset + 1: offset + 1 + count_anchor]
                offset += 1
        except Exception as err:
            raise ExtException(parent=err)
        pass

    def decode_pages(self, path, raw_data):
        # def decode_anchored():
        #     self.anchored = {}
        #     type_offset = 2
        #     for border in range(1, 5):
        #         # anchored_elements = {}
        #         # self.anchored.append(anchored_elements)
        #         type_count = int(raw_data[type_offset])
        #         for elem in range(type_count):
        #             _elem_data = raw_data[type_offset + 1 + elem]
        #             self.add_anchor('$Panel', border, _elem_data)
        #             # _elem_id = _elem_data[1]
        #             #
        #             # if _elem_id not in self.anchored:
        #             #     self.anchored[_elem_id] = {}
        #             # if border not in self.anchored[_elem_id]:
        #             #     self.anchored[_elem_id][border] = []
        #             # self.anchored[_elem_id][border] += [['Panel', _elem_data[0], _elem_data[2]]]
        #         raw_data[type_offset] = '0'
        #         del raw_data[type_offset + 1: type_offset + 1 + type_count]
        #         type_offset += 1
        def delete_anchored():
            type_offset = 2
            for border in range(4):
                type_count = int(raw_data[type_offset])
                raw_data[type_offset] = '0'
                del raw_data[type_offset + 1: type_offset + 1 + type_count]
                type_offset += 1

        def decode_info():
            pages_info_offset = pages_offset + 4

            pages_info_count = int(raw_data[pages_info_offset])
            extra_page_info_count = pages_info_count - page_count * 4  # хрен его знает что это, но встречается большее количество записей
            # if page_count * 4 != pages_info_count:
            #     raise NotImplementedError()

            for i in range(page_count):
                offset = i * 4 + 1 + pages_info_offset
                if i == 0:
                    offset = 1 + pages_info_offset
                    page_info = raw_data[offset: offset + 4 + extra_page_info_count]
                else:
                    offset = i * 4 + 1 + pages_info_offset + extra_page_info_count
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
                    "ver": self.ver,
                    "page_format_version": page_format_version,
                    "raw": raw_page
                }
            del pages_raw_data[1:1 + 2 + page_count]
            self.elements_data[self.calc_id(path, '-pages-', None)] = self.pages

            decode_info()
            if self.auto_include:
                delete_anchored()

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
            elem_id = None
            is_child = 0 if isinstance(elem_raw_data[1], list) else 1
            if is_child:
                elem_id, elem_data = super().encode(form, path, elem_tree, elem_data)
                self.last_elem_id = form.last_elem_id

                if self.auto_include:
                    path = self.calc_id(path, elem_tree['name'])
                else:
                    path = self.calc_id(path, elem_tree['page'], elem_tree['name'])
                # path = f"{elem_tree['page']}/{path}/{}" if path else f"{elem_tree['page']}/{elem_tree['name']}"
                self.elements_tree = elem_tree['child']
                self.elements_data = form.elements_data
                elem_raw_data[1 + is_child][1] = self.encode_pages(path, elem_raw_data[1 + is_child][1])
                self.encode_elements(path, elem_raw_data[-1])
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
            if self.auto_include:  # перезаписываем оглавление привязок
                elem_raw_data[1 + is_child][1] = self.encode_anchor_index(elem_raw_data[1 + is_child][1])
                # super().encode(form, path, raw_data)
            form.field_data_source += self.field_data_source
            return elem_id, elem_raw_data
        except Exception as err:
            raise ExtException(parent=err)

    @staticmethod
    def pages_offset(raw_data):
        try:
            return calc_offset([[2, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [4, 0]], raw_data)
        except Exception as err:
            raise ExtException(message='Не смогли найти описание страниц элементов формы')

    def encode_pages(self, path, raw_data):
        def encode_page(_elem_id):
            try:
                # elem_id = '/'.join([_path, _name]) if path else _name
                page_data = self.elements_data[_elem_id]
                pages.append(page_data['raw'])
                return page_data.get('info', [])
            except Exception as err:
                raise ExtException(parent=err)

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
                    pages_info += encode_page(self.calc_id(_path, elem['name']))

            else:
                _pages = self.elements_data[self.calc_id(_path, '-pages-')]
                page_count = len(_pages)
                pages.append(str(page_count))
                for name in _pages:
                    pages_info += encode_page(self.calc_id(_path, name))

            raw_data[pages_offset] = pages_raw_data[:1] + pages + pages_raw_data[1:]

            pages_info_offset = pages_offset + 4
            raw_data = raw_data[:pages_info_offset + 1] + pages_info + raw_data[pages_info_offset + 1:]
            raw_data[pages_info_offset] = str(len(pages_info))
            return raw_data
        except Exception as err:
            raise ExtException(parent=err)

    def encode_anchor_index(self, raw_data):
        try:
            result = []
            for border in range(4):
                anchored = self.anchor_index[border]
                result += [str(len(anchored))]
                if anchored:
                    result += anchored
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
                elem_id, res = handler.encode(self, page_id, elem, elem_data)
                self.elements_index[key] = elem_id
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
            self.anchored = {'1': [], '2': [], '3': [], '4': []}
            result = []
            if self.auto_include:
                for i, page in enumerate(self.elements_tree):
                    page_id = '/'.join(_id + [page['name']])
                    if page['child']:
                        for elem in page['child']:
                            key = f"{page_id}/{elem['name']}"
                            self.encode_element(page_id, elem, key, result)
                self.anchored_elem_name_to_elem_id(result, path)
            else:
                for elem in self.elements_tree:
                    page_id = '/'.join(_id)
                    key = []
                    if _path:
                        key.append(_path)
                    if elem['page']:
                        key.append(elem['page'])
                    key.append(elem['name'])
                    key = '/'.join(key)
                    self.encode_element(page_id, elem, key, result)

            raw_data[0] = str(len(result))
            raw_data += result
        except Exception as err:
            raise ExtException(parent=err)

    def anchored_elem_name_to_elem_id(self, result, path):
        def anchor_name_is_num(name):
            try:
                return str(int(name)) == name
            except (TypeError, ValueError):
                return False

        try:
            for elem in result:
                elem_raw_data = elem[-3]
                elem_id = elem[1]
                offset = 6
                _path = path.replace('includr', 'include')
                for anchor_border in range(6):
                    border = 1 if anchor_border > 3 else anchor_border
                    for j in range(1, 3):
                        anchor_name = elem_raw_data[offset][j][1]
                        if anchor_name == '-1':  # ни к чему не привязан
                            continue
                        if anchor_name == '0':  # привязан к панели
                            anchor_border = int(elem_raw_data[offset][j][2])
                            anchor_border = 1 if anchor_border > 3 else anchor_border
                            self.anchor_index[anchor_border].append([elem_raw_data[offset][0], elem_id, str(border)])
                        if anchor_name_is_num(anchor_name):
                            continue
                        else:
                            elem_raw_data[offset][j][1] = self.elements_index[
                                _path + anchor_name]  # нужно имя относительно панели
                    offset += 1

                for anchor_border in range(4):
                    count_anchor = int(elem_raw_data[offset])
                    for j in range(count_anchor):
                        offset += 1
                        anchor_data = elem_raw_data[offset]
                        anchor_name = anchor_data[1]
                        if not anchor_name_is_num(anchor_name):
                            anchor_data[1] = self.elements_index[_path + anchor_name]
                    # elem_raw_data[offset] = '0'
                    # del elem_raw_data[offset + 1: offset + 1 + count_anchor]
                    offset += 1
        except Exception as err:
            raise ExtException(parent=err)
        pass
