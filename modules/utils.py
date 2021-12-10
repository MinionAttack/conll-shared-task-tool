# -*- coding: utf-8 -*-

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


def select_subsets(language_set: List[str], treebank_set_size: int, sampling_size: int) -> List[List[str]]:
    print(f"INFO: Selecting {sampling_size} subset(s) of size {treebank_set_size}")

    results = []
    if language_set:
        while len(results) < sampling_size:
            print(f"Number of subsets selected: {len(results)}/{sampling_size}", end="\r")
            result = sample(language_set, k=treebank_set_size)
            if result not in results:
                results.append(result)

    return results
