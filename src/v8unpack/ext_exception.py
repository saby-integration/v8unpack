import json
import sys
import traceback
from os import path


# 3xxx - Ошибки в нашем коде
# 4xxx - Ошибки вызванные некорректными действиями пользователей
# 5xxx - Ошибки вызванные временной недоступностью функционала,повторный вызов с теми же параметрами может быть успешным
# 6xxx - Ошибки во внешних сервисах и библиотеках
# 8xxx - Запросы не реализованного, но потонциально интересного функционала
# 9xxx - Обертка над стандартными ошибками для испльзования в коде


class ExtException(Exception):
    _code = 3000
    _http_code = 500
    _message = None

    # _message = "Unknown error"

    def __new__(cls, *args, **kwargs):
        parent = kwargs.get('parent')
        if parent:
            # прокидываем ошибку наверх
            if isinstance(parent, ExtException) \
                    and parent.__class__ != ExtException \
                    and kwargs.get('message') is None \
                    and cls == ExtException:
                return super().__new__(parent.__class__)
            if isinstance(parent, dict):  # пытаемся поднять правильный класс
                class_name = parent.pop('__name__', None)
                module_name = parent.pop('__module__', None)
                if class_name and module_name:
                    try:
                        m = __import__(module_name)
                        parts = f'{module_name}.{class_name}'.split('.')
                        for comp in parts[1:]:
                            m = getattr(m, comp)
                        return super().__new__(m)
                    except:
                        pass
        return super().__new__(cls)

    def __init__(self, *, parent=None, code=None, message=None, detail=None, action=None, dump=None,
                 skip_traceback=0, stack=None):
        self.skip_traceback = skip_traceback
        self.code = code
        self.message = message
        self.detail = detail

        self.dump = {} if dump is None else dump
        self.stack = [] if stack is None else stack

        if action and not isinstance(action, str):  # это класс действте
            # self.add_action_to_stack(action)
            self.action = action.name
        else:
            self.action = action

        self.new_msg = bool(message)
        if parent:
            if isinstance(parent, ExtException):  # прокидываем ошибку наверх
                self.add_parent_to_stack(parent)
                if not message:
                    self.message = parent.message
                    self.detail = parent.detail
                    self.code = parent.code
                    self.dump = parent.dump
            elif isinstance(parent, Exception):
                if not message:
                    self.message = 'Unknown Error'
                if not detail:
                    self.detail = str(parent)
                self.add_sys_exc_to_stack()
            elif isinstance(parent, dict):
                self.code = parent.get('code', self._code)
                self.message = parent.get('message')
                self.detail = parent.get('detail')
                self.dump = parent.get('dump', {})
                self.stack = parent.get('stack', [])
                self.action = parent.get('action')

            else:
                raise NotImplementedError(f'ExtException parent={type(parent)}')
        if not self.stack:
            self.add_sys_exc_to_stack()
        if not self.message:
            self.message = self._message
        pass

    def add_action_to_stack(self, action):
        try:
            self.action = action.name
            if action.stat:
                action.set_end('Error')
                self.dump['_action_stat'] = action.stat
        except:
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
        if isinstance(exc_info[1], ExtException):
            message = getattr(exc_info[1], 'message')
            detail = getattr(exc_info[1], 'detail')
        else:
            message = exc_info[0].__name__
            detail = str(exc_info[1])
        return {
            'message': message,
            'detail': detail,
            'traceback': f'{path.basename(path.dirname(last_call.filename))}/{path.basename(last_call.filename)}, '
                         f'{last_call.name}, line {last_call.lineno}'
        }

    @property
    def title(self):
        title = ''
        if self.code:
            title += f'{self.code}:'

        title += f'{self.__class__.__name__} {self.message}'

        if self.detail:
            title += f' - {self.detail}'
        return title

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


class TooManyRequests(ExtException):
    _code = 4290
    _message = "Too Many Requests"
    # dump
    # X-RateLimit-Limit - количество запросов, которые равномерно можно сделать в течение интервала до появления 429 ошибки
    # X-Lognex-Retry-TimeInterval - интервал в миллисекундах, в течение которого можно сделать эти запросы
    # X-RateLimit-Remaining - Число запросов, которые можно отправить до получения 429 ошибки
    # X-Lognex-Reset - время до сброса ограничения в миллисекундах. Равно нулю, если ограничение не установлено
    # X-Lognex-Retry-After - время до сброса ограничения в миллисекундах.


class NotFound(ExtException):
    _code = 4300
    _message = "Not found"


class WaitingUserAction(ExtException):
    _code = 4911
    _message = "Waiting for user action"


class AccessDenied(ExtException):
    _code = 4031
    _http_code = 403
    _message = "Access denied"


class CancelOperation(ExtException):
    _code = 4999
    _message = "Cancel operation",


class NotAvailable(ExtException):
    _code = 5000
    _message = "Not available",


class ForeignError(ExtException):
    _code = 6000
    _message = "Unknown external error",


class ExtTimeoutError(ExtException):
    _code = 5008
    _http_code = 408
    _message = "Timeout",


class ExtNotImplemented(ExtException):
    _code = 8000
    _http_code = 400
    _message = "Not implemented",


def dumps_error(err):
    return json.dumps({
        '__name__': err.__class__.__name__,
        '__module__': err.__class__.__module__,
        'message': str(err)
    })