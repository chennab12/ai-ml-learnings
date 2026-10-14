from datetime import date

import pytest

from calculations import (
    ab_sample_size,
    classification_metrics,
    compound_success,
    gpus_needed,
    llm_cost,
    model_memory_gb,
    project_roi,
    quiz_score,
    review_load,
    shuffled_options,
    study_schedule,
    tokens_to_words,
    training_memory_gb,
    weeks_to_finish,
    words_to_tokens,
)


def test_classification_metrics():
    m = classification_metrics(tp=90, fp=10, fn=30, tn=870)
    assert m["precision"] == pytest.approx(0.9)
    assert m["recall"] == pytest.approx(0.75)
    assert m["accuracy"] == pytest.approx(0.96)
    assert m["f1"] == pytest.approx(2 * 0.9 * 0.75 / 1.65)


def test_classification_metrics_edge_cases():
    m = classification_metrics(0, 0, 10, 990)  # never predicts positive
    assert m["accuracy"] == pytest.approx(0.99)
    assert m["precision"] is None and m["recall"] == 0 and m["f1"] is None
    assert classification_metrics(0, 5, 5, 0)["f1"] == 0.0


def test_llm_cost():
    c = llm_cost(1000, 1_000_000, 0, 3.0, 15.0)
    assert c["per_request"] == pytest.approx(3.0)
    assert c["per_month"] == pytest.approx(90_000)
    full = llm_cost(1, 1_000_000, 0, 10, 0)["per_request"]
    cached = llm_cost(1, 1_000_000, 0, 10, 0, cached_share_pct=100, cache_discount_pct=90)["per_request"]
    assert cached == pytest.approx(full * 0.1)


def test_tokens_round_trip():
    assert words_to_tokens(750) == 1000
    assert tokens_to_words(1000) == 750


def test_memory_rules_of_thumb():
    assert model_memory_gb(7, 2) == pytest.approx((14, 16.8))
    assert model_memory_gb(70, 0.5, overhead_pct=0)[1] == pytest.approx(35)
    assert training_memory_gb(7) == 112
    assert gpus_needed(160, 80) == 2 and gpus_needed(161, 80) == 3 and gpus_needed(1, 80) == 1


def test_ab_sample_size_matches_reference():
    # 10% baseline, 10% relative lift, alpha 0.05, power 0.8 ≈ 14,750 per variant (standard calculators agree).
    assert 14_700 <= ab_sample_size(10, 10) <= 14_800
    assert ab_sample_size(10, 5) > 3.5 * ab_sample_size(10, 10)  # halving the effect ≈ 4x the sample
    assert ab_sample_size(60, 100) is None


def test_project_roi():
    r = project_roi(100_000, 5, 50, 2, 50, 100_000, 50_000)
    assert r["savings"] == 250_000
    assert r["error_cost"] == 50_000
    assert r["net"] == 150_000
    assert r["payback_months"] == pytest.approx(8)
    assert r["roi"] == pytest.approx(3.5)
    assert project_roi(10, 1, 10, 0, 0, 1000, 1000)["payback_months"] is None


def test_agent_reliability_compounds():
    assert compound_success(90, 7) == pytest.approx(0.478, rel=0.01)
    assert compound_success(95, 1) == pytest.approx(0.95)


def test_study_schedule_is_back_to_back():
    rows = study_schedule([("A", 5), ("B", 10)], 5, date(2026, 1, 1))
    assert rows[0]["Finish"] == date(2026, 1, 7)
    assert rows[1]["Start"] == date(2026, 1, 8)
    assert rows[1]["Finish"] == date(2026, 1, 21)
    assert study_schedule([("A", 5)], 0, date(2026, 1, 1)) is None
    assert weeks_to_finish(100, 5) == 20 and weeks_to_finish(10, 0) is None


def test_shuffled_options_keep_the_right_answer_and_are_stable():
    item = {"q": "Which is right?", "options": ["a", "b", "c", "d"], "answer": 2}
    options, answer = shuffled_options(item)
    assert sorted(options) == ["a", "b", "c", "d"]
    assert options[answer] == "c"
    assert shuffled_options(item) == (options, answer)


def test_quiz_score():
    items = [{"options": ["x", "y"], "answer": 1}, {"options": ["x", "y"], "answer": 0}]
    assert quiz_score(items, ["y", "x"]) == 2
    assert quiz_score(items, ["x", None]) == 0


def test_review_load():
    reviews, hours, people = review_load(6000, 10, 3, 6)
    assert reviews == 600 and hours == 30 and people == 5
