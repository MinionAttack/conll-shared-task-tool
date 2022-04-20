# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Dict, List, Tuple

from matplotlib.pyplot import savefig, plot, legend, xlabel, ylabel, title, xticks, clf, figure, yticks, annotate
from numpy import NaN, arange
from pandas import DataFrame, read_csv


def generate_opinion_charts(input_path: Path, scores_type: str, display_values: bool) -> None:
    print("INFO: Generate graphs of opinion scores")

    dataframes = load_dataframes(input_path)
    generate_chart(dataframes, scores_type, display_values)


def load_dataframes(input_path: Path) -> Dict[str, DataFrame]:
    print("INFO: Loading data")

    files = Path(input_path).glob('*.csv')
    dataframes = {}
    for corpora in files:
        dataframe = read_csv(corpora, sep=",", header=0, encoding="utf-8")
        dataframe = dataframe.replace({NaN: None})
        dataframes[corpora.stem] = dataframe

    return dataframes


def generate_chart(dataframes: Dict[str, DataFrame], scores_type: str, display_values: bool) -> None:
    print("INFO: Generating charts")

    for name, dataframe in dataframes.items():
        scores = dataframe.get(scores_type)
        if scores is not None:
            opinions = dataframe.opinions.tolist()
            scores = scores.tolist()
            opinions, scores = remove_none_values(opinions, scores)
            figure(figsize=(5, 5))
            yticks(arange(0, 1, 0.1))
            xticks(opinions)
            plot(opinions, scores, "o", label="test")
            xlabel('Number of opinions')
            ylabel('F1 score')
            title(name)
            legend(loc='best', fancybox=True, framealpha=0.5, handlelength=1, handleheight=0.5, handletextpad=0.5)
            if display_values:
                show_values(opinions, scores, "center", "center")

            Path(__file__).parent.parent.joinpath("charts").joinpath("opinions").mkdir(parents=True, exist_ok=True)
            file_path = Path(__file__).parent.parent.joinpath("charts").joinpath("opinions").joinpath(f"{name}.png")
            savefig(file_path, bbox_inches='tight', transparent=True, dpi=600)
            clf()
        else:
            print(f"ERROR: The indicated {scores_type} value has no scores")


def remove_none_values(opinions: List[int], scores: List[int]) -> Tuple[List[int], List[int]]:
    indices = {index for index, value in enumerate(scores) if value is None}

    final_opinions = [value for index, value in enumerate(opinions) if index not in indices]
    final_scores = [value for index, value in enumerate(scores) if index not in indices]

    return final_opinions, final_scores


def show_values(x_values: List[int], y_values: List[int], vertical_position: str, horizontal_position: str) -> None:
    # zip joins x and y coordinates in pairs
    for x, y in zip(x_values, y_values):
        if y is not None:
            label = "{:.3f}".format(y)
            annotate(label,  # this is the text
                     (x, y),  # this is the point to label
                     textcoords="offset points",  # how to position the text
                     xytext=(0, 8),  # distance from text to the points (x,y)
                     va=vertical_position,  # vertical alignment can be center, top, bottom, baseline
                     ha=horizontal_position)  # horizontal alignment can be left, right or center
