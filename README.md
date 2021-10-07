# saby v8unpack

[![img lib ver](https://img.shields.io/pypi/v/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img python ver](https://img.shields.io/pypi/pyversions/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img license](https://img.shields.io/pypi/l/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img coverage](https://img.shields.io/coveralls/saby/v8unpack.svg "")](https://coveralls.io/github/saby/v8unpack)

**v8unpack** - консольня утилита для сборки и распаковки бинарных файлов 
1С:Предприятие 8.х (cf, cfe, epf) без использования технологической платформы.

Основным назначением утилиты является:

1. сборка приложений 1С (расширения конфигураций, внешние обработки) для различных 
платформ и конфигураций из одних и тех же исходников.

2. удобное и человекочитаемое хранение исходников в системах контроля версий

Распаковка бинарника сделана на онове библиотеки [Infactum/onec_dtools](https://github.com/Infactum/onec_dtools)

Ключевые отличия от аналогичных утлит v8unpack:
 * Файлы хранятся в формате json
 * Программный код всегда хранится в отдельных файлах и может быть разделен на несколько файлов
 * Человеко-читаемые имена файлов
 * Структура хранения максимально приблежена к структуре метаданных
 * Файлы макетов хранятся в исходном виде (расширение исходного файла нужно указать в 
   комментарии к макету)
 * При сборке под 8.2 и 8.1. атоматически комментируются директивы 8.3

# Установка

    pip install v8unpack

# Использование

## Распаковка файла 1С

из коммандной строки:

    v8unpack.exe -E d:/sample.cf d:/unpack

из python:
```python
import v8unpack

if __name__ == '__main__':
    v8unpack.extract('d:/sample.cf', 'd:/unpack')
```

## Сборка исходников

из коммандной строки:

    v8unpack.exe -B d:/unpack d:/repacked.cf

из python:

```python
import v8unpack

v8unpack.build('d:/unpack', 'd:/repacked.cf')
```

## Документация

[Переход на сборку из одних исходников](https://github.com/saby/v8unpack/blob/main/docs/transition.md)

[Использование](https://github.com/saby/v8unpack/blob/main/docs/usage.md)

[История изменений](https://github.com/saby/v8unpack/blob/main/docs/history.md)

[Участие](https://github.com/saby/v8unpack/blob/main/docs/develop.md)

# Ограничения

Типов объектов метаданных в 1С много, свойств у них ещё больше. Можно бесконечно улучшать
качество и читаемость хранимых данных, до тех пор пока все объекты не будут расшифрованы.

На текущий момент в модуле реализованы только объекты необходимые автору. Текущий
 список реализованных объектов можно посмотреть в файле [metadata_types.py](https://github.com/saby/v8unpack/blob/main/src/v8unpack/metadata_types.py) 
 
Если Вам не хватает каких либо типов Вы можете самостоятельно их реализовать и 
добросить в этот репозиторий. О том как это сделать можно почитать в разделе [Участие](https://github.com/saby/v8unpack/blob/main/docs/develop.md) 