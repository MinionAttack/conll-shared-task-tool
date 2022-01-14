# -*- coding: utf-8 -*-

from enum import Enum
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any, Dict, List, Tuple

from matplotlib.pyplot import figure, savefig, yticks
from numpy import arange
from pandas import DataFrame
from seaborn import boxplot
from tabulate import tabulate

from modules.data_loader import load_data, load_language_set
from modules.utils import select_subsets
from resources.constants import RESULTS_TYPES_NAMES


class SortResults(Enum):
    PARSER_NAME = 0
    MAXIMUM = 1
    MINIMUM = 2
    MEAN = 3
    MEDIAN = 4
    STANDARD_DEVIATION = 5


def measure_shared_task_metrics(ranking_type: List[str], section_type: str, treebank_set_size: int, sampling_size: int,
                                cache_samples: bool) -> None:
    print(f"INFO: Calculating metrics on set {section_type}")

    if section_type == "individual":
        languages_set = load_language_set(ranking_type, section_type, "data")
        subsets = select_subsets(languages_set, treebank_set_size, sampling_size, cache_samples)
        for ranking in ranking_type:
            data = load_data(ranking, section_type, "data", split_names=True)
            language_set_data = data.get(ranking).get(section_type)
            calculate_performance_metric(ranking, language_set_data, subsets, "data")
    else:
        print("WARNING: Global metrics have not yet been implemented")


def calculate_performance_metric(ranking_type: str, language_set_data: Dict[str, List[Tuple[str, str, float]]], subsets: List[List[str]],
                                 folder_name: str) -> None:
    ranking_name = RESULTS_TYPES_NAMES.get(ranking_type)
    print(f"INFO: Calculation of parser performance metrics for {ranking_name}")

    parsers_scores = get_parsers_scores(language_set_data, subsets)
    subset_means = calculate_parser_subset_means(parsers_scores)
    parsers_ranking = get_parsers_ranking(subset_means)
    ranking_metrics = calculate_ranking_metrics(parsers_ranking)
    mean_scores_metrics = calculate_mean_metrics(subset_means)

    ordered_parsers = display_metrics_results(ranking_metrics, "ranking")
    generate_chart(ranking_type, parsers_ranking, ordered_parsers, folder_name)

    display_metrics_results(mean_scores_metrics, "scores")


def get_parsers_scores(language_set: Dict[str, List[Tuple[str, str, float]]],
                       subsets: List[List[str]]) -> Dict[Tuple[str, ...], Dict[str, List[float]]]:
    print(f"INFO: Obtaining the score for each parser in the subsets")

    parsers_scores = {}
    for subset in subsets:
        parser_positions = {}
        for language_subset in subset:
            treebank_ranking = language_set.get(language_subset)
            for treebank in treebank_ranking:
                parser = treebank[0]
                score = treebank[2]
                if parser in parser_positions.keys():
                    other_positions = parser_positions[parser]
                    other_positions.append(score)
                    parser_positions[parser] = other_positions
                else:
                    parser_positions[parser] = [score]
        parsers_scores[tuple(subset)] = parser_positions

    return parsers_scores


def calculate_parser_subset_means(parsers_scores: Dict[Tuple[str, ...], Dict[str, List[float]]]) -> Dict[Tuple[str, ...], Dict[str, float]]:
    print(f"INFO: Calculating the mean of the scores for each parser in each subset")

    results = {}
    for subset, ranking in parsers_scores.items():
        parsers_mean_score = {}
        for parser, scores in ranking.items():
            mean_value = mean(scores)
            parsers_mean_score[parser] = mean_value
        results[subset] = parsers_mean_score

    return results


def get_parsers_ranking(subset_means: Dict[Tuple[str, ...], Dict[str, float]]) -> Dict[str, List[int]]:
    print(f"INFO: Calculating the ranking of each parser based on the mean value of the scores in each subset")

    parsers_ranking = {}
    for subset, parsers_means in subset_means.items():
        ranking = dict(sorted(parsers_means.items(), key=lambda item: item[1], reverse=True))
        for index, parser in enumerate(ranking.keys(), start=1):
            if parser in parsers_ranking.keys():
                other_rankings = parsers_ranking[parser]
                other_rankings.append(index)
                parsers_ranking[parser] = other_rankings
            else:
                parsers_ranking[parser] = [index]

    return parsers_ranking


