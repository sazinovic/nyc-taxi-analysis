import pandas as pd
import pytest
from nyc_taxi.aggregation import aggregate_monthly_summary
from nyc_taxi.validation import validate_monthly_summary


def valid_summary(prepared):
    df = aggregate_monthly_summary(prepared, 2026, 1)
    df['processing_fingerprint'] = 'rules'
    df['zone_signature'] = 'zones'
    df['source_signature'] = 'source'
    return df


def test_valid_summary(prepared):
    validate_monthly_summary(valid_summary(prepared), '2026-01', '2026-01')


@pytest.mark.parametrize('column,value', [('month', 13), ('trip_count', -1), ('trip_count', 1.5),
    ('airport_pickup_share', 101), ('monetary_valid_count', 2), ('median_speed_mph', float('nan')),
    ('finite_signed_total_amount_sum', 999), ('processing_fingerprint', None)])
def test_bad_summaries_fail(prepared, column, value):
    df = valid_summary(prepared)
    df[column] = value
    with pytest.raises(ValueError):
        validate_monthly_summary(df)


@pytest.mark.parametrize('column', ['airport_pickup_share', 'credit_card_share', 'speed_coverage_pct'])
def test_in_range_but_incorrect_percentages_fail(prepared, column):
    df = valid_summary(prepared)
    df[column] = 50.0
    with pytest.raises(ValueError, match='denominator'):
        validate_monthly_summary(df)


def test_gap_and_duplicate_fail(prepared):
    df = valid_summary(prepared)
    with pytest.raises(ValueError, match='Duplicate'):
        validate_monthly_summary(pd.concat([df, df]))
    with pytest.raises(ValueError, match='coverage'):
        validate_monthly_summary(df, '2026-01', '2026-02')
