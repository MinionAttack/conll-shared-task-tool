# -*- coding: utf-8 -*-

import requests as requests
from typing import Any

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
