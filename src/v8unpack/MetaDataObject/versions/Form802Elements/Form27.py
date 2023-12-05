from .Panel import Panel
from .... import helper
from ....ext_exception import ExtException


class Form27:
    @classmethod
    def decode_elements(cls, form, form_data):
        try:
            meta_type = form_data[1][2][0]
            if meta_type != '09ccdc77-ea1a-4a6d-ab1c-3435eada2433':
                raise ExtException(message=f"Неизвестный формат элементов формы",
                                   detail=f"Новый тип элементов формы {meta_type}, "
                                          f"просьба передать файл формы {form.header.get('name')} разработчикам")
            elements_tree, elements_data = Panel.decode(None, '', form_data[1][2])
            form_version = form_data[1][10]
            element_count_all = form_data[1][1][
                1]  # хз что это, +3 к количеству элементов (может дополнительно количество панелей по количеству страниц плюсуется
            element_count_by_pages = form_data[2][1]  # дальше идут пачками по типам
            return elements_tree, elements_data
        except Exception as err:
            raise ExtException(parent=err)

    @classmethod
    def encode(cls, form, src_dir, file_name, version, raw_data, path=''):
        try:
        # index_element_count = 0
        # if raw_data[index_element_count] == 'Дочерние элементы отдельно':
            elements = helper.json_read(src_dir, f'{file_name}.elements{version}.json')
            form.elements_data = elements['data']
            form.elements_tree = elements['tree']
            result = Panel.encode(form, '', raw_data)
            return result
        except Exception as err:
            raise ExtException(parent=err)
