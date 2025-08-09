# Структура проекта ai_itmo_qa

## Запуск

Для корректной работы системы должны быть заданы переменные среды из файла [config.py](./config.py). Необходимо 2 файла - service key для генерации эмбеддингов Yandex GPT и service key для доступа к YDB.

### Парсинг данных

Все данные хранятся в векторном и текстовом виде в базе YDB. Хранилище заполняется запуском следующих команд:

```shell
scrapy runspider itmo_spider.py -a start_url="https://ai.itmo.ru/" specialization_source="ai_engineer"
```

```shell
scrapy runspider itmo_spider.py -a start_url="https://aiproduct.itmo.ru/" specialization_source="ai_product_manager"
```

### Запуск Telegram-бота

```shell
python main.py
```

Этот документ описывает структуру каталогов и файлов проекта `ai_itmo_qa`, предоставляя обзор его компонентов и их назначения.

## Структура каталогов

```
ai_itmo_qa/
├── agent.py
├── ai_engineer.md
├── bot.py
├── config.py
├── embeddings.py
├── itmo_spider.py
├── main.py
├── utils.py
└── data/
    ├── __init__.py
    └── ydb_adapter.py
```

## Описание файлов и каталогов

*   [`agent.py`](./agent.py): Содержит реализацию AI-агента, отвечающего за координацию различных задач и взаимодействий.
*   [`bot.py`](./bot.py): Реализует основную логику бота, обрабатывая взаимодействия с пользователем и ответы.
*   [`config.py`](./config.py): Основной конфигурационный файл проекта, хранящий учётные данные для подключения к сервисам.
*   [`embeddings.py`](./embeddings.py): Создание текстовых эмбеддингов.
*   [`itmo_spider.py`](./itmo_spider.py): Веб-краулер, предназначенный для сбора данных с доменов ИТМО. Точка входа в приложение для парсинга.
*   [`main.py`](./main.py): Основная точка входа в приложение, координирующая выполнение различных модулей.
*   [`tokenizer.json`](./tokenizer.json): JSON-файл с конфигурациями токенизатора, используемый для обработки текстовых данных.
*   [`utils.py`](./utils.py): Набор вспомогательных функций и методов, используемых в проекте.
*   [`requirements.txt`](./requirements.txt): Зависимости проекта.

### Каталог `data/`

Этот каталог предназначен для хранения модулей, связанных с данными, и, возможно, обработанных данных.

*   [`__init__.py`](./data/__init__.py): Помечает каталог `data` как Python-пакет.
*   [`ydb_adapter.py`](./data/ydb_adapter.py): Содержит код для адаптации и взаимодействия с Yandex Database.