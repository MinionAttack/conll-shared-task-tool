# -*- coding: utf-8 -*-

from csv import writer
from pathlib import Path
from re import compile
from typing import Dict, List, Tuple

import requests as requests
from lxml.cssselect import CSSSelector
from lxml.html import fromstring
from tqdm import tqdm

from modules.utils import handle_request
from resources.constants import BASE_URL, RESULTS_TYPES, SECTION_DETAILS


def get_rankings(ranking_type: str, task_year: int) -> None:
    print("INFO: Downloading the rankings")

    if ranking_type == "all":
        for results_type in RESULTS_TYPES:
            sections = download_ranking(results_type, task_year)
            processed_data = process_data(sections)
            store_data(processed_data, results_type)
    else:
        sections = download_ranking(ranking_type, task_year)
        processed_data = process_data(sections)
        store_data(processed_data, ranking_type)


def download_ranking(results_type: str, task_year: int) -> Dict[str, Dict[str, str]]:
    url = BASE_URL.format(task_year, results_type)
    request = handle_request(url)

    if request is not None and request.status_code == requests.codes.ok:
        content = request.text
        sections = retrieve_sections(content)
        if sections:
            return sections
        else:
            print('No section(s) found, check that the layout format of the website has not changed.')
    else:
        print('Error connecting to universaldependencies.org. The service may not be available at this time.')


def retrieve_sections(content: str) -> Dict[str, Dict[str, str]]:
    html_content = fromstring(content)
    sections = {}

    for grouping, treebanks in SECTION_DETAILS.items():
        values = {}
        for title_css, scores_css in tqdm(treebanks.items(), desc=f"Retrieving {grouping} section(s)"):
            title_selector = CSSSelector(title_css)
            title = title_selector(html_content)[0].text
            scores_selector = CSSSelector(scores_css)
            scores = scores_selector(html_content)[0].text
            values[title] = scores

        sections[grouping] = values

    return sections


def process_data(sections: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, List[Tuple[str, str, float]]]]:
    processed_data = {}
    for grouping, treebanks in sections.items():
        data = {}
        for title, scores in tqdm(treebanks.items(), desc=f"Processing {grouping} section(s)"):
            processed_scores = process_scores(scores)
            data[title] = processed_scores
        processed_data[grouping] = data

    return processed_data


def process_scores(scores: str) -> List[Tuple[str, str, float]]:
    leaderboard = []
    pattern = compile(r'^\d{1,2}\.\s')

    positions = scores.split("\n")[1:-1]
    for position in positions:
        fields = position.strip().split("\t")
        raw_name = fields[0].strip()
        if pattern.match(raw_name):
            cleaned_name = raw_name[3:].strip()
        else:
            cleaned_name = raw_name
        software = fields[1].strip()
        score = float(fields[2])
        result = (cleaned_name, software, score)
        leaderboard.append(result)

    return leaderboard


def store_data(processed_data: Dict[str, Dict[str, List[Tuple[str, str, float]]]], results_type: str) -> None:
    file_path = Path(__file__).absolute()
    root_folder = file_path.parent.parent
    path_data_folder = Path(root_folder).joinpath("data")

    for grouping, data in processed_data.items():
        file_folder = Path(path_data_folder).joinpath(results_type).joinpath(grouping)
        file_folder.mkdir(parents=True, exist_ok=True)
        for treebank, values in tqdm(data.items(), desc=f"Storing the {grouping} section(s) on disk"):
            filename = Path(file_folder, f"{treebank}.csv")
            with open(filename, 'wt', encoding="utf-8", newline='') as csv_file:
                file_stream = writer(csv_file, dialect='excel')
                file_stream.writerows(values)
        print(f"INFO: All information has been written in the following folder: {file_folder.absolute()}")
