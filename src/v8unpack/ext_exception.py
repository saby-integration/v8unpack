import json
import sys
import traceback
from os import path


# 3xxx - Ошибки в нашем коде
# 4xxx - Ошибки вызванные некорректными действиями пользователей
# 5xxx - Ошибки вызванные временной недоступностью функционала, повторный вызов с теми же параметрами может быть успешным
# 6xxx - Ошибки во внешних сервисах и библиотеках
# 8xxx - Запросы не реализованного, но потенциально интересного функционала
# 9xxx - Обертка над стандартными ошибками для использования в коде


class ExtException(Exception):
    _code = 3000
    _http_code = 500
    _message = "Unknown error"

    def __new__(cls, *args, **kwargs):
        parent = kwargs.get('parent')
        if parent:
            # прокидываем ошибку наверх
            if isinstance(parent, ExtException) and parent.__class__ != ExtException and cls == ExtException:
                return parent.__class__(*args, **kwargs)
            # восстанавливаем из строки
        return super(ExtException, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.skip_traceback = kwargs.get('skip_traceback', 0)
        self.code = ''
        self.message = ''
        self.detail = ''
        self.action = ''
        self.dump = {}
        self.stack = []
        self.new_msg = False
        parent = kwargs.get('parent')
        if parent and isinstance(parent, ExtException):  # прокидываем ошибку наверх
            self.add_parent_to_stack(parent)
            self.message = parent.message
            self.code = parent.code
            self.detail = parent.detail
            self.new_msg = bool(kwargs.get('message'))
        self.init_from_dict(kwargs)
        if parent and isinstance(parent, Exception) and not isinstance(parent, ExtException):
            self.code = self._code
            self.message = kwargs.get('message', self._message)
            if not self.detail:
                self.detail = str(parent)
            self.add_sys_exc_to_stack()
        if args:
            if isinstance(args[0], str):
                self.new_msg = True
                self.message = args[0]
            else:
                raise Exception(f'Not supported ExtException args[0] ({type(args[0])})')
        if not self.stack:
            self.add_sys_exc_to_stack()
        pass

    def add_parent_to_stack(self, parent):
        if not isinstance(parent, ExtException):
            return None
        self.stack += parent.stack
        if not parent.action:
            return
        parent.dump['action'] = parent.action
        if not self.stack:
            data = self.get_sys_exc_info()
            if data:
                parent.dump['traceback'] = data['traceback']

        if parent.new_msg:
            parent.dump['message'] = parent.message
            if parent.detail:
                parent.dump['detail'] = parent.detail
        self.stack.append(parent.dump)

    def add_sys_exc_to_stack(self):
        try:
            data = self.get_sys_exc_info()
        except IndexError:
            return
        if not data:
            return
        data['action'] = self.action
        self.stack.append(data)

    def get_sys_exc_info(self):
        exc_info = sys.exc_info()
        if exc_info[2] is None:
            return None
        last_call = traceback.extract_tb(exc_info[2], limit=self.skip_traceback + 1)
        last_call = last_call[self.skip_traceback]
        return {
            'message': exc_info[0].__name__,
            'detail': str(exc_info[1]),
            'traceback': f'{path.basename(last_call.filename)}, {last_call.name}, line {last_call.lineno}'
        }

    def init_from_dict(self, data):
        for field in ['code', 'message', 'detail', 'action', 'dump', 'stack']:
            if field in data:
                setattr(self, field, data[field])
        if not self.message:
            self.message = self._message
        if not self.code:
            self.code = self._code

    @property
    def title(self):
        if self.detail:
            return f'{self.code}: {self.message} - {self.detail}'
        return f'{self.code}: {self.message}'

    def __str__(self):
        res = f'{self.title}'
        if self.dump:
            res += f'\nDump: action={self.action}; '
            for elem in self.dump:
                res += f'{elem}={self.dump[elem]}; '
        if self.stack:
            res += '\n Stack:'
            for stack in self.stack:
                _action = stack.get('action', '')
                res += f'\n  - {_action}: '
                for elem in stack:
                    if elem != 'action':
                        res += f'{elem}={stack[elem]}; '
        return res

    def dumps(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_dict(self):
        return {
            '__name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'message': self.message,
            'detail': self.detail,
            'code': self.code,
            'action': self.action,
            'dump': self.dump,
            'stack': self.stack
        }

    @property
    def http_code(self):
        return self._http_code


class HandlerNotFoundError(ExtException):
    _code = 3100
    _message = "Handler not found",


class UserError(ExtException):
    _code = 4000


class Unauthorized(ExtException):
    _code = 4011
    _http_code = 401
    _message = "Unauthorized"


class ResourceNotAvailable(ExtException):
    _code = 4100
    _message = "Resource not available"


class KeyNotFound(ExtException):
    _code = 4200
    _message = "Required parameter are missing"


class AccessDenied(ExtException):
    _code = 4031
    _http_code = 403
    _message = "Access denied"


class CancelOperation(ExtException):
    _code = 4999
    _message = "Cancel operation",


class NotAvailableError(ExtException):
    _code = 5000
    _message = "Not available",


class ForeignError(ExtException):
    _code = 6000
    _message = "Unknown external error",


class ExtTimeoutError(ExtException):
    _code = 5008
    _http_code = 408
    _message = "Timeout",


def dumps_error(err):
    return json.dumps({
        '__name__': err.__class__.__name__,
        '__module__': err.__class__.__module__,
        'message': str(err)
    })
