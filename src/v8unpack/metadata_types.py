from enum import Enum


class MetaDataTypes(Enum):
    # todo в синтаксис помощнике найти все английские названия искать строкой "ОбъектМетаданных: [хxx...]"
    ExternalDataProcessor = 'c3831ec8-d8d5-4f93-8a22-f9bfae07327f'  # Внешняя обработка
    Configuration = '9cd510cd-abfc-11d4-9434-004095e12fc7'
    CommandGroup = '1c57eabe-7349-44b3-b1de-ebfeab67b47d'  # ГруппаКоманд
    TabularSectionAttribute = '2bcef0d1-0981-11d6-b9b8-0050bae0a95d'  # Атрибут Табличной части Внешней обработки
    FormAttribute = 'ec6bb5e5-b7a8-4d75-bec9-658107a699cf'  # Атрибут Внешней обработки
    Documents = "061d872a-5787-460e-95ac-ed74ea3a3e84"  # Документы
    DocumentAttributes = "45e46cbc-3e24-4165-8b7b-cc98a6f80211"  # Документ.Реквизиты
    DocumentCommand = 'b544fc6a-2ba3-4885-8fb2-cb289fb6d65e'  # Команда документа
    DocumentForm = "fb880e93-47d7-4127-9357-a20e69c17545"  # Форма документа
    DataProcessor = "bf845118-327b-4682-b5c6-285d2a0eb296"  # Обработки
    Template = '3daea016-69b7-4ed4-9453-127911372fe6'  # Макет внешней обработки
    Form = 'd5b0e5ed-256d-401c-9c36-f630cafd8a62'  # Форма внешней обработки
    Catalog = "cf4abea6-37b2-11d4-940f-008048da11f9"  # Справочники
    CatalogForm = 'fdf816d2-1ead-11d5-b975-0050bae0a95d'  # Форма элемента
    CatalogCommand = '4fe87c89-9ad4-43f6-9fdb-9dc83b3879c6'  # Команда справочника
    CommonPicture = '7dcd43d9-aca5-4926-b549-1842e6a4e8cf'  # ОбщиеКартинки
    CommonCommand = '2f1a5187-fb0e-4b05-9489-dc5dd6412348'  # ОбщаяКоманда
    CommonTemplate = '0c89c792-16c3-11d5-b96b-0050bae0a95d'  # ОбщиеМакеты
    CommonModules = '0fe48980-252d-11d6-a3c7-0050bae0a776'  # ОбщиеМодули
    CommonForms = "07ee8426-87f1-11d5-b99c-0050bae0a95d"  # ОбщиеФормы
    Report = '631b75a0-29e2-11d6-a3c7-0050bae0a776'  # Report
    InformationRegister = '13134201-f60b-11d5-a3c7-0050bae0a776'  # РегистрыСведений
    Subsystem = '37f2fa9a-b276-11d4-9435-004095e12fc7'  # Подсистемы
    Role = '09736b02-9cac-4e3f-b4f7-d3e9576ab948'  # Роли
    Language = '9cd510ce-abfc-11d4-9434-004095e12fc7'  # Языки
    # ПараметрыСеанса = '24c43748-c938-45d0-8d14-01424a72b11e'
    Enums = "f6a80749-5ad7-400b-8519-39dc5dff2542"  # Перечисления
    # ПланВидовХарактеристик = '82a1b659-b220-4d94-a9bd-14d757b95a48'
    # ПланыВидовРасчета = '30b100d6-b29f-47ac-aec7-cb8ca8a54767'
    # ПланыОбмена = '857c4a91-e5f4-4fac-86ec-787626f1c108'
    # ПланыСчетов = '238e7e88-3c5f-48b2-8a3b-81ebbecb20ed'
    # РегистрыНакопления = 'b64d9a40-1642-11d6-a3c7-0050bae0a776'
    # РегистрыРасчета = 'f2de87a8-64e5-45eb-a22d-b3aedab050e7'
    # Стили = '3e5404af-6ef8-4c73-ad11-91bd2dfac4c8'
    # РегистрыБухгалтерии = '2deed9b8-0056-4ffe-a473-c20a6c32a0bc'
    StyleItems = '58848766-36ea-4076-8800-e91eb49590d7'  # ЭлеменыСтиля
    # HTTPСервисы = '0fffc09c-8f4c-47cc-b41c-8d5c5a221d79'
    # XDTOПакеты = 'cc9df798-7c94-4616-97d2-7aa0b7bc515e'
    # WebСервисы = '8657032e-7740-4e1d-a3ba-5dd6e8afb78f'
