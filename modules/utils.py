# -*- coding: utf-8 -*-

from csv import reader, writer
from pathlib import Path
from random import sample
from typing import Any, List

import requests as requests

from resources.constants import BROWSER_USER_AGENT


def handle_request(url: str) -> Any:
    headers = {'User-Agent': BROWSER_USER_AGENT, 'Upgrade-Insecure-Requests': '1', 'DNT': '1'}

    try:
        request = requests.get(url, headers=headers)
        request.raise_for_status()

        return request
    except requests.exceptions.HTTPError as http_error:
        print(f"Http Error: {http_error}")
    except requests.exceptions.ConnectionError as connection_error:
        print(f"Error Connecting: {connection_error}")
    except requests.exceptions.TooManyRedirects as redirects_error:
        print(f"Too Many Redirects: {redirects_error}")
    except requests.exceptions.Timeout as timeout_error:
        print(f"Timeout Error: {timeout_error}")
    except requests.exceptions.RequestException as request_exception:
        print(f"Error: {request_exception}")

    return None


def select_subsets(language_set: List[str], treebank_set_size: int, sampling_size: int, cache_samples: bool) -> List[List[str]]:
    if cache_samples:
        cached_samples = load_cached_samples(treebank_set_size, sampling_size)
        if cached_samples:
            results = cached_samples
        else:
            samples = generate_samples(language_set, treebank_set_size, sampling_size)
            save_samples(samples, treebank_set_size, sampling_size)
            results = samples
    else:
        results = generate_samples(language_set, treebank_set_size, sampling_size)

    return results


def load_cached_samples(treebank_set_size: int, sampling_size: int) -> List[List[str]]:
    print(f"INFO: Loading {sampling_size} subset(s) of size {treebank_set_size} from disk")

    file_path = Path(__file__).absolute()
    root_folder = file_path.parent.parent
    path_cache_folder = Path(root_folder).joinpath("cache")
    cache_file = Path(path_cache_folder, f"{treebank_set_size}-{sampling_size}.csv")

    if cache_file.exists():
        samples = read_csv_file(cache_file)
        return samples
    else:
        print(f"WARNING: There is no file of {sampling_size} subset(s) of size {treebank_set_size} that has been previously saved")
        return []


def read_csv_file(file: Path) -> List[List[str]]:
    print(f"INFO: Reading {file.name} file")

    samples = []
    with open(file, 'rt', encoding="utf-8", newline='') as csv_file:
        csv_reader = reader(csv_file)
        for row in csv_reader:
            samples.append(row)

    return samples


def generate_samples(language_set: List[str], treebank_set_size: int, sampling_size: int) -> List[List[str]]:
    print(f"INFO: Selecting {sampling_size} subset(s) of size {treebank_set_size}")

    results = []
    if language_set:
        while len(results) < sampling_size:
            print(f"Number of subsets selected: {len(results)}/{sampling_size}", end="\r")
            result = sample(language_set, k=treebank_set_size)
            if result not in results:
                results.append(result)

    return results


def save_samples(samples: List[List[str]], treebank_set_size: int, sampling_size: int) -> None:
    print(f"INFO: Saving {sampling_size} subset(s) of size {treebank_set_size} to disk")

    file_path = Path(__file__).absolute()
    root_folder = file_path.parent.parent
    path_cache_folder = Path(root_folder).joinpath("cache")
    path_cache_folder.mkdir(parents=True, exist_ok=True)

    file_name = Path(path_cache_folder, f"{treebank_set_size}-{sampling_size}.csv")

    with open(file_name, 'wt', encoding="utf-8", newline='') as cache_file:
        csv_writer = writer(cache_file, dialect='unix')
        csv_writer.writerows(samples)
