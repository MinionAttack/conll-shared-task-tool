# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set

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

    headers = ["Number of opinions", "Occurrences", "Number of times a sentence shares parts"]
    display_occurrences(ordered_opinion_occurrences, ordered_similar_parts_occurrences, headers)

    detailed_parts_occurrences = {}
    count_detailed_similar_parts(sentences, detailed_parts_occurrences)

    display_detailed_occurrences(detailed_parts_occurrences)


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
        source = opinion.get("Source")
        target = opinion.get("Target")
        expression = opinion.get("Polar_expression")

        if not empty_part(source) and not collision:
            collision = add_elements(source, sources)
        if not empty_part(target) and not collision:
            collision = add_elements(target, targets)
        if not empty_part(expression) and not collision:
            collision = add_elements(expression, expressions)

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


def count_detailed_similar_parts(sentences: List[Dict[str, Any]], detailed_occurrences: Dict[str, List[Dict[str, Any]]]) -> None:
    for sentence_index, sentence in enumerate(sentences, start=1):
        sources = []
        targets = []
        expressions = []

        opinions = sentence.get("opinions")
        opinion_parts = ["Source", "Target", "Polar_expression"]
        for opinion_part in opinion_parts:
            for opinion_index, opinion in enumerate(opinions, start=1):
                collisions = get_collisions(opinion_part, opinion_index, opinion, opinions)
                if collisions:
                    if opinion_part == "Source":
                        if not is_sublist(sources, collisions) and not is_index_part_collision(sources, collisions):
                            sources.append(collisions)
                    elif opinion_part == "Target":
                        if not is_sublist(targets, collisions) and not is_index_part_collision(targets, collisions):
                            targets.append(collisions)
                    elif opinion_part == "Polar_expression":
                        if not is_sublist(expressions, collisions) and not is_index_part_collision(expressions, collisions):
                            expressions.append(collisions)
                    else:
                        continue
                else:
                    continue

            if opinion_part == "Source" and sources:
                data = {"collisions": sources, "opinions": len(opinions)}
                add_collisions(opinion_part, data, detailed_occurrences)
            elif opinion_part == "Target" and targets:
                data = {"collisions": targets, "opinions": len(opinions)}
                add_collisions(opinion_part, data, detailed_occurrences)
            elif opinion_part == "Polar_expression" and expressions:
                data = {"collisions": expressions, "opinions": len(opinions)}
                add_collisions(opinion_part, data, detailed_occurrences)
            else:
                continue


def get_collisions(part: str, opinion_index: int, actual_opinion: Dict[str, Any], other_opinions: List[Dict[str, Any]]) -> List[int]:
    actual_opinion_part = actual_opinion.get(part)

    part_collisions = []
    if not empty_part(actual_opinion_part):
        actual_opinion_part_data = get_opinion_part_data(actual_opinion_part)
        others = other_opinions[opinion_index::1]
        no_collisions = 0
        for other_index, other_opinion in enumerate(others, start=1):
            other_opinion_part = other_opinion.get(part)
            if not empty_part(other_opinion_part):
                other_opinion_part_data = get_opinion_part_data(other_opinion_part)
                if actual_opinion_part_data == other_opinion_part_data:
                    # [1,2,1,3,1,4] -> [1,2,3,4]
                    if opinion_index in part_collisions:
                        part_collisions.append(opinion_index + other_index)
                    else:
                        part_collisions.append(opinion_index)
                        part_collisions.append(opinion_index + other_index)
                else:
                    no_collisions += 1
            else:
                continue
        if no_collisions == len(others):
            part_collisions.append(opinion_index)

        return part_collisions
    else:
        return part_collisions


def get_opinion_part_data(opinion_part: List[List[str]]) -> Set[Tuple[str, str]]:
    words = opinion_part[0]
    positions = opinion_part[1]

    data = set()
    for word, position in zip(words, positions):
        pair = (word, position)
        data.add(pair)

    return data


def is_index_part_collision(reference: List[List[int]], compare: List[int]) -> bool:
    if len(compare) == 1:
        for collisions in reference:
            if compare[0] in collisions:
                return True
            else:
                continue
    else:
        return False

    return False


def is_sublist(reference: List[List[int]], compare: List[int]):
    # This removes the case when [[1,2,3], [2,3]].
    # In this case [2,3] should not be added.

    for collisions in reference:
        first_index = -1
        for collisions_index in range(len(collisions)):
            if first_index >= 0:
                compare_index = collisions_index - first_index
                if collisions[collisions_index] != compare[compare_index]:
                    return False
                if compare_index == len(compare) - 1:
                    return True
            elif collisions[collisions_index] == compare[0]:
                first_index = collisions_index

    return False


