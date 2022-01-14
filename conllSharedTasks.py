#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from argparse import ArgumentParser, Namespace
from distutils import util
from typing import List

from modules.experiments import measure_experiments_metrics
from modules.metrics import measure_shared_task_metrics
from modules.outlier_statistics import get_outlier_statistics
from modules.outliers import get_parser_outliers
from modules.rankings import get_rankings


def main() -> None:
    parser = ArgumentParser(description='Gets the rankings and shows some metrics on the CoNLL Shared Task of the specified year or in '
                                        'custom experiments.')
    subparsers = parser.add_subparsers(title='Commands', dest='command')

    cache_sample_help = "Indicates whether the generated samples are cached or not. If caching is indicated, previously generated " \
                        "samples shall be loaded unless such samples do not exist, which shall be generated and then cached. When " \
                        "loading samples from the cache, the size of the treebank and the sample size are checked to ensure that they " \
                        "match the given values."

    subparser = subparsers.add_parser('rankings', help='Get the classification results of the specified type and year from the website.')
    subparser.add_argument('--type', type=str, choices=['las', 'mlas', 'blex', 'uas', 'clas', 'upos', 'xpos', 'ufeats', 'alltags',
                                                        'lemmas', 'sentences', 'words', 'tokens'], required=True,
                           help="The type of the ranking.")
    subparser.add_argument('--year', type=int, choices=[17, 18], required=True, help="The year of the shared task.")

    subparser = subparsers.add_parser('metrics', help='Gets the indicated metric on the selected CoNLL Shared Task dataset.')
    subparser.add_argument('--ranking', type=str, choices=['las', 'mlas', 'blex', 'uas', 'clas', 'upos', 'xpos', 'ufeats', 'alltags',
                                                           'lemmas', 'sentences', 'words', 'tokens'], nargs='+', required=True,
                           help="The ranking(s) to compare scores. To indicate several at the same time, they must be separated by spaces.")
    subparser.add_argument('--section', type=str, choices=['individual', 'group'], required=True,
                           help="The type of the section on which to calculate the metric.")
    subparser.add_argument('--treebank_set_size', type=int, required=True, help="The size of the treebank sets. There are 82 different "
                                                                                "treebanks.")
    subparser.add_argument('--sampling_size', type=int, required=True, help="The number of samples on which to generate the metric. "
                                                                            "Very large numbers may cause the metric to take time to "
                                                                            "calculate. Repetition of treebanks between sets are allowed, "
                                                                            "but only N-1 treebanks shall be repeated between sets. The "
                                                                            "maximum number of samples available with 82 treebanks for a "
                                                                            "treebank set size (N) are 82! / (N! x (82 - N)!).")
    subparser.add_argument('--cache_samples', type=str, choices=["yes", "no"], required=True, help=cache_sample_help)

    subparser = subparsers.add_parser('experiments', help='For a ranking, gets a leaderboard of the parsers used in the customised '
                                                          'experiments.')
    subparser.add_argument('--ranking', type=str, choices=['las', 'uas'], nargs='+', required=True,
                           help="The ranking(s) to compare scores. To indicate several at the same time, they must be separated by spaces.")
    subparser.add_argument('--section', type=str, choices=['individual'], required=True, help="The type of the section on which to "
                                                                                              "calculate the metric.")
    subparser.add_argument('--treebank_set_size', type=int, required=True, help="The size of the treebank sets. There are 47 different "
                                                                                "treebanks.")
    subparser.add_argument('--sampling_size', type=int, required=True, help="The number of samples on which to generate the metric. "
                                                                            "Very large numbers may cause the metric to take time to "
                                                                            "calculate. Repetition of treebanks between sets are allowed, "
                                                                            "but only N-1 treebanks shall be repeated between sets. The "
                                                                            "maximum number of samples available with 47 treebanks for a "
                                                                            "treebank set size (N) are 47! / (N! x (47 - N)!).")
    subparser.add_argument('--cache_samples', type=str, choices=["yes", "no"], required=True, help=cache_sample_help)

    subparser = subparsers.add_parser('outliers', help='For a given parser, it shows the subsets in which it obtained its best position.')
    subparser.add_argument('--parser', type=str, choices=['AntNLP (Shanghai)', 'ArmParser (Yerevan)', 'BASELINE UDPipe 1.2 (Praha)',
                                                          'BOUN (İstanbul)', 'CEA LIST (Paris)', 'CUNI x-ling (Praha)',
                                                          'Fudan (Shanghai)', 'HIT-SCIR (Harbin)', 'HUJI (Yerushalayim)',
                                                          'IBM NY (Yorktown Heights)', 'ICS PAS (Warszawa)', 'iParse (Pittsburgh)',
                                                          'KParse (İstanbul)', 'LATTICE (Paris)', 'LeisureX (Shanghai)',
                                                          'NLP-Cube (București)', "ONLP lab (Ra'anana)", 'ParisNLP (Paris)',
                                                          'Phoenix (Shanghai)', 'SLT-Interactions (Bengaluru)', 'SParse (İstanbul)',
                                                          'Stanford (Stanford)', 'TurkuNLP (Turku)', 'UDPipe Future (Praha)',
                                                          'UniMelb (Melbourne)', 'Uppsala (Uppsala)'], nargs='+', required=True,
                           help="The name of the parser from which to display outlier positions. Because parser names contain spaces or "
                                "single quotes, the name must be enclosed in double quotes. To indicate several at the same time, they "
                                "must be separated by spaces.")
    subparser.add_argument('--section', type=str, choices=['individual', 'group'], required=True, help="The type of section in which to "
                                                                                                       "obtain the outliers.")
    subparser.add_argument('--ranking', type=str, choices=['las', 'mlas', 'blex', 'uas', 'clas', 'upos', 'xpos', 'ufeats', 'alltags',
                                                           'lemmas', 'sentences', 'words', 'tokens'], nargs='+', required=True,
                           help="The type of the ranking in which to obtain the outliers. To indicate several at the same time, they must "
                                "be separated by spaces.")
    subparser.add_argument('--limit', type=int, required=True, help="The number of outliers to be displayed.")
    subparser.add_argument('--show_best', type=str, choices=["yes", "no"], required=True,
                           help="Show the best outliers or the worst outliers.")
    subparser.add_argument('--treebank_set_size', type=int, required=True, help="The size of the treebank sets. There are 82 different "
                                                                                "treebanks.")
    subparser.add_argument('--sampling_size', type=int, required=True, help="The number of samples on which to generate the metric. "
                                                                            "Very large numbers may cause the metric to take time to "
                                                                            "calculate. Repetition of treebanks between sets are allowed, "
                                                                            "but only N-1 treebanks shall be repeated between sets. The "
                                                                            "maximum number of samples available with 82 treebanks for a "
                                                                            "treebank set size (N) are 82! / (N! x (82 - N)!).")
    subparser.add_argument('--cache_samples', type=str, choices=["yes", "no"], required=True, help=cache_sample_help)

    subparser = subparsers.add_parser('statistics', help='It shows different statistics on the outliers of the language sets.')
    subparser.add_argument('--file', type=str, required=True, help="Path to the file with the treebank sets of the outliers of a parser.")

    arguments = parser.parse_args()
    if arguments.command:
        process_arguments(arguments)
    else:
        parser.print_help()


