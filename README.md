# conll-shared-task-tool

![build](https://img.shields.io/badge/build-passing-success) ![build](https://img.shields.io/badge/license-MIT-success) ![build](https://img.shields.io/badge/python-3.8%2B-blue) ![build](https://img.shields.io/badge/platform-linux--64-lightgrey) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=MinionAttack_conll-shared-task-tool&metric=alert_status)](https://sonarcloud.io/dashboard?id=MinionAttack_conll-shared-task-tool)

Table of contents.

1. [Summary](#summary)
2. [How to use](#how-to-use)
3. [Examples](#examples)
4. [Licensing agreement](#licensing-agreement)

## Summary

This is a tool to download the CoNLL Shared Task classification tables and perform metrics on them. It also allows to perform metrics on
local results and display outliers for a parser.

This script has 8 features:

1. Download the parser ranking tables from the Conll Shared Task website for a particular year.
2. Calculate different metrics on the downloaded data by displaying the results on screen and generating the respective graphs.
3. For the data calculated in the local experiments, it obtains the classification of the parsers used.
4. For a parser, show the outliers observed in the graphs.
5. For outliers of a parser, calculate some statistics on them.
6. For a corpus of SemEval-2022 Shared Task 10, find how many sentences have multiple opinions that share some part.
7. For a corpus of SemEval-2022 Shared Task 10, separate the files by the number of sentence opinions.
8. For a corpus of SemEval-2022 Shared Task 10, Generates graphs with F1 values for each number of opinions.

**It is important to note that the script uses the _data_, _experiments_, _cache_ and _charts_ folders as the base directory for some features.**

## How to use

Install the necessary dependencies listed in the `requirements.txt` file.

`$ pip3 install -r requirements.txt`

To run the script, from a terminal in the root directory, type:

`$ ./conllSharedTasks.py`

This will show the usage:

```
usage: conllSharedTasks.py [-h] {rankings,metrics,experiments,outliers,statistics,analise,separate,opinions} ...

Gets the rankings and shows some metrics on the CoNLL Shared Task of the specified year or in custom experiments.

optional arguments:
  -h, --help            show this help message and exit

Commands:
  {rankings,metrics,experiments,outliers,statistics,analise,separate,opinions}
    rankings            Get the classification results of the specified type and year from the website.
    metrics             Gets the indicated metric on the selected CoNLL Shared Task dataset.
    experiments         For a ranking, gets a leaderboard of the parsers used in the customised experiments.
    outliers            For a given parser, it shows the subsets in which it obtained its best position.
    statistics          It shows different statistics on the outliers of the language sets.
    analise             For a given corpus, analyse whether it has sentences with several opinions in which some element is shared between them.
    separate            Divide the files of each corpus into as many files as the number of opinions.
    opinions            Generates graphs with F1 values for each number of opinions.
```

If you want to know how to use a specific command, for example the *rankings* command, type:

`$ ./conllSharedTasks.py rankings --help`

And it will show the help:

```
usage: conllSharedTasks.py rankings [-h] --type {all,las,mlas,blex,uas,clas,upos,xpos,ufeats,alltags,lemmas,sentences,words,tokens} --year {17,18}

optional arguments:
  -h, --help            show this help message and exit
  --type {all,las,mlas,blex,uas,clas,upos,xpos,ufeats,alltags,lemmas,sentences,words,tokens}
                        The type of the ranking.
  --year {17,18}        The year of the shared task.
```

### Note

If you get an error that you do not have permissions to run the script, type:

`$ chmod u+x conllSharedTasks.py`

Run the script again.

## Examples

### Preliminary clarification

For each type of metric, the website distinguishes between individual treebank rankings and group rankings. The differences between this
distinction should be taken into account when indicating the _--section_ parameter.

### 1. Download the data

To download all the rankings for 2018:

`$ ./conllSharedTasks.py rankings --type all --year 18`

To download a specific ranking for the year 2018:

`$ ./conllSharedTasks.py rankings --type blex --year 18`

### 2. Calculate the metrics

For a specific classification:

`$ ./conllSharedTasks.py metrics --ranking blex --section individual --treebank_set_size 10 --sampling_size 100000 --cache_samples yes`

To indicate several classifications at the same time, they must be separated by spaces:

`$ ./conllSharedTasks.py metrics --ranking las uas blex --section individual --treebank_set_size 10 --sampling_size 100000 --cache_samples yes`

**Note**: Use _--cache_samples_ to store the generated subsets on disk and save time on subsequent invocations of the command.

### 3. Show the classification table of the parsers used in the local experiments.

This command expects a given directory and file structure:

```
experiments/
├── metric_1
│   └── section_type
│       ├── treebank.csv
│       └── ...
└── metric_2
    └── section_type
        ├── treebank.csv
        └── ...
```

With the data attached to this repository, only the options of the _LAS_ and _UAS_ are available. If you want to add more metrics, you have
to modify the command line in the _conllSharedTasks.py_ file, indicating in the _choices_ option the new metrics.

`subparser.add_argument('--ranking', type=str, choices=['las', 'uas', 'new_option_1', 'new_option_2', ...], nargs='+', required=True, help="The ranking(s) to compare scores. To indicate several at the same time, they must be separated by spaces.")`

For a specific metric:

`$ ./conllSharedTasks.py experiments --ranking las --section individual --treebank_set_size 10 --sampling_size 100000 --cache_samples yes`

To indicate several metrics at the same time, they must be separated by spaces:

`$ ./conllSharedTasks.py experiments --ranking las uas --section individual --treebank_set_size 10 --sampling_size 100000 --cache_samples yes`

**Note**: Use _--cache_samples_ to store the generated subsets on disk and save time on subsequent invocations of the command.

### 4. Show the outliers

__Note__: Because parser names contain spaces or single quotes, the name must be enclosed in double quotes.

For a specific parser in a specific metric:

`$ ./conllSharedTasks.py outliers --parser "HIT-SCIR (Harbin)" --section individual --ranking las --limit 20 --show_best no --treebank_set_size 10 --sampling_size 100000 --cache_samples yes`

To indicate several parsers and/or metrics at the same time, they must be separated by spaces:

`$ ./conllSharedTasks.py outliers --parser "HIT-SCIR (Harbin)" "AntNLP (Shanghai)" --section individual --ranking las uas --limit 20 --show_best no --treebank_set_size 10 --sampling_size 100000 --cache_samples yes`

- **show_best**: This parameter controls whether the best outliers (yes) or the worst outliers (no) are displayed.
    - Showing the best outliers makes sense in the case of parsers that perform poorly in general, but have subsets where they do much
      better than expected.
    - Showing the worst outliers makes sense in the case of parsers that perform well in general, but have subsets where they do much worse
      than expected.

**Note**: Use _--cache_samples_ to store the generated subsets on disk and save time on subsequent invocations of the command.

### 5. Calculate outliers statistics

`$ ./conllSharedTasks.py statistics --file Desktop/statistics_worst_udpipe-future.csv`

The file must be a *CSV* without spaces between the values, for example:

```
hr_set,fo_oft,cs_pud,ko_gsd,th_pud,he_htb,cs_pdt,uk_iu,hsb_ufal,pl_sz
pl_sz,la_ittb,pcm_nsc,th_pud,hi_hdtb,hsb_ufal,grc_proiel,ko_kaist,sl_sst,ug_udt
fa_seraji,it_postwita,no_nynorsklia,hsb_ufal,ca_ancora,ru_syntagrus,es_ancora,fo_oft,ur_udtb,nl_alpino
uk_iu,sr_set,hsb_ufal,hi_hdtb,en_ewt,sl_sst,cs_pdt,ja_gsd,pcm_nsc,sv_talbanken
en_gum,es_ancora,cs_pdt,pl_sz,hu_szeged,ja_gsd,gl_ctg,ja_modern,hsb_ufal,ko_kaist
```

### 6. Analise corpus

`$ ./conllSharedTasks.py analise --file Desktop/SemEval-2022_Shared_Task_10/data/opener_es/test.json`

This will show a table with the results for each measure:

1. The number of opinions, how many times they occur and, for each opinion, how many share part of an opinion with the rest of the opinions.

```
|  Number of opinions  |  Occurrences  |  Number of times a sentence shares parts  |
|----------------------|---------------|-------------------------------------------|
|          1           |      159      |                     0                     |
|          2           |      77       |                    32                     |
|          3           |      41       |                    31                     |
|          4           |      34       |                    27                     |
|          5           |      17       |                    17                     |
|          6           |       5       |                     5                     |
|          7           |       8       |                     5                     |
|          8           |       6       |                     6                     |
|          9           |       5       |                     5                     |
|          10          |       3       |                     3                     |
|          11          |       2       |                     2                     |
|          12          |       1       |                     1                     |
|          13          |       2       |                     2                     |
|          14          |       1       |                     1                     |
|          17          |       1       |                     1                     |
```

2. For each part of an opinion, it shows the number of collisions of each size.
    1. The "All Cx" column shows how many times a part of an opinion collides with all other opinions in a sentence.
    2. The column "Not All Cx" shows how many times a part of an opinion does not collide with all other opinions in a sentence. In this
       case, repetitions are not taken into account, so the numbers show single occurrences.

```
|        |  C1  |  All C1  |  Not All C1  |  C2  |  All C2  |  Not All C2  |  C3  |  All C3  |  C4  |  Not All C4  |
|--------|------|----------|--------------|------|----------|--------------|------|----------|------|--------------|
| Source |  17  |    10    |      2       |  9   |    3     |      1       |  1   |    1     |  1   |      1       |


|        |  C1  |  All C1  |  Not All C1  |  C2  |  All C2  |  Not All C2  |  C3  |  All C3  |  Not All C3  |  C4  |  Not All C4  |
|--------|------|----------|--------------|------|----------|--------------|------|----------|--------------|------|--------------|
| Target | 535  |   114    |      5       |  96  |    20    |      3       |  21  |    11    |      2       |  1   |      1       |


|                  |  C1  |  All C1  |  Not All C1  |  C2  |  All C2  |  Not All C2  |  C3  |  All C3  |  Not All C3  |  C4  |  All C4  |  Not All C4  |  C5  |  All C5  |  Not All C5  |  C6  |  Not All C6  |
|------------------|------|----------|--------------|------|----------|--------------|------|----------|--------------|------|----------|--------------|------|----------|--------------|------|--------------|
| Polar_expression | 813  |   159    |      4       |  43  |    9     |      3       |  4   |    1     |      1       |  5   |    1     |      1       |  4   |    1     |      2       |  1   |      1       |
```

### 7. Separate sentences by the number of opinions

`$ ./conllSharedTasks.py separate --original data/original --separated data/separated`

This will generate files in the following format: `name-number_opinions.json`

### 8. Generate graphs with F1 scores for each number of opinions

`$ ./conllSharedTasks.py opinions --folder data/opinions/ --scores test --display`

- **folder**: Folder where the CSV files are located.
    - Note: CSV files must have a header on the first line, as the program interprets the first line as the column names.
    - If there is no value for a given number of opinions, leave it empty as the program will interpret it as `None` (See #4).
      ```
      opinions,dev,test
      0,0.000,0.000
      1,0.372,0.292
      2,0.394,0.343
      3,0.400,0.500
      4,,0.484
      ```
- **scores**: The type of scores to be displayed on the graphs (`dev` or `test`).
- **display**: If specified, displays the values of the points on the graph.

The charts will be generated inside the `charts/opinions/` folder.

## Licensing agreement

MIT License

Copyright (c) 2021 Iago Alonso Alonso

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "
Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the
following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
