from enum import Enum


class MetaDataTypes(Enum):
    # todo в синтаксис помощнике найти все английские названия искать строкой "ОбъектМетаданных: [хxx...]"
    # DocumentAttribute = "45e46cbc-3e24-4165-8b7b-cc98a6f80211"        # Документ.Реквизиты
    # ExternalDataSource = 'e68182ea-4237-4383-967f-90c1e3370bc7'         # Внешние источники данных (не точно...)
    AccountingRegister = '2deed9b8-0056-4ffe-a473-c20a6c32a0bc'  # Регистры бухгалтерии
    AccountingRegisterForm = 'd3b5d6eb-4ea2-4610-a3e2-624d4e815934'  # Регистры бухгалтерии
    AccumulationRegister = 'b64d9a40-1642-11d6-a3c7-0050bae0a776'  # Регистры накопления
    AccumulationRegisterForm = 'b64d9a44-1642-11d6-a3c7-0050bae0a776'  # Регистры накопления форма
    BusinessProcess = 'fcd3404e-1523-48ce-9bc0-ecdb822684a1'  # Бизнес-процессы
    BusinessProcessCommand = '7a3e533c-f232-40d5-a932-6a311d2480bf'
    BusinessProcessForm = '3f7a8120-b71a-4265-98bf-4d9bc09b7719'
    CalculationRegister = 'f2de87a8-64e5-45eb-a22d-b3aedab050e7'  # Регистры расчета
    CalculationRegisterForm = 'a2cb086c-db98-43e4-a1a9-0760ab048f8d'  # Регистры расчета
    CalculationRegisterRecalculations = '274bf899-db0e-4df6-8ab5-67bf6371ec0b'  # Перерасчеты
    Catalog = "cf4abea6-37b2-11d4-940f-008048da11f9"  # Справочники
    CatalogCommand = '4fe87c89-9ad4-43f6-9fdb-9dc83b3879c6'  # Команда справочника
    CatalogForm = 'fdf816d2-1ead-11d5-b975-0050bae0a95d'  # Форма элемента справочника
    ChartOfAccounts = '238e7e88-3c5f-48b2-8a3b-81ebbecb20ed'  # План счетов
    ChartOfAccountsForm = '5372e285-03db-4f8c-8565-fe56f1aea40e'  # План счетов
    ChartOfCalculationTypes = '30b100d6-b29f-47ac-aec7-cb8ca8a54767'  # План видов расчета
    ChartOfCalculationTypesForm = 'a7f8f92a-7a4b-484b-937e-42d242e64144'
    ChartOfCharacteristicType = '82a1b659-b220-4d94-a9bd-14d757b95a48'  # План видов характеристик
    ChartOfCharacteristicTypeForm = 'eb2b78a8-40a6-4b7e-b1b3-6ca9966cbc94'  # План видов характеристик
    CommandGroup = '1c57eabe-7349-44b3-b1de-ebfeab67b47d'  # Группа команд
    CommonAttribute = '15794563-ccec-41f6-a83c-ec5f7b9a5bc1'  # Общие реквизиты
    CommonCommand = '2f1a5187-fb0e-4b05-9489-dc5dd6412348'  # Общая команда
    CommonForm = "07ee8426-87f1-11d5-b99c-0050bae0a95d"  # Общие формы
    CommonModule = '0fe48980-252d-11d6-a3c7-0050bae0a776'  # Общие модули
    CommonPicture = '7dcd43d9-aca5-4926-b549-1842e6a4e8cf'  # Общие картинки
    CommonTemplate = '0c89c792-16c3-11d5-b96b-0050bae0a95d'  # Общие макеты
    Configuration = '9cd510cd-abfc-11d4-9434-004095e12fc7'  # Идентифицирует род. узел описания конфигурации
    Constant = '0195e80c-b157-11d4-9435-004095e12fc7'  # Константы
    DataProcessor = "bf845118-327b-4682-b5c6-285d2a0eb296"  # Обработки
    DataProcessorCommand = '45556acb-826a-4f73-898a-6025fc9536e1'
    DefinedType = 'c045099e-13b9-4fb6-9d50-fca00202971e'  # Определяемые типы
    Document = "061d872a-5787-460e-95ac-ed74ea3a3e84"  # Документы
    DocumentCommand = 'b544fc6a-2ba3-4885-8fb2-cb289fb6d65e'  # Команда документа
    DocumentForm = "fb880e93-47d7-4127-9357-a20e69c17545"  # Форма документа
    DocumentJournal = '4612bd75-71b7-4a5c-8cc5-2b0b65f9fa0d'  # Журналы документов
    DocumentJournalCommand = "a49a35ce-120a-4c80-8eea-b0618479cd70"
    DocumentJournalForm = 'ec81ad10-ca07-11d5-b9a5-0050bae0a95d'
    DocumentNumerators = '36a8e346-9aaa-4af9-bdbd-83be3c177977'  # Нумератор документа
    Enum = "f6a80749-5ad7-400b-8519-39dc5dff2542"  # Перечисления
    EnumForm = "33f2e54b-37ce-4a7a-a569-b648d7aa4634"  # Перечисления
    EventSubscription = '4e828da6-0f44-4b5b-b1c0-a2b3cfe7bdcc'  # Подписки на события
    ExchangePlan = '857c4a91-e5f4-4fac-86ec-787626f1c108'  # План обмена
    ExchangePlanCommand = 'd5207c64-11d5-4d46-bba2-55b7b07ff4eb'
    ExchangePlanForm = '87c509ab-3d38-4d67-b379-aca796298578'  # План обмена Form
    ExternalDataProcessor = 'c3831ec8-d8d5-4f93-8a22-f9bfae07327f'  # Внешняя обработка
    FilterCriterion = '3e7bfcc0-067d-11d6-a3c7-0050bae0a776'  # Критерии отбора
    FilterCriterionForm = '00867c40-06b1-11d6-a3c7-0050bae0a776'  # Критерии отбора Form
    Form = 'd5b0e5ed-256d-401c-9c36-f630cafd8a62'  # Форма внешней обработки
    FormAttribute = 'ec6bb5e5-b7a8-4d75-bec9-658107a699cf'  # Атрибут Внешней обработки
    FunctionalOption = 'af547940-3268-434f-a3e7-e47d6d2638c3'  # Функциональные опции
    FunctionalOptionsParameter = '30d554db-541e-4f62-8970-a1c6dcfeb2bc'  # Параметры функциональных опций
    HTTPService = '0fffc09c-8f4c-47cc-b41c-8d5c5a221d79'  # HTTPСервис
    InformationRegister = '13134201-f60b-11d5-a3c7-0050bae0a776'  # Регистры сведений
    InformationRegisterCommand = 'b44ba719-945c-445c-8aab-1088fa4df16e'
    InformationRegisterForm = '13134204-f60b-11d5-a3c7-0050bae0a776'  # Form регистра сведений
    Interface = '39bddf6a-0c3c-452b-921c-d99cfa1c2f1b'  # Интерфейсы
    Language = '9cd510ce-abfc-11d4-9434-004095e12fc7'  # Языки
    Report = '631b75a0-29e2-11d6-a3c7-0050bae0a776'  # Отчеты
    ReportCommand = 'e7ff38c0-ec3c-47a0-ae90-20c73ca72246'  # Отчеты
    ReportForm = 'a3b368c0-29e2-11d6-a3c7-0050bae0a776'  # Отчеты форма
    Role = '09736b02-9cac-4e3f-b4f7-d3e9576ab948'  # Роли
    ScheduledJob = '11bdaf85-d5ad-4d91-bb24-aa0eee139052'  # Регламентные задания
    Sequences = 'bc587f20-35d9-11d6-a3c7-0050bae0a776'  # Последовательность, 1 ШТ
    SessionParameter = '24c43748-c938-45d0-8d14-01424a72b11e'  # Параметры сеанса
    SettingsStorage = '46b4cd97-fd13-4eaa-aba2-3bddd7699218'  # Хранилища настроек
    SettingsStorageForm = 'b8533c0c-2342-4db3-91a2-c2b08cbf6b23'
    Style = '3e5404af-6ef8-4c73-ad11-91bd2dfac4c8'  # Стиль
    StyleItem = '58848766-36ea-4076-8800-e91eb49590d7'  # Элемены стиля
    Subsystem = '37f2fa9a-b276-11d4-9435-004095e12fc7'  # Подсистемы
    TabularSectionAttribute = '2bcef0d1-0981-11d6-b9b8-0050bae0a95d'  # Атрибут Табличной части Внешней обработки
    Task = '3e63355c-1378-4953-be9b-1deb5fb6bec5'  # Задачи
    TaskCommand = 'f27c2152-a2c9-4c30-adb1-130f5eb2590f'
    TaskForm = '3f58cbfb-4172-4e54-be49-561a579bb38b'
    Template = '3daea016-69b7-4ed4-9453-127911372fe6'  # Макет внешней обработки
    WebService = '8657032e-7740-4e1d-a3ba-5dd6e8afb78f'  # Веб-сервис
    WSReference = 'd26096fb-7a5d-4df9-af63-47d04771fa9b'  # WS-ссылки
    XDTOPackage = 'cc9df798-7c94-4616-97d2-7aa0b7bc515e'  # ПакетXDTO





