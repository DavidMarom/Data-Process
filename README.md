# Antisemitism Detection — Tweet Text Analysis Pipeline

> **Detecting antisemitic language at scale**: An end-to-end NLP data processing pipeline that ingests ~14,700 raw tweets, cleans and analyzes linguistic patterns across labeled hate-speech and neutral content, and delivers a structured analytical report — fully automated, reproducible, and designed to extend to downstream ML classification.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white)
![Pytest](https://img.shields.io/badge/Tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

---

## Table of Contents

1. [Business Problem](#1-business-problem)
2. [Dataset](#2-dataset)
3. [Data Processing Steps & Challenges](#3-data-processing-steps--challenges)
4. [Analysis Dimensions](#4-analysis-dimensions)
5. [Key Findings](#5-key-findings)
6. [Architecture](#6-architecture)
7. [Tech Stack](#7-tech-stack)
8. [How to Run](#8-how-to-run)
9. [Project Structure](#9-project-structure)

---

## 1. Business Problem

Online antisemitism has surged across social media platforms. Manual moderation at scale is impossible, and automated detection requires a strong understanding of the linguistic fingerprint of hateful content **before** a model can be trained.

This pipeline solves the **pre-modelling problem**: given a labelled tweet dataset, it systematically characterizes the linguistic differences between antisemitic and non-antisemitic content — producing clean, analysis-ready data and a structured report that directly informs feature engineering for downstream classifiers.

**Impact**: Accelerates the path from raw social-media data to a deployable hate-speech detection model by automating the entire EDA and cleaning workflow.

---

## 2. Dataset

| Property | Value |
|---|---|
| Source | `data/tweets_dataset.csv` |
| Size | ~14,700 tweets |
| Columns | `TweetID`, `Username`, `Text`, `CreateDate`, `Biased`, `Keyword` |
| Label | `Biased` — binary flag (`0` = non-antisemitic, `1` = antisemitic) |
| Language | English |

The `Biased` column contains missing values for some records, representing unlabelled or ambiguous content — handled explicitly in the cleaning step.

---

## 3. Data Processing Steps & Challenges

### 3.1 Loading
- **Selective feature loading**: Only `Text` and `Biased` columns are ingested, reducing memory footprint on the full CSV.
- **Encoding resilience**: The loader catches `UnicodeDecodeError` and re-raises with an actionable message including the file path and encoding attempted — critical for tweet text that may contain non-ASCII characters.

### 3.2 Cleaning

The cleaner (`src/cleaner.py`) addresses three real-world text-quality challenges:

| Challenge | Solution |
|---|---|
| Missing labels (`NaN` in `Biased`) | Rows dropped via `dropna(subset=['Biased'])` |
| Mixed case obscuring word frequency | Full lowercasing applied |
| Punctuation inflating token counts | Stripped using `str.maketrans` against `string.punctuation` |

The cleaned dataset is saved to `results/tweets_dataset_cleaned.csv` for downstream model training.

### 3.3 Category Mapping
Raw binary labels (`0`, `1`) are mapped to human-readable keys (`non_antisemitic`, `antisemitic`) in the output report, preventing silent numeric-index bugs in downstream code.

---

## 4. Analysis Dimensions

Five targeted analyses run across the full corpus and **broken down by label** (antisemitic vs. non-antisemitic):

| Analyzer | What It Measures | Why It Matters |
|---|---|---|
| **Record Count** | Tweet volume per category | Quantifies class imbalance — a critical input to model training strategy |
| **Average Word Length** | Mean words per tweet per category | Longer antisemitic tweets may signal ideological elaboration vs. slurs |
| **Most Common Words** | Top-10 tokens across the corpus | Reveals vocabulary overlap and guides stopword decisions |
| **Top Longest Tweets** | The 3 longest tweets per category | Surfaces edge cases and informs max-sequence-length choices for transformers |
| **Uppercase Word Count** | ALL-CAPS words per category | Proxy for emotional intensity / shouting — a potential classification feature |

All analyzers follow a shared `Analyzer` interface, run in a single pass via `CompositeAnalyzer`, and emit `dict` outputs that are then transformed and serialized to JSON.

---

## 5. Key Findings

> The pipeline produces a `results/results.json` report with the following structure:

```json
{
    "total_tweets":    { "non_antisemitic": ..., "antisemitic": ..., "total": ... },
    "average_length":  { "non_antisemitic": ..., "antisemitic": ..., "total": ... },
    "common_words":    { "total": ["word1", "word2", ...] },
    "longest_3_tweets":{ "non_antisemitic": [...], "antisemitic": [...] },
    "uppercase_words": { "non_antisemitic": ..., "antisemitic": ..., "total": ... }
}
```

Run the pipeline to generate live results against the current dataset (see [How to Run](#8-how-to-run)).

---

## 6. Architecture

The codebase applies two classic design patterns that keep the analysis extensible without touching existing code:

**Composite Pattern** — `CompositeAnalyzer` aggregates any number of `NamedAnalyzer` wrappers and runs them all in one call, returning a unified results dictionary. Adding a new analysis metric requires zero changes to existing code.

**Strategy Pattern** — `TextDataSetLoader` and `ReportBuilder` are abstract base classes. The concrete `CSVTextDataSetLoader` and `JsonReportBuilder` implementations are swappable — e.g., switching to a database loader or a Parquet report requires only a new subclass.

```
main.py
└── manager.py
    ├── CSVTextDataSetLoader  →  TextDataSet (wraps pd.DataFrame)
    ├── clean_tweet_data      →  cleaned CSV
    ├── CompositeAnalyzer
    │   ├── RecordsCountAnalyzer
    │   ├── AverageWordsLengthAnalyzer
    │   ├── MostCommonWordsAnalyzer
    │   ├── TopLongestTextRecordsAnalyzer
    │   └── UppercaseWordCountAnalyzer
    ├── ResultsTransformer    →  category mapping + key filtering
    └── JsonReportBuilder     →  results/results.json
```

---

## 7. Tech Stack

| Tool | Role |
|---|---|
| **Python 3.10+** | Core language |
| **pandas 2.0+** | Data loading, cleaning, grouped aggregations |
| **collections.Counter** | Efficient frequency counting for common-words analysis |
| **pytest 7.0+** | Unit and integration testing of the loader |
| **pyproject.toml** | pytest configuration and project metadata |

---

## 8. How to Run

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run the Full Pipeline

```bash
python main.py
```

This will:
1. Load `data/tweets_dataset.csv`
2. Run all 5 analyses across both label categories
3. Write the cleaned dataset to `results/tweets_dataset_cleaned.csv`
4. Write the analysis report to `results/results.json`

### Run Tests

```bash
pytest -v
```

Tests cover: basic CSV loading, column selection, error handling for missing files, and `get_dataframe` integrity.

---

## 9. Project Structure

```
Data-Process/
├── data/
│   └── tweets_dataset.csv          # Raw labelled tweet dataset (~14,700 rows)
├── results/                        # Generated outputs (gitignored)
│   ├── tweets_dataset_cleaned.csv
│   └── results.json
├── src/
│   ├── manager.py                  # Pipeline orchestration
│   ├── cleaner.py                  # Text normalization
│   ├── report_builder.py           # Abstract + JSON report writers
│   ├── results_transformer.py      # Category mapping and key filtering
│   ├── loader/
│   │   ├── text_loader.py          # Abstract loader interface
│   │   └── csv_text_loader.py      # pandas CSV implementation
│   ├── entities/
│   │   └── text_dataset.py         # TextDataSet wrapper
│   └── analysis/
│       ├── analyzer.py             # Abstract Analyzer base
│       ├── named_analyzer.py       # Name-tagged analyzer wrapper
│       ├── composite_analyzer.py   # Runs all analyzers in one pass
│       └── analyzers/
│           ├── records_count_analyzer.py
│           ├── average_words_length_analyzer.py
│           ├── most_common_word_analyzer.py
│           ├── top_longest_text_records_analyzer.py
│           └── uppercase_word_count_analyzer.py
├── tests/
│   └── test_csv_loader.py
├── main.py
├── requirements.txt
└── pyproject.toml
```
