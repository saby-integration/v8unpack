"""CfPatcher — патчинг .cf файлов 1С: замена модулей, header'ов, бинарный поиск.

Стратегия: распаковка cf → правка файлов → сборка cf.
Round-trip сохраняет 100% данных (6794/6794 файлов побайтово идентичны).

Использование:
    from v8unpack.cf_patcher import CfPatcher

    with CfPatcher("original.cf") as p:
        # Прочитать модуль по UUID подконтейнера
        code = p.read_module("8fa89d4f-...")
        code += "\\n// Новый код\\n"
        p.write_module("8fa89d4f-...", code)

        # Найти UUID подконтейнера по содержимому модуля
        uuid = p.find_module_uuid("уникальная строка из модуля")

        # Бинарная замена в любом файле (same-size safe)
        p.binary_replace("uuid.0", old_bytes, new_bytes)

        # Собрать
        p.build("patched.cf")
"""
import os
import shutil
import tempfile
import zlib

from .container import Container
from .json_container_decoder import JsonContainerDecoder


class CfPatcher:
    """Патчер .cf файлов 1С с сохранением бинарной совместимости.

    Работает через распаковку/запаковку контейнера.
    Round-trip потеря: ~38KB на padding (0.1%), все данные идентичны.
    """

    def __init__(self, cf_path: str, work_dir: str = None):
        self.cf_path = cf_path
        self.work_dir = work_dir or tempfile.mkdtemp(prefix="cf_patch_")
        self._extracted = False
        self._main_field3 = None
        self._sub_field3 = {}  # uuid → оригинальный field3 подконтейнеров

    def extract(self):
        """Распаковать cf в рабочую директорию."""
        if self._extracted:
            return
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)
        os.makedirs(self.work_dir)
        with open(self.cf_path, 'rb') as f:
            c = Container()
            c.read(f)
            self._main_field3 = c.header_field3
            c.extract(self.work_dir, deflate=True)
            # Сохраняем checksums для обновления versions при build
            self._extract_checksums = c._extract_checksums
        self._extracted = True

    def _ensure_extracted(self):
        if not self._extracted:
            self.extract()

    # ─── Файлы контейнера ────────────────────────────────────

    def list_files(self) -> list:
        """Список файлов в контейнере."""
        self._ensure_extracted()
        return sorted(os.listdir(self.work_dir))

    def file_path(self, name: str) -> str:
        """Путь к файлу в рабочей директории."""
        self._ensure_extracted()
        return os.path.join(self.work_dir, name)

    def is_container(self, name: str) -> bool:
        """Проверить, является ли файл подконтейнером (бинарным)."""
        path = self.file_path(name)
        if not os.path.exists(path) or os.path.getsize(path) < 4:
            return False
        with open(path, 'rb') as f:
            return f.read(4) == b'\xff\xff\xff\x7f'

    # ─── Header (метаданные: реквизиты, типы) ────────────────

    def read_header(self, uuid: str) -> list:
        """Прочитать header объекта (скобочный формат → list)."""
        self._ensure_extracted()
        jcd = JsonContainerDecoder(src_dir=self.work_dir, file_name=uuid)
        with open(self.file_path(uuid), 'r', encoding='utf-8-sig') as f:
            return jcd.decode_file(f)

    def write_header(self, uuid: str, data: list):
        """Записать header объекта (list → скобочный формат)."""
        self._ensure_extracted()
        jcd = JsonContainerDecoder(src_dir=self.work_dir, file_name=uuid)
        encoded = jcd.encode_root_object(data)
        with open(self.file_path(uuid), 'w', encoding='utf-8-sig') as f:
            f.write(encoded)

    # ─── Модули кода ─────────────────────────────────────────

    def _extract_subcontainer(self, uuid: str) -> str:
        """Распаковать подконтейнер uuid.0, вернуть путь к директории."""
        self._ensure_extracted()
        sub_file = self.file_path(f"{uuid}.0")
        if not os.path.exists(sub_file):
            raise FileNotFoundError(f"Subcontainer {uuid}.0 not found")
        if not self.is_container(f"{uuid}.0"):
            raise ValueError(
                f"{uuid}.0 is not a binary container (text/base64 file). "
                f"Module may be stored under a different UUID. "
                f"Use find_module_uuid() to locate it."
            )

        sub_dir = os.path.join(self.work_dir, f"_sub_{uuid}")
        if os.path.exists(sub_dir):
            shutil.rmtree(sub_dir)
        os.makedirs(sub_dir)

        with open(sub_file, 'rb') as f:
            c = Container()
            c.read(f)
            self._sub_field3[uuid] = c.header_field3
            c.extract(sub_dir, deflate=False)

        return sub_dir

    def _rebuild_subcontainer(self, uuid: str, sub_dir: str):
        """Пересобрать подконтейнер с оригинальным field3."""
        sub_file = self.file_path(f"{uuid}.0")
        field3 = self._sub_field3.get(uuid)
        with open(sub_file, 'w+b') as f:
            c = Container()
            c.build(f, sub_dir, nested=True, header_field3=field3)
        shutil.rmtree(sub_dir)

    def read_module(self, uuid: str) -> str:
        """Прочитать модуль объекта из подконтейнера.

        Args:
            uuid: UUID объекта, чей .0 файл содержит подконтейнер с модулем.
                  Для документов/обработок это может быть UUID отличный от
                  UUID самого объекта. Используйте find_module_uuid() для поиска.

        Returns:
            Текст модуля (UTF-8). Пустая строка если модуля нет.
        """
        sub_dir = self._extract_subcontainer(uuid)
        text_path = os.path.join(sub_dir, "text")
        if not os.path.exists(text_path):
            shutil.rmtree(sub_dir)
            return ""
        with open(text_path, 'rb') as f:
            raw = f.read()
        # Убираем BOM, декодируем как UTF-8
        if raw[:3] == b'\xef\xbb\xbf':
            raw = raw[3:]
        code = raw.decode('utf-8')
        shutil.rmtree(sub_dir)
        return code

    def write_module(self, uuid: str, code: str):
        """Записать модуль объекта и пересобрать подконтейнер.

        Сохраняет оригинальный формат переводов строк (CRLF/CRCRLF).
        Если передан текст с LF — конвертирует в CRLF.

        Args:
            uuid: UUID объекта (тот же что для read_module).
            code: Новый текст модуля.
        """
        sub_dir = self._extract_subcontainer(uuid)
        text_path = os.path.join(sub_dir, "text")

        # Определяем формат newline из оригинального файла
        orig_nl = b'\r\n'  # default CRLF
        if os.path.exists(text_path):
            with open(text_path, 'rb') as f:
                orig_raw = f.read(4096)
            if b'\r\r\n' in orig_raw:
                orig_nl = b'\r\r\n'
            elif b'\r\n' in orig_raw:
                orig_nl = b'\r\n'

        # Нормализуем newlines: сначала к LF, потом к оригинальному формату
        code = code.replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
        raw = code.encode('utf-8')
        raw = b'\xef\xbb\xbf' + raw.replace(b'\n', orig_nl)

        with open(text_path, 'wb') as f:
            f.write(raw)
        self._rebuild_subcontainer(uuid, sub_dir)

    # ─── Поиск UUID ──────────────────────────────────────────

    def find_module_uuid(self, search_text: str) -> str:
        """Найти UUID подконтейнера, содержащего заданный текст в модуле.

        В cf формате UUID объекта (документ, обработка) может не совпадать
        с UUID подконтейнера, хранящего его модуль. Эта функция ищет
        текст во всех подконтейнерах и возвращает UUID первого найденного.

        Args:
            search_text: Уникальная строка из модуля для поиска.

        Returns:
            UUID (без .0) подконтейнера с модулем.

        Raises:
            ValueError: если текст не найден ни в одном подконтейнере.
        """
        self._ensure_extracted()
        search_bytes = search_text.encode('utf-8')

        for fname in sorted(os.listdir(self.work_dir)):
            if fname.startswith('_'):
                continue
            if not fname.endswith('.0'):
                continue
            path = os.path.join(self.work_dir, fname)
            if os.path.getsize(path) < 100:
                continue
            with open(path, 'rb') as f:
                head = f.read(4)
            if head != b'\xff\xff\xff\x7f':
                continue  # не контейнер
            with open(path, 'rb') as f:
                data = f.read()
            if search_bytes in data:
                return fname[:-2]  # убираем .0

        raise ValueError(f"Text not found in any subcontainer: {search_text[:50]}...")

    # ─── Бинарная замена ─────────────────────────────────────

    def binary_replace(self, filename: str, old: bytes, new: bytes) -> int:
        """Заменить байты в файле контейнера.

        Для подконтейнеров (.0) заменяет в сжатом/несжатом виде напрямую.
        Для текстовых файлов — простая замена.

        Args:
            filename: Имя файла в контейнере (например "uuid.0").
            old: Байты для поиска.
            new: Байты замены. Рекомендуется same-size для безопасности.

        Returns:
            Количество замен.
        """
        self._ensure_extracted()
        path = self.file_path(filename)
        with open(path, 'rb') as f:
            data = f.read()
        count = data.count(old)
        if count > 0:
            data = data.replace(old, new)
            with open(path, 'wb') as f:
                f.write(data)
        return count

    def binary_replace_text(self, filename: str, old_text: str, new_text: str,
                            encoding: str = 'utf-8') -> int:
        """Заменить текст в файле контейнера (кодируя в указанную кодировку).

        Args:
            filename: Имя файла в контейнере.
            old_text: Текст для поиска.
            new_text: Текст замены.
            encoding: Кодировка (по умолчанию UTF-8).

        Returns:
            Количество замен.
        """
        return self.binary_replace(
            filename,
            old_text.encode(encoding),
            new_text.encode(encoding)
        )

    # ─── Сборка ──────────────────────────────────────────────

    def build(self, output_path: str) -> int:
        """Собрать патченный .cf файл.

        Автоматически обновляет UUID в файле versions для
        изменённых файлов (через Container.build).

        Returns:
            Размер выходного файла в байтах.
        """
        self._ensure_extracted()
        # Удаляем временные директории подконтейнеров
        for d in os.listdir(self.work_dir):
            if d.startswith('_sub_'):
                shutil.rmtree(os.path.join(self.work_dir, d))

        with open(output_path, 'w+b') as f:
            c = Container()
            c._extract_checksums = self._extract_checksums
            c.build(f, self.work_dir, nested=False, header_field3=self._main_field3)
        return os.path.getsize(output_path)

    def cleanup(self):
        """Удалить рабочую директорию."""
        if os.path.exists(self.work_dir):
            shutil.rmtree(self.work_dir)

    def __enter__(self):
        self.extract()
        return self

    def __exit__(self, *args):
        self.cleanup()
