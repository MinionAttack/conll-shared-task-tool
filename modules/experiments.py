# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Tuple

from tabulate import tabulate

from modules.data_loader import load_data, load_language_set
from modules.metrics import calculate_parser_subset_means, get_parsers_ranking, get_parsers_scores, select_subsets
from resources.constants import RESULTS_TYPES_NAMES


def measure_experiments_metrics(ranking_type: List[str], section_type: str, treebank_set_size: int, sampling_size: int,
                                cache_samples: bool) -> None:
    print(f"INFO: Calculating metrics of the experiments on set {section_type}")

    if section_type == "individual":
        languages_set = load_language_set(ranking_type, section_type, "experiments")
        subsets = select_subsets(languages_set, treebank_set_size, sampling_size, cache_samples)
        for ranking in ranking_type:
            data = load_data(ranking, section_type, "experiments", split_names=False)
            language_set = data.get(ranking).get(section_type)
            calculate_classification(ranking, language_set, subsets)
    else:
        print("WARNING: Global metrics have not yet been implemented")


def calculate_classification(ranking_type: str, language_set: Dict[str, List[Tuple[str, str, float]]], subsets: List[List[str]]) -> None:
    ranking_name = RESULTS_TYPES_NAMES.get(ranking_type)
    print(f"INFO: Calculation of parser classification for {ranking_name}")

    parsers_scores = get_parsers_scores(language_set, subsets)
    subset_means = calculate_parser_subset_means(parsers_scores)
    parsers_ranking = get_parsers_ranking(subset_means)
    parsers_classification = count_positions_occurrences(parsers_ranking)
    display_classification_results(parsers_classification)


def count_positions_occurrences(parsers_ranking: Dict[str, List[int]]) -> Dict[str, Dict[int, int]]:
    print(f"INFO: Calculating the number of occurrences for each position")

    parsers_number = len(list(parsers_ranking.keys()))
    parsers_classification = {}
    for parser, positions in parsers_ranking.items():
        classification = {}
        for number in range(1, parsers_number + 1):
            occurrences = positions.count(number)
            classification[number] = occurrences
        parsers_classification[parser] = classification

    return parsers_classification


def display_classification_results(parsers_classification: Dict[str, Dict[int, int]]) -> None:
    print(f"INFO: Showing the classification")

    table_data = tabulate_data_format(parsers_classification)
    table = tabulate(table_data, headers="firstrow", tablefmt="github", stralign="left", numalign="center", floatfmt=".2f")
    print(f"\n{table}\n")


def tabulate_data_format(parsers_classification: Dict[str, Dict[int, int]]) -> List[List[Any]]:
    data = []
    headers = []

    for parser, classification in parsers_classification.items():
        parser_data = []
        if not headers:
            headers = [f"Position {item}" for item in list(classification.keys())]
        parser_data.append(parser)
        classification = list(classification.values())
        parser_data.extend(classification)
        data.append(parser_data)

    data.insert(0, headers)

    return data
