from loader.csv_text_loader import CSVTextDataSetLoader

from cleaner import clean_tweet_data

from analysis.composite_analyzer import CompositeAnalyzer
from analysis.named_analyzer import NamedAnalyzer
from analysis.analyzers.records_count_analyzer import RecordsCountAnalyzer
from analysis.analyzers.average_words_length_analyzer import AverageWordsLengthAnalyzer
from analysis.analyzers.most_common_word_analyzer import MostCommonWordsAnalyzer
from analysis.analyzers.top_longest_text_records_analyzer import (
    TopLongestTextRecordsAnalyzer,
)
from analysis.analyzers.uppercase_word_count_analyzer import UppercaseWordCountAnalyzer

from results_transformer import ResultsTransformer

from report_builder import ReportBuilder, JsonReportBuilder

TARGET_CATEGORY_FEATURE = "Biased"
TARGET_TEXT_FEATURE = "Text"
NUM_COMMON_WORDS = 10
NUM_LONGEST_TWEETS = 3
DEFAULT_CATEGORY_NAME = "total"

CATEGORY_MAPPING = {0: "non_antisemitic", 1: "antisemitic"}

DATASET_FILEPATH = "data/tweets_dataset.csv"
CLEANED_DATASET_FILEPATH = "results/tweets_dataset_cleaned.csv"
JSON_REPORT_FILEPATH = "results/results"

REPORT_HEADLINES = {
    "tt": "total_tweets",
    "al": "average_length",
    "cw": "common_words",
    "lnt": f"longest_{NUM_LONGEST_TWEETS}_tweets",
    "uw": "uppercase_words",
}

# Load dataset
loader = CSVTextDataSetLoader(
    filepath=DATASET_FILEPATH,
    chosen_features=[TARGET_TEXT_FEATURE, TARGET_CATEGORY_FEATURE],
)
dataset = loader.load()

# Question 1 - Data Analysis
analyzers = [
    NamedAnalyzer(
        REPORT_HEADLINES["tt"],
        RecordsCountAnalyzer(
            dataset,
            category_feature=TARGET_CATEGORY_FEATURE,
            default_category=DEFAULT_CATEGORY_NAME,
        ),
    ),
    NamedAnalyzer(
        REPORT_HEADLINES["al"],
        AverageWordsLengthAnalyzer(
            dataset,
            text_feature=TARGET_TEXT_FEATURE,
            category_feature=TARGET_CATEGORY_FEATURE,
            default_category=DEFAULT_CATEGORY_NAME,
            dropna=True,
        ),
    ),
    NamedAnalyzer(
        REPORT_HEADLINES["cw"],
        MostCommonWordsAnalyzer(
            dataset,
            text_feature=TARGET_TEXT_FEATURE,
            top_n=NUM_COMMON_WORDS,
            default_category=DEFAULT_CATEGORY_NAME,
        ),
    ),
    NamedAnalyzer(
        REPORT_HEADLINES["lnt"],
        TopLongestTextRecordsAnalyzer(
            dataset,
            text_feature=TARGET_TEXT_FEATURE,
            top_n=NUM_LONGEST_TWEETS,
            category_feature=TARGET_CATEGORY_FEATURE,
            default_category=DEFAULT_CATEGORY_NAME,
            dropna=True,
        ),
    ),
    NamedAnalyzer(
        REPORT_HEADLINES["uw"],
        UppercaseWordCountAnalyzer(
            dataset,
            text_feature=TARGET_TEXT_FEATURE,
            category_feature=TARGET_CATEGORY_FEATURE,
            default_category=DEFAULT_CATEGORY_NAME,
            dropna=True,
        ),
    ),
]

composite_analyzer = CompositeAnalyzer(analyzers)
results = composite_analyzer.run_all()

# Question 2 - Clean Data
clean_df = clean_tweet_data(dataset.get_dataframe())
clean_df.to_csv(CLEANED_DATASET_FILEPATH, index=False)


# Question 3 - Build Report
report_transformer = ResultsTransformer(
    category_mapping=CATEGORY_MAPPING,
    tuple_extract_keys=[REPORT_HEADLINES["cw"]],
    tuple_extract_index=0,
    exclude_keys={
        REPORT_HEADLINES["lnt"]: [DEFAULT_CATEGORY_NAME],
    },
)
final_results = report_transformer.transform(results)

report_builder: ReportBuilder = JsonReportBuilder(
    filepath=JSON_REPORT_FILEPATH, report=final_results
)

report_builder.save()
