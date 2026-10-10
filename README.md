# NYC Yellow Taxi Analysis

End-to-end analysis of New York City Yellow Taxi trip data using Python, covering more than eleven years of taxi activity.

The project combines detailed exploratory data analysis with reusable data-processing code, automated tests, and a longitudinal analysis of **831,237,097 Yellow Taxi trips across 140 monthly datasets from January 2015 through August 2026**.

---

## Overview

NYC Yellow Taxi trip records provide a large real-world dataset for studying transportation demand, trip behavior, geographic patterns, fares, airport activity, and payment behavior.

This project was designed as a complete analytical workflow rather than a single notebook. It includes:

- exploratory data analysis
- data-quality assessment
- feature engineering
- reusable cleaning logic
- task-specific analytical filters
- geographic enrichment
- monthly aggregation
- longitudinal trend analysis
- automated testing
- reproducible project structure
- portfolio-ready visualizations

The analysis begins with a detailed investigation of January 2026 data and then extends the same processing logic across the full 2015–2026 period.

---

## Objectives

The project aims to answer several questions:

- How has Yellow Taxi demand changed over time?
- Did the decline in taxi activity begin before the COVID-19 pandemic?
- How have typical trip duration, distance, and speed changed?
- How have recorded trip amounts evolved?
- What role do airport trips play in the Yellow Taxi market?
- How has payment behavior changed?
- Which data-quality issues need to be handled before analysis?
- Can the processing logic be reused consistently across more than a decade of monthly data?

---

## Dataset

- **Source:** NYC Taxi & Limousine Commission (TLC)
- **Dataset:** Yellow Taxi Trip Records
- **Period:** January 2015 – August 2026
- **Files analyzed:** 140 monthly Parquet files
- **Trips analyzed:** 831,237,097
- **Format:** Apache Parquet

Official TLC trip-record data:

