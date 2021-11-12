# saby v8unpack

[![img lib ver](https://img.shields.io/pypi/v/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img python ver](https://img.shields.io/pypi/pyversions/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img license](https://img.shields.io/pypi/l/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img coverage](https://img.shields.io/coveralls/saby/v8unpack.svg "")](https://coveralls.io/github/saby/v8unpack)

**v8unpack** - консольная утилита для сборки и распаковки бинарных файлов 
1С:Предприятие 8.х (cf, cfe, epf) без использования технологической платформы.

В какой-то момент жить без системы контроля версий на уровне исходников стало совсем не выносимо и обозрев все 
варианты выбор пал на v8unpack. Однако, без устранения основных недостатков его использование было бы крайне 
не удобным (плоский список из нечеловекочитаемых файлов, скрытый где-то в дебрях программный код управляемых форм). 
Сразу скажу, что мы с глубоким уважением относимся к труду авторов v8unpack, данная утилита отлично выполняет все 
свои функции и без неё создание этого решения было бы не возможным. Кроме этого её Python реализация от [Infactum](https://github.com/Infactum/onec_dtools) 
была взята за основу без каких либо изменений.

## Ключевые отличия от аналогичных утилит:
* Структура хранения максимально приближена к структуре метаданных, человеко-читаемые имена файлов
* Программный код всегда хранится в отдельных файлах и может быть разделен на несколько файлов
* Общие для разных решений объекты метаданных могут автоматически браться из субмодулей
* Двоичные данные макетов и картинки хранятся в исходном виде
* При сборке под 8.2 и 8.1. автоматически комментируются директивы 8.3
* Файлы хранятся в формате json

## Основным назначением нашей версии утилиты являются:

1.	Автоматическая сборка приложений 1С (расширения конфигураций, внешние обработки) 
для различных платформ и конфигураций из одних и тех же исходников
2.	Удобное и человекочитаемое хранение исходников в системах контроля версий.


## Установка

    pip install v8unpack

или [скачайте exe файл](https://github.com/saby-integration/v8unpack/raw/main/exe/v8unpack.exe)

## Распаковка файла 1С

из командной строки:

    v8unpack.exe -E d:/sample.cf d:/unpack

из python:
```python
import v8unpack

if __name__ == '__main__':
    v8unpack.extract('d:/sample.cf', 'd:/unpack')
```

## Сборка исходников

из командной строки:

    v8unpack.exe -B d:/unpack d:/repacked.cf

из python:

```python
import v8unpack

if __name__ == '__main__':
    v8unpack.build('d:/unpack', 'd:/repacked.cf')
```

## Документация

[Переход на сборку из одних исходников](https://github.com/saby-integration/v8unpack/blob/main/docs/transition.md)

[Использование](https://github.com/saby-integration/v8unpack/blob/main/docs/usage.md)

[История изменений](https://github.com/saby-integration/v8unpack/blob/main/docs/history.md)

[Участие](https://github.com/saby-integration/v8unpack/blob/main/docs/develop.md)

## Алгоритм работы
Утилита распаковывает и запаковывет бинарник 1С в 4 этапа:

1.	Распаковка стандартным v8unpack – на выходе текстовые файлы
2.	Конвертация в json
3.	Декодирование заголовков и разбивка по типам метаданных
4.	Организация кода и структуры хранения

![Алгоритм работы](https://github.com/saby-integration/v8unpack/blob/main/docs/stage.png)

## Ограничения

Разметка форм и свойства объектов по прежнему является не читаемыми, но в этом виде проще проводить их 
анализ и при желании дополнить парсер.

На текущий момент [утилита покрывает только нужные нам типы метаданных](https://github.com/saby-integration/v8unpack/blob/main/src/v8unpack/metadata_types.py), 
мы будем рады [любому участию в проекте](https://github.com/saby-integration/v8unpack/blob/main/docs/develop.md).
