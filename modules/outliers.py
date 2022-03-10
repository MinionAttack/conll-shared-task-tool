# -*- coding: utf-8 -*-
import gc
from typing import Any, Dict, List, Tuple

from tabulate import tabulate

from modules.data_loader import load_data, load_language_set
from modules.metrics import calculate_parser_subset_means, get_parsers_scores
from modules.utils import select_subsets
from resources.constants import RESULTS_TYPES_NAMES


def get_parser_outliers(parsers: List[str], section_type: str, ranking_types: List[str], treebank_set_size: int, sampling_size: int,
                        limit: int, show_best: bool, cache_samples: bool) -> None:
    if section_type == "individual":
        classification = {}
        if show_best:
            outliers_type = "best"
        else:
            outliers_type = "worst"

        languages_set = load_language_set(ranking_types, section_type, "data")
        subsets = select_subsets(languages_set, treebank_set_size, sampling_size, cache_samples)
        for ranking_type in ranking_types:
            data = load_data(ranking_type, section_type, "data", split_names=False)
            language_set_data = data.get(ranking_type).get(section_type)
            parsers_scores = get_parsers_scores(language_set_data, subsets)
            subset_means = calculate_parser_subset_means(parsers_scores)
            del parsers_scores
            parsers_ranking = get_parsers_ranking(subset_means, show_best, limit)
            del subset_means
            classification[ranking_type] = parsers_ranking
            gc.collect()

        for parser in parsers:
            print(f"\nINFO: Obtaining the {limit} {outliers_type} outliers for parser {parser} in subsets of size {treebank_set_size} for "
                  f"a sampling size of {sampling_size}")
            show_parser_outliers(parser, classification)
    else:
        print("WARNING: Global metrics have not yet been implemented")


def get_parsers_ranking(subset_means: Dict[Tuple[str, ...], Dict[str, float]],
                        show_best: bool, limit: int) -> Dict[str, List[Dict[str, Any]]]:
    print(f"INFO: Calculating the ranking of each parser based on the mean value of the scores in each subset")

    subset_rankings = get_subset_rankings(subset_means)
    parsers_ranking = rearrange_rankings(subset_rankings, show_best, limit)

    return parsers_ranking


def get_subset_rankings(subset_means: Dict[Tuple[str, ...], Dict[str, float]]) -> Dict[Tuple[str, ...], Dict[str, int]]:
    subset_ranking = {}
    for subset, parsers_means in subset_means.items():
        parsers_ranking = {}
        ranking = dict(sorted(parsers_means.items(), key=lambda item: item[1], reverse=True))
        for index, parser in enumerate(ranking.keys(), start=1):
            parsers_ranking[parser] = index
        subset_ranking[subset] = parsers_ranking

    return subset_ranking


def rearrange_rankings(subset_rankings: Dict[Tuple[str, ...], Dict[str, int]],
                       show_best: bool, limit: int) -> Dict[str, List[Dict[str, Any]]]:
    rearranged = {}
    for subset, parsers_raking in subset_rankings.items():
        for parser, score in parsers_raking.items():
            subset_positions = []
            if parser in rearranged.keys():
                other_subset_positions = rearranged.get(parser)
                other_subset_positions.append({"subset": subset, "score": score})
                rearranged[parser] = other_subset_positions
            else:
                item = {"subset": subset, "score": score}
                subset_positions.append(item)
                rearranged[parser] = subset_positions

    sorted_rearrange = {}
    for parser, ranking in rearranged.items():
        ordered = sorted(ranking, key=lambda value: value['score'], reverse=not show_best)
        sorted_rearrange[parser] = ordered[:limit]

    return sorted_rearrange


def show_parser_outliers(parser: str, classification: Dict[str, Dict[str, List[Dict[str, Any]]]]) -> None:
    for metric, parsers in classification.items():
        metric_name = RESULTS_TYPES_NAMES.get(metric)
        print(f"INFO: Showing outliers for {metric_name}")
        values = parsers.get(parser)
        table_data = tabulate_data_format(values)
        table = tabulate(table_data, headers="firstrow", tablefmt="github", stralign="left", numalign="center", floatfmt=".2f")
        print(f"\n{table}\n")


def tabulate_data_format(values: List[Dict[str, Any]]) -> List[List[Any]]:
    data = []
    headers = ["Subset", "Position"]

    data.append(headers)
    for value in values:
        subset = value.get("subset")
        score = value.get("score")
        item = [subset, score]
        data.append(item)

    return data
