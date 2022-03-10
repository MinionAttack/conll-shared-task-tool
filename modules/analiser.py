# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import List, Dict, Any

from tabulate import tabulate


def get_duplicate_elements(file: str) -> None:
    print("Searching for duplicate elements in multi-opinion sentences")

    file_path = Path.home().joinpath(Path(file))
    with open(file_path) as sentences_file:
        sentences = json.load(sentences_file)
    file_name = file_path.stem
    find_duplicates(sentences, file_name)


def find_duplicates(sentences: List[Dict[str, Any]], file_name: str) -> None:
    print(f"Finding duplicate elements in {file_name} file")

    opinion_occurrences = {}
    similar_parts_occurrences = {}
    for sentence in sentences:
        opinions = sentence.get("opinions")
        if opinions:
            count_occurrences(opinions, opinion_occurrences)
            count_similar_parts(opinions, similar_parts_occurrences)
        else:
            continue

    ordered_opinion_occurrences = dict(sorted(opinion_occurrences.items()))
    ordered_similar_parts_occurrences = dict(sorted(similar_parts_occurrences.items()))

    display_occurrences(ordered_opinion_occurrences, ordered_similar_parts_occurrences, "Number of opinions", "Occurrences",
                        "Number of times a sentence shares parts")


def count_occurrences(opinions: List[Dict[str, Any]], occurrences: Dict[int, int]) -> None:
    length = len(opinions)
    if length in occurrences.keys():
        occurrences[length] += 1
    else:
        occurrences[length] = 1


def count_similar_parts(opinions: List[Dict[str, Any]], similar_occurrences: Dict[int, int]) -> None:
    sources = set()
    targets = set()
    expressions = set()

    number_opinions = len(opinions)
    initialise_counter(number_opinions, similar_occurrences)

    collision = False
    for opinion in opinions:
        source_part = opinion.get("Source")
        target_part = opinion.get("Target")
        expression_part = opinion.get("Polar_expression")

        if not empty_part(source_part) and not collision:
            collision = add_elements(source_part, sources)
        if not empty_part(target_part) and not collision:
            collision = add_elements(target_part, targets)
        if not empty_part(expression_part) and not collision:
            collision = add_elements(expression_part, expressions)

        if collision:
            similar_occurrences[number_opinions] += 1
            break


def initialise_counter(number_opinions: int, occurrences: Dict[int, int]) -> None:
    if number_opinions not in occurrences.keys():
        occurrences[number_opinions] = 0


def empty_part(opinion_part: List[List[str]]) -> bool:
    words = opinion_part[0]
    positions = opinion_part[1]

    if words and positions:
        return False
    else:
        return True


def add_elements(opinion_part: List[List[str]], parts: set) -> bool:
    words = opinion_part[0]
    positions = opinion_part[1]

    for word, position in zip(words, positions):
        pair = (word, position)
        if pair in parts:
            return True
        else:
            parts.add(pair)

    return False


def display_occurrences(occurrences: Dict[int, int], shared_parts: Dict[int, int], first_header: str, second_header: str,
                        third_header: str) -> None:
    table_data = tabulate_data_format(occurrences, shared_parts, first_header, second_header, third_header)
    table = tabulate(table_data, headers="firstrow", tablefmt="github", stralign="left", numalign="center", floatfmt=".2f")
    print(f"\n{table}\n")


def tabulate_data_format(occurrences: Dict[int, int], shared_parts: Dict[int, int], first_header: str, second_header: str,
                         third_header: str) -> List[List[Any]]:
    data = []
    headers = [first_header, second_header, third_header]

    data.append(headers)
    for (key, value), (key2, value2) in zip(occurrences.items(), shared_parts.items()):
        item = [key, value, value2]
        data.append(item)

    return data
