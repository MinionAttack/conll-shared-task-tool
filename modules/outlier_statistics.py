# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Dict

from modules.utils import read_csv_file


def get_outlier_statistics(file: str) -> None:
    print("Obtaining statistics on outliers")

    families_sizes_file = Path("data/families_sizes.csv")
    families_sizes_raw = read_csv_file(families_sizes_file)
    families_sizes = process_families_size_values(families_sizes_raw)
    parser_outliers_path = Path.home().joinpath(Path(file))
    subsets = read_csv_file(parser_outliers_path)

    calculate_statistics(subsets, families_sizes)
    calculate_statistics_low_resources(subsets)


def process_families_size_values(families_sizes: List[List[str]]) -> Dict[str, Dict[str, str]]:
    print("Processing family values and sizes")

    results = {}
    for family_size in families_sizes:
        if len(family_size) == 4:
            details = {}
            treebank = family_size[0]
            details['name'] = family_size[1]
            details['size'] = int(family_size[2].upper().replace("K", ""))
            details['families'] = family_size[3]
            results[treebank] = details
        else:
            print("The format of the data for families and sizes is not correct, it should contain 4 columns")

    return results


def calculate_statistics(subsets: List[List[str]], families_sizes: Dict[str, Dict[str, str]]) -> None:
    print("Calculating statistics on outliers")

    rows_values = []
    for subset in subsets:
        row_values = []
        for treebank in subset:
            if treebank in families_sizes.keys():
                values = {}
                data = families_sizes[treebank]
                values["size"] = data.get("size")
                values["families"] = data.get("families")
                row_values.append(values)
            else:
                continue
        rows_values.append(row_values)

    means = calculate_rows_means(rows_values)
    overall = calculate_overall_means(means)
    display_results(overall)


def calculate_rows_means(rows_values: List[List[Dict[str, str]]]) -> List[Dict[str, float]]:
    print("Calculating the mean values of each subset")

    rows_means = []
    for row_values in rows_values:
        accumulated = {}
        for treebank in row_values:
            size = treebank.get("size")
            if "size" in accumulated.keys():
                actual = accumulated.get("size")
                new = actual + size
                accumulated["size"] = new
            else:
                accumulated["size"] = size
            families = treebank.get("families")
            if families in accumulated.keys():
                actual = accumulated.get(families)
                new = actual + 1
                accumulated[families] = new
            else:
                accumulated[families] = 1

        means = {}
        subset_length = len(row_values)
        for key, value in accumulated.items():
            means[key] = value / subset_length
        rows_means.append(means)

    return rows_means


def calculate_overall_means(subsets_means: List[Dict[str, float]]) -> Dict[str, float]:
    print("Calculating the overall mean values")

    accumulated = {}
    for subset_means in subsets_means:
        for key, value in subset_means.items():
            if key in accumulated.keys():
                actual = accumulated[key]
                new = actual + value
                accumulated[key] = new
            else:
                accumulated[key] = value

    overall_means = {}
    subset_length = len(subsets_means)
    for key, value in accumulated.items():
        overall_means[key] = value / subset_length

    return overall_means


def display_results(overall: Dict[str, float]) -> None:
    print("Showing results")

    print("")
    for key, value in overall.items():
        formatted_value = "{:.2f}".format(value)
        if key == "size":
            print(f"{key}: {formatted_value}K")
        else:
            print(f"{key}: {formatted_value}")


def calculate_statistics_low_resources(subsets: List[List[str]]) -> None:
    low_resources = ['cs_pud', 'en_pud', 'fi_pud', 'ja_modern', 'sv_pud', 'gl_treegal', 'ga_idt', 'la_perseus', 'sme_giella',
                     'no_nynorsklia', 'ru_taiga', 'sl_sst', 'bxr_bdt', 'hsb_ufal', 'hy_armtdp', 'kk_ktb', 'kmr_mg', 'br_keb', 'fo_oft',
                     'pcm_nsc', 'th_pud']

    rows_values = []
    for subset in subsets:
        counter = 0
        for treebank in subset:
            if treebank in low_resources:
                counter += 1
            else:
                continue
        rows_values.append(counter)

    means = calculate_rows_means_low_resources(rows_values)
    overall = calculate_overall_means_low_resources(means)
    formatted_overall = "{:.2f}".format(overall)
    print(f"\nLow resources ratio: {formatted_overall}")


def calculate_rows_means_low_resources(rows_values: List[int]) -> List[float]:
    print("\nCalculating the mean values of each subset for low resources")

    rows_means = []
    subset_length = len(rows_values)
    for row_value in rows_values:
        row_mean = row_value / subset_length
        rows_means.append(row_mean)

    return rows_means


def calculate_overall_means_low_resources(subsets_means: List[float]) -> float:
    print("Calculating the overall mean values for low resources")

    subset_length = len(subsets_means)
    accumulated = 0
    for subset_means in subsets_means:
        accumulated += subset_means

    overall_mean = accumulated / subset_length

    return overall_mean
