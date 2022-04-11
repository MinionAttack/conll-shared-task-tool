# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import List, Dict, Any


def walk_directories(input_path: Path, output_path: Path) -> None:
    print("INFO: Browsing through directories to extract")

    input_path_name = input_path.name
    files = []

    for item in input_path.glob("*"):
        if item.is_dir() and not item.name.startswith('.'):
            for element in item.iterdir():
                if element.is_file() and element.suffix == ".json":
                    files.append(element)
        elif item.is_file() and not item.name.startswith('.') and item.suffix == ".json":
            files.append(item)
        else:
            continue

    separate_opinions(files, input_path_name, output_path)


def separate_opinions(files: List[Path], input_path_name: str, output_path: Path) -> None:
    print("INFO: Separating sentences by number of opinions")

    for file in files:
        name = file.name
        file_folder_name = file.parent.name
        if file_folder_name != input_path_name:
            file_folder = output_path.joinpath(file_folder_name)
            file_folder.mkdir(parents=True, exist_ok=True)
            output_file = file_folder.joinpath(name)
        else:
            output_file = output_path.joinpath(name)
        separate_file(file, output_file)


def separate_file(file: Path, output_file: Path) -> None:
    with open(file, 'rt') as data:
        sentences = json.load(data)

    separated_sentences = separate_sentences(sentences)
    write_separated_sentences(output_file, separated_sentences)


def separate_sentences(sentences: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    result = {}
    for sentence in sentences:
        opinions = sentence["opinions"]
        number_opinions = len(opinions)
        if number_opinions in result.keys():
            result[number_opinions].append(sentence)
        else:
            result[number_opinions] = [sentence]

    return result


def write_separated_sentences(output_file: Path, separated_sentences: Dict[int, List[Dict[str, Any]]]) -> None:
    Path.mkdir(output_file.parent, parents=True, exist_ok=True)

    corpus = output_file.parent.name
    for number_opinions, sentences in separated_sentences.items():
        print(f"INFO: Writing the separated sentences for {corpus} with {number_opinions} opinion(s) to a file")
        file_name = f"{output_file.stem}-{number_opinions}.json"
        opinions_output_file = output_file.parent.joinpath(file_name)
        with open(opinions_output_file, 'wt') as file:
            json.dump(sentences, file)
