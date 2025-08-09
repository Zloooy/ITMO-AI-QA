# ai_itmo_qa Project Structure

This document outlines the directory and file structure of the `ai_itmo_qa` project, providing an overview of its components and their purposes.

## Directory Structure

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

## File and Directory Descriptions

*   [`agent.py`](ai_itmo_qa/agent.py): Contains the implementation of the AI agent, likely responsible for orchestrating various tasks and interactions.
*   [`bot.py`](ai_itmo_qa/bot.py): Implements the core logic for the bot, handling user interactions and responses.
*   [`config.py`](ai_itmo_qa/config.py): The main configuration file for the project, storing settings and parameters.
*   [`embeddings.py`](ai_itmo_qa/embeddings.py): Handles the generation and management of text embeddings, crucial for natural language processing tasks.
*   [`itmo_spider.py`](ai_itmo_qa/itmo_spider.py): A web crawler specifically designed to scrape data from ITMO-related sources.
*   [`main.py`](ai_itmo_qa/main.py): The primary entry point of the application, coordinating the execution of different modules.
*   [`tokenizer.json`](ai_itmo_qa/tokenizer.json): A JSON file containing tokenizer configurations, used for processing text data.
*   [`utils.py`](ai_itmo_qa/utils.py): A collection of utility functions and helper methods used across the project.

### `data/` Directory

This directory is intended for storing data-related modules and possibly processed data.

*   [`__init__.py`](ai_itmo_qa/data/__init__.py): Marks the `data` directory as a Python package.
*   [`ydb_adapter.py`](ai_itmo_qa/data/ydb_adapter.py): Contains code for adapting and interacting with Yandex Database.