---
description: Repository Information Overview
alwaysApply: true
---

# DOCX to MDX Converter Information

## Summary
Инструмент для конвертации структурированных DOCX файлов в формат MDX (Markdown + JSX), сохраняющий метаданные, структуру контента и цветовое форматирование. Специально разработан для наборов данных NASA VEDA, обеспечивая правильное преобразование пространственных данных с поддержкой динамического количества слоев.

## Structure
- **converter/**: Основной модуль с функциями для парсинга и преобразования DOCX в MDX
- **markdown/**: Директория для сохранения сгенерированных MDX файлов
- **setup/**: Файлы для настройки окружения (conda, requirements)
- **template/**: Шаблоны DOCX файлов для примера структуры

## Language & Runtime
**Language**: Python
**Version**: Python 3.10 (рекомендуется)
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- python-docx==1.1.2 (работа с DOCX файлами)
- ruamel.yaml==0.18.10 (продвинутая работа с YAML)
- lxml==5.3.1 (XML парсинг)
- PyYAML==6.0.2 (работа с YAML)

## Build & Installation
**Установка с conda**:
```bash
conda env create -f setup/docx2mdx_env.yaml
conda activate docx2mdx
```

**Установка с pip**:
```bash
pip install -r setup/requirements.txt
```

## Usage
**Конвертация DOCX в MDX**:
```bash
python dump.py /path/to/input.docx rgb_or_hex_string
```

**Примеры**:
```bash
python dump.py "template/test_LIS.docx" "rgb"
# или
python dump.py "template/test_LIS.docx" "hex"
```

## Main Components

### Parser Module
**Файл**: `converter/parse.py`
**Функциональность**: Извлечение данных из DOCX файлов, включая таблицы, метаданные и текстовые блоки.
**Ключевые функции**:
- `retrieve_all_docx_data()`: Извлечение всех данных из DOCX
- `parse_layer_information()`: Обработка информации о слоях данных
- `parse_media_alt_text()`: Извлечение метаданных медиа

### Prose Module
**Файл**: `converter/prose.py`
**Функциональность**: Форматирование текстовых блоков и создание MDX структуры.
**Ключевые функции**:
- `construct_non_prose_section()`: Создание YAML frontmatter
- `format_prose_block()`: Форматирование текстовых блоков
- `generate_mdx_content_headers()`: Генерация заголовков MDX

### Utils Module
**Файл**: `converter/utils.py`
**Функциональность**: Вспомогательные функции для работы с файлами и конвертации цветов.
**Ключевые функции**:
- `color_converter()`: Конвертация между форматами цветов (HEX ↔ RGB)
- `convert_docx_to_mdx_path()`: Преобразование путей файлов
- `save_mdx_content()`: Сохранение MDX контента

### Main Script
**Файл**: `dump.py`
**Функциональность**: Основной скрипт для запуска конвертации.
**Процесс**:
1. Извлечение данных из DOCX
2. Построение структуры MDX
3. Сборка и форматирование контента
4. Сохранение результата в директории markdown/