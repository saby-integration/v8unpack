# saby v8unpack

[![img lib ver](https://img.shields.io/pypi/v/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img python ver](https://img.shields.io/pypi/pyversions/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img license](https://img.shields.io/pypi/l/v8unpack.svg "")](https://pypi.python.org/pypi/v8unpack)
[![img coverage](https://img.shields.io/coveralls/Infactum/v8unpack.svg "")](https://coveralls.io/github/saby/v8unpack)

**v8unpack** - консольня утилита для сборки и распаковки бинарных файлов 
1С:Предприятие 8.х (cf, cfe, epf) без использования технологической платформы.

Основным назначением утилиты является:
1 сборка разных приложений 1С (расширения конфигураций, внешние обраотки) для различных 
платформ и конфигураций из одних и тех же исходников.
1 удобное и человекочитаемое хранение исходников в системах контроля версий

Распаковка бинарника сделана на онове библиотеки [Infactum/onec_dtools](https://github.com/Infactum/onec_dtools)

Ключевые отличия от аналогичных утлит v8unpack:
 * Файлы хранятся в формате json
 * Программный код всегда хранится в отдельных файлах
 * Человеко-читаемые имена файлов, структура хранения максимально приблежена к структуре метаданных
 * Файлы макетов хранятся в исходном виде (расширение исходного файла двоичных данных нужно указать в 
   комментарии к макету)
 * Атоматически комментируются директивы 8.3 не нужные в 8.2

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

[Переход на сборку из одних исходников](/docs/transition.md)

[Использование](/docs/usage.md)

[История изменений](/docs/history.md)

[Участие](/docs/develop.md)

# Ограничения

Типов объектов метаданных в 1С много, свойств у них ещё больше. Можно бесконечно улучшать
качество и читаемость хранимых данных, до тех пор пока все объекты не будут расшифрованы.

На текущий момент в модуле реализованы только объекты необходимые автору. Текущий
 список реализованных объектов можно посмотреть в файле [metadata_types.py](/src/v8unpack/metadata_types.py) 
 
Если Вам не хватает каких либо типов Вы можете самостоятельно их реализовать и 
добросить в этот репозиторий. О том как это сделать можно почитать в разделе [Участие](/docs/develop.md) 