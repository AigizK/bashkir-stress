#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для фильтрации башкирских слов по заданным правилам.
Оставляет только те слова, которые НЕ подходят ни под одно из правил.
"""

import sys
import argparse


def get_bashkir_vowels():
    """Возвращает множество гласных букв башкирского языка."""
    return set('аәоөүуыиэеяю')


def is_vowel_in_context(word, index):
    """
    Проверяет, является ли буква на данной позиции гласной с учетом контекста.
    Для 'ү' и 'у' проверяет, не стоят ли они рядом с другой гласной.
    """
    if index < 0 or index >= len(word):
        return False

    char = word[index].lower()
    vowels = get_bashkir_vowels()
    special_vowels = set('үу')
    regular_vowels = vowels - special_vowels

    # Обычные гласные всегда гласные
    if char in regular_vowels:
        return True

    # Специальные гласные - только если не рядом с обычной гласной
    if char in special_vowels:
        # Проверяем предыдущую букву
        if index > 0 and word[index-1].lower() in regular_vowels:
            return False
        # Проверяем следующую букву
        if index < len(word) - 1 and word[index+1].lower() in regular_vowels:
            return False
        return True

    return False


def find_last_vowel_index(word):
    """
    Находит индекс последней гласной в слове.
    Буквы 'ү' и 'у' не считаются гласными, если стоят рядом с другой гласной.
    Возвращает -1, если гласных нет.
    """
    vowels = get_bashkir_vowels()
    special_vowels = set('үу')
    regular_vowels = vowels - special_vowels
    last_index = -1

    for i, char in enumerate(word):
        char_lower = char.lower()

        # Обычные гласные всегда считаются гласными
        if char_lower in regular_vowels:
            last_index = i
        # Специальные гласные 'ү' и 'у' считаются гласными только если не рядом с другой гласной
        elif char_lower in special_vowels:
            # Проверяем соседние буквы
            has_adjacent_vowel = False

            # Проверяем предыдущую букву
            if i > 0 and word[i-1].lower() in regular_vowels:
                has_adjacent_vowel = True

            # Проверяем следующую букву
            if i < len(word) - 1 and word[i+1].lower() in regular_vowels:
                has_adjacent_vowel = True

            # Если нет соседней обычной гласной, то это гласная
            if not has_adjacent_vowel:
                last_index = i

    return last_index


def should_exclude_word(word, index):
    """
    Проверяет, нужно ли исключить слово по одному из правил.
    Возвращает True, если слово подходит под любое из правил (и должно быть исключено).
    """
    word_lower = word.lower()

    # Правило 1a: слово заканчивается на -ма/-мә/-мо/-ме/-мө/-мы (без проверки предыдущей буквы)
    simple_endings = ['мо', 'ме', 'мө', 'мы']
    if any(word_lower.endswith(ending) for ending in simple_endings):
        return True

    # Правило 1b: слово заканчивается на другие окончания, но перед ними не должна быть гласная
    complex_endings = ['боҙ', 'беҙ', 'быҙ', 'бөҙ', 'мен', 'мөн', 'мон', 'мын',
                       'һең', 'һөң', 'һоң', 'һың', 'һегеҙ', 'һөгөҙ', 'һоғоҙ', 'һығыҙ', 'са', 'сә']
    for ending in complex_endings:
        if word_lower.endswith(ending):
            # Проверяем букву перед окончанием
            prefix_index = len(word) - len(ending) - 1
            if prefix_index >= 0:
                # Если перед окончанием стоит гласная, правило не действует
                if is_vowel_in_context(word, prefix_index):
                    continue
            # Окончание найдено и перед ним нет гласной - исключаем слово
            return True

    question_words = ["кем", "ниндәй","нисек","ҡайҙа","ниңә","нисә","ҡасан","ҡайһы","ҡайҙан","нишләп","нимә"]

    # Правило 2: слово начинается на вопросительное слово из списка
    if any(word_lower.startswith(qword) for qword in question_words):
        return True

    # Правило 3: индекс указывает на последнюю гласную
    last_vowel_index = find_last_vowel_index(word)
    if last_vowel_index != -1 and last_vowel_index == index:
        return True

    return False


def filter_words(input_file, output_file):
    """
    Читает входной файл, фильтрует слова и записывает результат в выходной файл.
    """
    filtered_words = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) != 2:
                    print(f"Предупреждение: некорректная строка '{line}', пропускаем")
                    continue

                word = parts[0]
                try:
                    index = int(parts[1])
                except ValueError:
                    print(f"Предупреждение: некорректный индекс в строке '{line}', пропускаем")
                    continue

                # Если слово НЕ подходит ни под одно правило - добавляем в результат
                if not should_exclude_word(word, index):
                    filtered_words.append(line)

        # Записываем результат
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in filtered_words:
                f.write(line + '\n')

        print(f"Обработка завершена успешно!")
        print(f"Всего отфильтровано слов: {len(filtered_words)}")

    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Фильтрация башкирских слов по заданным правилам'
    )
    parser.add_argument('input_file', help='Входной файл со словами')
    parser.add_argument('output_file', help='Выходной файл для результата')

    args = parser.parse_args()

    filter_words(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