def add_collisions(part_name: str, part_collisions: Dict[str, Any], all_collisions: Dict[str, List[Dict[str, Any]]]) -> None:
    if part_name in all_collisions.keys():
        values = all_collisions[part_name]
        values.append(part_collisions)
        all_collisions[part_name] = values
    else:
        all_collisions[part_name] = [part_collisions]


def display_occurrences(occurrences: Dict[int, int], shared_parts: Dict[int, int], headers: List[str]) -> None:
    table_data = tabulate_data_format(occurrences, shared_parts, headers)
    table = tabulate(table_data, headers="firstrow", tablefmt="github", stralign="left", numalign="center", floatfmt=".2f")
    print(f"\n{table}\n")


def tabulate_data_format(occurrences: Dict[int, int], shared_parts: Dict[int, int], headers: List[str]) -> List[List[Any]]:
    data = [headers]
    for (key, value), (key2, value2) in zip(occurrences.items(), shared_parts.items()):
        item = [key, value, value2]
        data.append(item)

    return data


def display_detailed_occurrences(occurrences: Dict[str, List[Dict[str, Any]]]) -> None:
    scores = get_scores(occurrences)
    all_scores = get_all_scores(occurrences)
    not_all_scores = get_not_all_scores(occurrences)

    for (score_name, score_part), (all_name, all_part), (not_name, not_part) in zip(scores.items(), all_scores.items(),
                                                                                    not_all_scores.items()):
        if score_name == all_name and score_name == not_name:
            table_data = get_table_data(score_name, score_part, all_part, not_part)
            table = tabulate(table_data, headers="firstrow", tablefmt="github", stralign="left", numalign="center", floatfmt=".2f")
            print(f"\n{table}\n")
        else:
            print(f"WARNING: The structure does not match: {score_name} - {all_name}, skipping")


def get_scores(all_collisions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[int, int]]:
    scores = {'Source': {}, 'Target': {}, 'Polar_expression': {}}

    for part_name, collisions in all_collisions.items():
        name_score = scores.get(part_name)
        for item in collisions:
            occurrences = item["collisions"]
            for occurrence in occurrences:
                size = len(occurrence)
                if size in name_score.keys():
                    name_score[size] += 1
                else:
                    name_score[size] = 1

        ordered_scores = dict(sorted(name_score.items()))
        scores[part_name] = ordered_scores

    return scores


def get_all_scores(all_collisions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[int, int]]:
    all_scores = {'Source': {}, 'Target': {}, 'Polar_expression': {}}

    for part_name, collisions in all_collisions.items():
        name_score = all_scores.get(part_name)
        for item in collisions:
            occurrences = item["collisions"]
            number_opinions = item["opinions"]
            for occurrence in occurrences:
                if len(occurrence) == number_opinions:
                    if number_opinions in name_score.keys():
                        name_score[number_opinions] += 1
                    else:
                        name_score[number_opinions] = 1
                else:
                    continue

    return all_scores


def get_not_all_scores(all_collisions: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[int, int]]:
    not_all_scores = {'Source': {}, 'Target': {}, 'Polar_expression': {}}

    for part_name, collisions in all_collisions.items():
        name_score = not_all_scores.get(part_name)
        for item in collisions:
            occurrences = item["collisions"]
            number_opinions = item["opinions"]
            for occurrence in occurrences:
                if len(occurrence) != number_opinions:
                    if number_opinions in name_score.keys() and len(occurrence) in name_score.keys():
                        if occurrence not in name_score[len(occurrence)]:
                            name_score[len(occurrence)].append(occurrence)
                        else:
                            continue
                    else:
                        name_score[len(occurrence)] = [occurrence]
                else:
                    continue

    for name, values in not_all_scores.items():
        for opinions, items in values.items():
            elements = len(items)
            values[opinions] = elements

        ordered = dict(sorted(values.items()))
        not_all_scores[name] = ordered

    return not_all_scores


def get_table_data(score_name: str, scores: Dict[int, int], all_scores: Dict[int, int], not_scores: Dict[int, int]) -> List[List[Any]]:
    headers = []

    for score_key in scores.keys():
        headers.append(f"C{score_key}")
        if score_key in all_scores.keys():
            headers.append(f"All C{score_key}")
        if score_key in not_scores.keys():
            headers.append(f"Not All C{score_key}")

    data = [headers]
    values = [score_name]

    for score_key, score_value in scores.items():
        values.append(score_value)
        if score_key in all_scores.keys():
            all_value = all_scores[score_key]
            values.append(all_value)
        if score_key in not_scores.keys():
            not_value = not_scores[score_key]
            values.append(not_value)

    data.append(values)

    return data


def get_not_all_data(name: str, part: Dict[int, int]) -> List[List[Any]]:
    headers = []

    for score_key in part.keys():
        headers.append(f"Not All C{score_key}")

    data = [headers]
    values = [name]

    for score_value in part.values():
        values.append(score_value)

    data.append(values)

    return data