def calculate_ranking_metrics(parsers_ranking: Dict[str, List[int]]) -> Dict[str, Dict[str, float]]:
    print(f"INFO: Calculating ranking metrics")

    parsers_ranking_metrics = calculate_metrics(parsers_ranking)

    return parsers_ranking_metrics


def calculate_mean_metrics(subset_means: Dict[Tuple[str, ...], Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    print(f"INFO: Calculating scores metrics")

    grouped_parser_means = group_parser_means(subset_means)
    parser_statistics = calculate_metrics(grouped_parser_means)

    return parser_statistics


def group_parser_means(subset_means: Dict[Tuple[str, ...], Dict[str, float]]) -> Dict[str, List[float]]:
    grouped_parser_means = {}

    for subset, metrics in subset_means.items():
        for parser, score in metrics.items():
            if parser in grouped_parser_means.keys():
                previous_metrics = grouped_parser_means[parser]
                previous_metrics.append(score)
                grouped_parser_means[parser] = previous_metrics
            else:
                grouped_parser_means[parser] = [score]

    return grouped_parser_means


def calculate_metrics(values: Dict[str, List[Any]]) -> Dict[str, Dict[str, Any]]:
    metrics = {}

    for parser, means in values.items():
        maximum_value = max(means)
        minimum_value = min(means)
        mean_value = mean(means)
        median_value = median(means)
        standard_deviation_value = stdev(means)
        metrics[parser] = {'minimum': minimum_value, 'maximum': maximum_value, 'mean': mean_value, 'median': median_value,
                           'standard_deviation': standard_deviation_value}

    return metrics


def display_metrics_results(calculated_metrics: Dict[str, Dict[str, float]], metric_type: str) -> List[str]:
    print(f"INFO: Showing the results of the metrics for: {metric_type}")

    table_data, ordered_parsers = tabulate_data_format(calculated_metrics)
    table = tabulate(table_data, headers="firstrow", tablefmt="github", stralign="left", numalign="center", floatfmt=".2f")
    print(f"\n{table}\n")

    return ordered_parsers


def tabulate_data_format(metrics: Dict[str, Dict[str, float]]) -> Tuple[List[List[Any]], List[str]]:
    data = []
    headers = []

    for parser, values in metrics.items():
        parser_data = []
        if not headers:
            headers = list(values.keys())
        parser_data.append(parser)
        values = list(values.values())
        parser_data.extend(values)
        data.append(parser_data)

    # For fields other than PARSER_NAME, convert the element to float instead of str
    data.sort(key=lambda item: float(item[SortResults.MEDIAN.value]))
    ordered_parsers = [item[SortResults.PARSER_NAME.value] for item in data]
    data.insert(0, headers)

    return data, ordered_parsers


def generate_chart(ranking_type: str, parser_positions: Dict[str, List[int]], ordered_parsers: List[str], folder_name: str) -> None:
    print(f"INFO: Generating chart")

    reordered_parsers = {}
    for parser in ordered_parsers:
        if " " in parser:
            formatted = parser.replace(" ", "\n")
        elif "-" in parser:
            formatted = parser.replace("-", "\n")
        else:
            formatted = parser
        if "1.2" in formatted:
            formatted = formatted.replace("\n1.2", "")

        positions = parser_positions.get(parser)
        reordered_parsers[formatted] = positions

    dataframe = DataFrame.from_dict(reordered_parsers)
    figure(figsize=(15, 8))
    yticks(arange(0, 30, 1))
    graph = boxplot(data=dataframe)
    title = RESULTS_TYPES_NAMES.get(ranking_type)
    # graph.set(title=title)
    graph.set_xticklabels(graph.get_xticklabels(), rotation=90, fontsize=12)
    graph.invert_yaxis()
    graph.set(ylabel="Ranking")
    # graph.tick_params(labelbottom=False, bottom=False)
    Path(__file__).parent.parent.joinpath("charts").joinpath(folder_name).mkdir(parents=True, exist_ok=True)
    file_path = Path(__file__).parent.parent.joinpath("charts").joinpath(folder_name).joinpath(f"{title}.png")

    savefig(file_path, bbox_inches='tight')
