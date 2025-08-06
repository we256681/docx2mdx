#!/usr/bin/env python3
"""
Скрипт для массовой конвертации всех DOCX файлов из папки template/ в MDX файлы
с сохранением структуры папок в директории markdown/
"""

import os
import sys
import glob
from pathlib import Path
from converter import parse as par
from converter import utils
from converter import prose
import yaml
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString
import re
import io

# Порядок блоков prose
orderTOP = ['Introduction paragraph', 'Source Data Product Citation', 'Version History', 'Scientific Details']
orderBOTTOM = ['Disclaimer','Limitations of Use','License']

def convert_docx_to_mdx_path_with_structure(docx_path, template_dir="template", output_dir="markdown"):
    """
    Конвертирует путь .docx файла в путь .data.mdx файла с сохранением структуры папок.

    Args:
        docx_path (str): Путь к исходному .docx файлу
        template_dir (str): Корневая папка с шаблонами
        output_dir (str): Выходная папка

    Returns:
        str: Путь к выходному .data.mdx файлу
    """
    # Получаем относительный путь от template_dir
    docx_path = Path(docx_path)
    template_path = Path(template_dir)

    # Вычисляем относительный путь
    relative_path = docx_path.relative_to(template_path)

    # Заменяем расширение
    mdx_filename = re.sub(r"\.docx$", ".data.mdx", relative_path.name)

    # Создаем полный путь для выходного файла
    output_path = Path(output_dir) / relative_path.parent / mdx_filename

    # Создаем директории если они не существуют
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return str(output_path)

def convert_single_file(docx_path, hex_or_rgb='rgb'):
    """
    Конвертирует один DOCX файл в MDX.

    Args:
        docx_path (str): Путь к DOCX файлу
        hex_or_rgb (str): Формат цвета ('rgb' или 'hex')

    Returns:
        str: Путь к созданному MDX файлу или None в случае ошибки
    """
    try:
        print(f"Конвертирую: {docx_path}")

        # Извлекаем данные из DOCX файла
        table_0, table_1, table_optional, prose_content = par.retrieve_all_docx_data(docx_path)

        # Строим non-prose секцию
        output = prose.construct_non_prose_section(table_0, table_1, prose_content, hex_or_rgb)

        # Определяем путь для выходного файла с сохранением структуры
        outfile = convert_docx_to_mdx_path_with_structure(docx_path)

        # Собираем MDX контент
        mdx_parts = []

        # 1. Добавляем YAML frontmatter
        yaml_instance = utils.get_yaml_instance()
        string_stream = io.StringIO()
        yaml_instance.dump(output, string_stream)
        frontmatter_yaml = f"---\n{string_stream.getvalue()}---\n\n"
        mdx_parts.append(frontmatter_yaml)

        # 2. Добавляем MDX content headers
        mdx_parts.append(prose.generate_mdx_content_headers(table_1))

        # 3. Добавляем ОБЯЗАТЕЛЬНЫЕ TOP prose блоки
        for header in orderTOP:
            if header in prose_content:
                mdx_parts.append(prose.format_prose_block(prose_content, header))

        # 4. Добавляем ОПЦИОНАЛЬНЫЕ prose блоки
        if len(table_optional) > 0:
            for k, v in table_optional.items():
                if isinstance(table_optional[k], list) and len(table_optional[k]) > 0 and isinstance(table_optional[k][0], dict):
                    key_ = list(table_optional[k][0].keys())[0]
                    mdx_parts.append(prose.format_prose_block(table_optional[k][0], key_))

        # 5. Добавляем ОБЯЗАТЕЛЬНЫЕ BOTTOM prose блоки
        for header in orderBOTTOM:
            if header in prose_content:
                mdx_parts.append(prose.format_prose_block(prose_content, header))

        # Сохраняем финальный MDX файл
        final_mdx_content = "".join(mdx_parts)
        utils.save_mdx_content(outfile, final_mdx_content)

        # Пост-обработка
        utils.debug_mdx_file(outfile)
        utils.remove_trailing_whitespace(outfile)

        print(f"✓ Успешно сконвертирован: {outfile}")
        return outfile

    except Exception as e:
        print(f"✗ Ошибка при конвертации {docx_path}: {str(e)}")
        return None

def find_all_docx_files(template_dir="template"):
    """
    Находит все DOCX файлы в указанной директории и её подпапках.

    Args:
        template_dir (str): Директория для поиска

    Returns:
        list: Список путей к DOCX файлам
    """
    docx_files = []
    template_path = Path(template_dir)

    if not template_path.exists():
        print(f"Папка {template_dir} не существует!")
        return docx_files

    # Ищем все .docx файлы рекурсивно
    for docx_file in template_path.rglob("*.docx"):
        # Пропускаем временные файлы Word (начинающиеся с ~$)
        if not docx_file.name.startswith("~$"):
            docx_files.append(str(docx_file))

    return docx_files

def main():
    """
    Основная функция для массовой конвертации.
    """
    # Параметры по умолчанию
    template_dir = "template"
    hex_or_rgb = "rgb"

    # Обработка аргументов командной строки
    if len(sys.argv) > 1:
        hex_or_rgb = sys.argv[1]

    print(f"Начинаю массовую конвертацию DOCX файлов из папки '{template_dir}'")
    print(f"Формат цвета: {hex_or_rgb}")
    print("-" * 60)

    # Находим все DOCX файлы
    docx_files = find_all_docx_files(template_dir)

    if not docx_files:
        print(f"В папке '{template_dir}' не найдено DOCX файлов.")
        return

    print(f"Найдено {len(docx_files)} DOCX файлов:")
    for docx_file in docx_files:
        print(f"  - {docx_file}")
    print("-" * 60)

    # Конвертируем каждый файл
    successful_conversions = 0
    failed_conversions = 0

    for docx_file in docx_files:
        result = convert_single_file(docx_file, hex_or_rgb)
        if result:
            successful_conversions += 1
        else:
            failed_conversions += 1
        print()  # Пустая строка для разделения

    # Итоговая статистика
    print("=" * 60)
    print(f"Конвертация завершена!")
    print(f"Успешно: {successful_conversions}")
    print(f"С ошибками: {failed_conversions}")
    print(f"Всего: {len(docx_files)}")

    if successful_conversions > 0:
        print(f"\nРезультаты сохранены в папке 'markdown/' с сохранением структуры.")

if __name__ == '__main__':
    main()