[NYC Taxi & Limousine Commission — Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

The raw TLC datasets are intentionally not included in this repository.

The total trip count represents records included in the monthly analysis period. Individual analyses may use smaller subsets depending on task-specific data-quality requirements.

---

## Key Findings

### 1. Yellow Taxi demand declined substantially

Average monthly trip volume for January–August declined from:

| Period | Average monthly trips |
|---|---:|
| 2015 Jan–Aug | 12.47M |
| 2019 Jan–Aug | 7.13M |
| 2026 Jan–Aug | 3.71M |

The decline was already visible before the pandemic.

The historical monthly peak in the analyzed period occurred in **March 2015 with approximately 13.34 million trips**, while the pandemic low occurred in **April 2020 with only 237,941 trips**.

Although trip activity recovered after 2020, it remained well below pre-pandemic levels.

![NYC Yellow Taxi monthly trip volume](reports/figures/monthly_trip_volume.png)

*Monthly Yellow Taxi trip volume from January 2015 through August 2026.*

---

### 2. Typical trips became longer

Between January–August 2019 and the same period of 2026:

- median trip duration increased from **11.11 to 14.10 minutes**
- median trip distance increased from **1.65 to 1.93 miles**
- median speed declined from approximately **10.00 to 9.29 mph**

The longer typical trip duration is therefore associated with both longer trip distances and somewhat lower travel speeds.

---

### 3. Recorded trip amounts increased substantially

Median recorded total amount increased from:

- **$14.28** in January–August 2019
- to **$23.68** in January–August 2026

At the same time, average monthly recorded total amount declined from approximately:

- **$135.3M** in 2019
- to **$112.2M** in 2026

Higher recorded amounts per trip have therefore only partially offset the large reduction in total trip volume.

These values are nominal and are not adjusted for inflation.

![NYC Yellow Taxi median recorded trip amount](reports/figures/median_total_amount.png)

*Median recorded total amount per Yellow Taxi trip from January 2015 through August 2026.*

---

### 4. Airport trips became relatively more important

Airport pickup share increased from:

- **4.39%** in January–August 2015
- **5.82%** in January–August 2019
- **6.49%** in January–August 2026

This does not necessarily mean that the absolute number of airport trips increased.

Instead, airport trips now represent a larger share of total Yellow Taxi activity.

![NYC Yellow Taxi airport pickup share](reports/figures/airport_pickup_share.png)

*Share of Yellow Taxi trips originating at JFK, LaGuardia, or Newark from January 2015 through August 2026.*

---

### 5. Payment behavior changed

Credit-card usage increased strongly through most of the analyzed period and reached an annual average of approximately **77.9% in 2023**.

The apparent decline after 2024 requires additional context.

Recent data contain a rapidly growing `payment_type = 0` / Flex Fare category. For example:

| Period | Payment type 0 | Credit card |
|---|---:|---:|
| Dec 2024 | 8.89% | 74.51% |
| Jan 2025 | 15.54% | 70.34% |
| Jan 2026 | 29.21% | 60.40% |

Among trips outside the `payment_type = 0` category, credit cards remained increasingly dominant.

The post-2024 pattern should therefore not be interpreted simply as passengers moving away from card payments.

---

## Long-Term Comparison

| Metric | 2015 Jan–Aug | 2019 Jan–Aug | 2026 Jan–Aug |
|---|---:|---:|---:|
| Monthly trips | 12.47M | 7.13M | 3.71M |
| Median duration | 10.94 min | 11.11 min | 14.10 min |
| Median distance | 1.75 mi | 1.65 mi | 1.93 mi |
| Median speed | 10.71 mph | 10.00 mph | 9.29 mph |
| Median total amount | $11.84 | $14.28 | $23.68 |
| Monthly total amount | $198.7M | $135.3M | $112.2M |
| Airport pickup share | 4.39% | 5.82% | 6.49% |
| Credit card share | 62.44% | 71.50% | 63.62% |

The results indicate that the Yellow Taxi market observed in 2026 is meaningfully different from the market observed in 2015: trip volume is much lower, while typical trips are longer, recorded trip amounts are higher, and airport activity represents a larger share of total trips.

---

## Analysis Notebooks

### [`01-exploration.ipynb`](notebooks/01-exploration.ipynb)

Detailed exploratory analysis using January 2026 Yellow Taxi data.

Topics include:

- schema inspection
- missing values
- data-quality issues
- anomalous records
- trip duration
- trip distance
- travel speed
- hourly and daily demand
- passenger counts
- payment behavior
- fares and tips
- geographic patterns
- taxi zones
- airport activity

This notebook is used to investigate the data in detail and establish the analytical rules later reused by the processing pipeline.

### [`02-longitudinal-analysis.ipynb`](notebooks/02-longitudinal-analysis.ipynb)

Long-term analysis covering **January 2015 through August 2026**.

Topics include:

- long-term trip demand
- pre-pandemic demand decline
- COVID-19 disruption
- post-pandemic recovery
- trip-duration trends
- trip-distance trends
- speed trends
- recorded trip-amount trends
- airport pickup share
- payment behavior
- comparison of 2015, 2019, and 2026
- portfolio-ready longitudinal visualizations

---

## Data Quality and Cleaning Strategy

Real-world taxi data contain multiple types of anomalous or incomplete records.

Examples identified during the analysis include:

- zero or negative trip durations
- extremely large trip distances
- implausible travel speeds
- negative monetary values
- missing passenger counts
- missing rate codes
- unusual vendor-specific records
- records outside the nominal reporting month

Rather than applying one universal filter and deleting every suspicious record, the project uses **task-specific analysis masks**.

For example:

- duration analysis requires valid trip duration
- distance analysis requires valid trip distance
- speed analysis requires valid duration, distance, and plausible speed
- monetary analysis requires valid monetary fields
- passenger analysis requires valid passenger-count information

This approach preserves usable information while preventing unrelated data-quality issues from unnecessarily removing records from every analysis.

---

## Feature Engineering

Reusable feature-engineering functions create variables including:

### Time features

- pickup hour
- day of week
- day name
- weekend indicator
- year
- month

### Trip features

- trip duration in minutes
- average trip speed in mph

### Monetary features

- pre-tip amount
- effective tip rate

### Location features

- pickup borough
- drop-off borough
- pickup zone
- drop-off zone
- same-zone indicator
- same-borough indicator
- airport pickup indicator
- airport drop-off indicator
- airport name

Airport identification includes:

- JFK
- LaGuardia
- Newark

---

## Processing Pipeline

The reusable processing pipeline performs the following sequence:

```text
Raw TLC Parquet file
        │
        ▼
Load trip data
        │
        ▼
Core feature engineering
        │
        ▼
Taxi-zone enrichment
        │
        ▼
Location and airport features
        │
        ▼
Data-quality flags
        │
        ▼
Task-specific analysis masks
        │
        ▼
Analysis-ready dataset
        │
        ▼
Monthly aggregation
```

The same pipeline can be applied to individual monthly datasets across the full study period.

---

## Longitudinal Processing

The longitudinal workflow processes monthly TLC files sequentially and produces a compact monthly summary dataset.

Metrics include:

- trip count
- median trip duration
- median trip distance
- median speed
- median total amount
- aggregate recorded total amount
- airport pickup share
- credit-card share

The processing workflow supports checkpointing so previously completed months can be skipped if processing is resumed.

The final longitudinal dataset contains **140 monthly observations** covering January 2015 through August 2026.

---

## Project Structure

```text
nyc-taxi/
├── notebooks/
│   ├── 01-exploration.ipynb
│   └── 02-longitudinal-analysis.ipynb
│
├── reports/
│   └── figures/
│       ├── monthly_trip_volume.png
│       ├── median_total_amount.png
│       └── airport_pickup_share.png
│
├── scripts/
│   ├── schema_audit.py
│   └── validate_monthly_summary.py
│
├── src/
│   └── nyc_taxi/
│       ├── __init__.py
│       ├── aggregation.py
│       ├── cleaning.py
│       ├── features.py
│       ├── longitudinal.py
│       └── pipeline.py
│
├── tests/
│   ├── test_cleaning.py
│   ├── test_features.py
│   └── test_pipeline.py
│
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Technologies

The project uses:

- Python 3.13
- pandas
- PyArrow
- Matplotlib
- JupyterLab
- pytest
- uv
- Git
- GitHub

---

## Setup

The project uses [`uv`](https://docs.astral.sh/uv/) for Python environment and dependency management.

Clone the repository:

```bash
git clone https://github.com/sazinovic/nyc-taxi-analysis.git
cd nyc-taxi-analysis
```

Install the project and its dependencies:

```bash
uv sync
```

Run JupyterLab:

```bash
uv run jupyter lab
```

Run the automated tests:

```bash
uv run pytest
```

---

## Data Setup

Raw datasets are stored outside the Git repository.

The project expects Yellow Taxi files in the following structure:

```text
~/Data/raw/nyc-taxi/
├── taxi_zone_lookup.csv
│
└── yellow/
    ├── 2015/
    │   ├── yellow_tripdata_2015-01.parquet
    │   ├── yellow_tripdata_2015-02.parquet
    │   └── ...
    │
    ├── 2016/
    │   └── ...
    │
    └── 2026/
        ├── yellow_tripdata_2026-01.parquet
        ├── ...
        └── yellow_tripdata_2026-08.parquet
```

Processed longitudinal data is stored separately:

```text
~/Data/processed/nyc-taxi/
└── monthly_summary.parquet
```

Keeping large raw and processed datasets outside the repository keeps the Git history small while separating source data from project code.

---

## Testing

Core processing logic is covered by automated tests using `pytest`.

The tests cover areas including:

- time-feature creation
- trip-feature creation
- monetary-feature logic
- taxi-zone joins
- location features
- airport identification
- cleaning flags
- passenger validation
- rate-code validation
- analysis masks
- end-to-end pipeline execution

Run all tests with:

```bash
uv run pytest
```

---

## Important Analytical Limitations

Several limitations should be considered when interpreting the results.

### Recorded total amount is not net revenue

`total_amount` includes multiple fare components and should not be interpreted as direct driver or company revenue.

For this reason, the project refers to it as **recorded total amount** rather than revenue.

### Monetary values are nominal

Dollar amounts are not adjusted for inflation.

Changes in recorded trip amounts may reflect multiple factors, including:

- fare-rule changes
- surcharges
- congestion-related fees
- trip-distance changes
- trip-mix changes
- inflation

The analysis therefore does not attribute monetary changes to a single cause.

### Correlation does not establish causation

Relationships such as the negative association between demand and travel speed are interpreted as associations only.

The analysis does not claim that one variable directly causes another without additional evidence.

### Payment categories changed over time

Payment-code composition changed during the study period, particularly in recent years.

Long-term comparisons of payment behavior therefore require additional care.

### 2026 is a partial year

The dataset currently ends in August 2026.

Comparisons involving 2026 use January–August periods where appropriate to maintain comparable seasonal coverage.

### Task-specific subsets differ

Not every analysis uses all 831,237,097 trip records.

Validity requirements differ by analytical task. For example, speed analysis requires valid duration, distance, and plausible speed, while monetary analysis applies monetary validity rules.

This prevents unrelated data-quality problems from unnecessarily excluding otherwise usable records.

---

## Reproducibility

Both analytical notebooks have been validated by restarting the Jupyter kernel and executing all cells from beginning to end.

The reusable package separates analytical logic from notebook presentation, allowing the same transformations to be applied consistently to additional monthly TLC datasets.

The longitudinal workflow also supports checkpointing so historical processing can resume without recomputing previously completed months.

---

## Project Status

Completed:

- detailed January 2026 exploratory analysis
- data-quality investigation
- reusable feature engineering
- reusable cleaning rules
- task-specific analysis masks
- taxi-zone enrichment
- airport classification
- automated tests
- reusable monthly processing pipeline
- 140-month historical processing
- longitudinal analysis from 2015–2026
- executive analytical summary
- portfolio-ready visualizations

Future extensions may include:

- demand forecasting
- machine-learning models
- additional geographic analysis
- interactive dashboards
- inflation-adjusted monetary analysis

---

## Purpose

This project was built as an end-to-end data-analysis portfolio project demonstrating:

- analytical reasoning
- Python and pandas
- handling of large real-world datasets
- data cleaning
- exploratory analysis
- feature engineering
- visualization
- reusable software design
- automated testing
- longitudinal analysis
- Git-based project development
- communication of business insights