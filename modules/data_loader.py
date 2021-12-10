# -*- coding: utf-8 -*-

from csv import reader
from pathlib import Path
from typing import Dict, List, Tuple

from tqdm import tqdm

from resources.constants import SECTION_TYPES


def load_language_set(ranking_type: List[str], section_type: str, folder_name: str) -> List[str]:
    print("INFO: Loading language subsets")

    file_path = Path(__file__).absolute()
    root_folder = file_path.parent.parent
    path_data_folder = Path(root_folder).joinpath(folder_name)

    sets = {}
    for ranking in ranking_type:
        ranking_folders = get_folders(path_data_folder)
        if ranking_folders:
            ranking_folder = ranking_folders.get(ranking)
            section_folders = get_folders(ranking_folder)
            sets[ranking] = get_languages(section_type, section_folders)
        else:
            print(f"ERROR: {folder_name} does not exist or is empty")

    lengths = []
    for ranking, sections in sets.items():
        for section, languages in sections.items():
            length = len(languages)
            lengths.append(length)
    language_set = []
    if len(set(lengths)) == 1:
        for ranking in sets.keys():
            languages = sets[ranking][section_type]
            language_set.extend(languages)
            break
    else:
        print(f"ERROR: There is a ranking that does not contain the same number of languages")

    return language_set


def load_data(ranking_type: str, section_type: str, folder_name: str,
              split_names: bool) -> Dict[str, Dict[str, Dict[str, List[Tuple[str, str, float]]]]]:
    print("INFO: Loading data")

    file_path = Path(__file__).absolute()
    root_folder = file_path.parent.parent
    path_data_folder = Path(root_folder).joinpath(folder_name)

    ranking_folders = get_folders(path_data_folder)
    data = {}
    if ranking_folders:
        if ranking_type == "all":
            for ranking_name, ranking_folder in tqdm(ranking_folders.items(), desc=f"Loading data from all rankings"):
                section_folders = get_folders(ranking_folder)
                data[ranking_name] = get_files(section_type, section_folders, split_names)
        else:
            ranking_folder = ranking_folders.get(ranking_type)
            section_folders = get_folders(ranking_folder)
            data[ranking_type] = get_files(section_type, section_folders, split_names)
    else:
        print(f"ERROR: {folder_name} does not exist or is empty")

    return data


def get_folders(path_data_folder: Path) -> Dict[str, Path]:
    folders = {}

    for item in path_data_folder.glob("*"):
        if item.is_dir():
            name = item.name
            folders[name] = item

    return folders


def get_languages(section_type: str, folders: Dict[str, Path]) -> Dict[str, List[str]]:
    languages = {}

    files = []
    if section_type == "all":
        for section in SECTION_TYPES:
            folder = folders.get(section)
            for file in folder.iterdir():
                filename = file.stem
                files.append(filename)
            languages[section] = files
    else:
        folder = folders.get(section_type)
        for file in folder.iterdir():
            filename = file.stem
            files.append(filename)
        languages[section_type] = files

    return languages


def get_files(section_type: str, folders: Dict[str, Path], split_names: bool) -> Dict[str, Dict[str, List[Tuple[str, str, float]]]]:
    data = {}

    if section_type == "all":
        for section in SECTION_TYPES:
            folder = folders.get(section)
            files = read_files(folder, split_names)
            data[section] = files
    else:
        folder = folders.get(section_type)
        files = read_files(folder, split_names)
        data[section_type] = files

    return data


def read_files(folder: Path, split_names: bool) -> Dict[str, List[Tuple[str, str, float]]]:
    csv_files = {}

    for file in folder.iterdir():
        with open(file, 'rt', encoding="utf-8", newline='') as csv_file:
            filename = file.stem
            file_content = reader(csv_file, dialect='excel')
            results = []
            for row in file_content:
                if split_names:
                    name = row[0].strip().split(" (")[0]
                else:
                    name = row[0].strip()
                software = row[1].strip()
                score = float(row[2].strip())
                position = (name, software, score)
                results.append(position)
            csv_files[filename] = results

    return csv_files