def process_arguments(arguments: Namespace) -> None:
    print("INFO: Processing parameters")

    command = arguments.command
    if command == "rankings":
        ranking_type = arguments.type
        task_year = arguments.year
        rankings_handler(ranking_type, task_year)
    elif command == "metrics":
        ranking_type = arguments.ranking
        section_type = arguments.section
        treebank_set_size = arguments.treebank_set_size
        sampling_size = arguments.sampling_size
        cache_samples = bool(util.strtobool(arguments.cache_samples))
        metrics_handler(ranking_type, section_type, treebank_set_size, sampling_size, cache_samples)
    elif command == "experiments":
        ranking_type = arguments.ranking
        section_type = arguments.section
        treebank_set_size = arguments.treebank_set_size
        sampling_size = arguments.sampling_size
        cache_samples = bool(util.strtobool(arguments.cache_samples))
        experiments_handler(ranking_type, section_type, treebank_set_size, sampling_size, cache_samples)
    elif command == "outliers":
        parsers = arguments.parser
        section_type = arguments.section
        rankings = arguments.ranking
        treebank_set_size = arguments.treebank_set_size
        sampling_size = arguments.sampling_size
        limit = arguments.limit
        show_best = bool(util.strtobool(arguments.show_best))
        cache_samples = bool(util.strtobool(arguments.cache_samples))
        outliers_handler(parsers, section_type, rankings, treebank_set_size, sampling_size, limit, show_best, cache_samples)
    elif command == "statistics":
        file = arguments.file
        statistics_handler(file)
    else:
        print("ERROR: Unknown parameter")


def rankings_handler(ranking_type: str, task_year: int) -> None:
    get_rankings(ranking_type, task_year)


def metrics_handler(ranking_type: List[str], section_type: str, treebank_set_size: int, sampling_size: int, cache_samples: bool) -> None:
    measure_shared_task_metrics(ranking_type, section_type, treebank_set_size, sampling_size, cache_samples)


def experiments_handler(ranking_type: List[str], section_type: str, treebank_set_size: int, sampling_size: int,
                        cache_samples: bool) -> None:
    measure_experiments_metrics(ranking_type, section_type, treebank_set_size, sampling_size, cache_samples)


def outliers_handler(parsers: List[str], section_type: str, rankings: List[str], treebank_set_size: int, sampling_size: int,
                     limit: int, show_best: bool, cache_samples: bool) -> None:
    get_parser_outliers(parsers, section_type, rankings, treebank_set_size, sampling_size, limit, show_best, cache_samples)


def statistics_handler(file: str) -> None:
    get_outlier_statistics(file)


if __name__ == "__main__":
    main()
