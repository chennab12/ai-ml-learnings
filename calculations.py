"""Transparent arithmetic behind the calculators and the quiz. Illustrations, not vendor quotes."""
import math
import random
import zlib
from datetime import timedelta
from statistics import NormalDist

WORDS_PER_TOKEN = 0.75  # common rule of thumb for English text; varies by tokenizer and language


def _ratio(num, den):
    return num / den if den else None


def classification_metrics(tp, fp, fn, tn):
    """Accuracy, precision, recall, F1 and specificity from a confusion matrix (None where undefined)."""
    precision, recall = _ratio(tp, tp + fp), _ratio(tp, tp + fn)
    if precision is None or recall is None:
        f1 = None
    else:
        f1 = _ratio(2 * precision * recall, precision + recall) or 0.0
    return {
        "accuracy": _ratio(tp + tn, tp + fp + fn + tn),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "specificity": _ratio(tn, tn + fp),
    }


def llm_cost(requests_per_day, input_tokens, output_tokens, price_in_per_m, price_out_per_m, cached_share_pct=0.0, cache_discount_pct=90.0):
    """Cost per request, day, 30-day month and year. Cached input tokens are billed at a discount."""
    cached = input_tokens * cached_share_pct / 100
    billed_input = (input_tokens - cached) + cached * (1 - cache_discount_pct / 100)
    per_request = (billed_input * price_in_per_m + output_tokens * price_out_per_m) / 1_000_000
    per_day = per_request * requests_per_day
    return {"per_request": per_request, "per_1k": per_request * 1000, "per_day": per_day, "per_month": per_day * 30, "per_year": per_day * 365}


def words_to_tokens(words):
    return math.ceil(words / WORDS_PER_TOKEN)


def tokens_to_words(tokens):
    return math.floor(tokens * WORDS_PER_TOKEN)


def model_memory_gb(params_billion, bytes_per_param, overhead_pct=20.0):
    """(weights GB, weights plus overhead GB) for inference; overhead loosely covers activations and KV cache."""
    weights = params_billion * bytes_per_param
    return weights, weights * (1 + overhead_pct / 100)


def training_memory_gb(params_billion, bytes_per_param=16):
    """Rule of thumb for full fine-tuning with mixed precision and the Adam optimizer (≈ 16 bytes per parameter)."""
    return params_billion * bytes_per_param


def gpus_needed(total_gb, gpu_gb):
    return max(1, math.ceil(total_gb / gpu_gb)) if gpu_gb > 0 else None


def ab_sample_size(baseline_pct, mde_relative_pct, alpha=0.05, power=0.8):
    """Users needed per variant for a two-sided test of two proportions."""
    p1 = baseline_pct / 100
    p2 = p1 * (1 + mde_relative_pct / 100)
    if not 0 < p1 < 1 or not 0 < p2 < 1 or p1 == p2:
        return None
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_beta = NormalDist().inv_cdf(power)
    pooled = (p1 + p2) / 2
    n = (z_alpha * math.sqrt(2 * pooled * (1 - pooled)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return math.ceil(n)


def project_roi(annual_volume, manual_cost_per_item, automation_pct, error_pct, cost_per_error, build_cost, annual_run_cost, years=3):
    """Yearly net benefit, payback months and multi-year ROI of automating part of a manual process."""
    automated = annual_volume * automation_pct / 100
    savings = automated * manual_cost_per_item
    error_cost = automated * error_pct / 100 * cost_per_error
    net = savings - error_cost - annual_run_cost
    payback = build_cost / (net / 12) if net > 0 else None
    roi = (net * years - build_cost) / build_cost if build_cost else None
    return {"savings": savings, "error_cost": error_cost, "net": net, "payback_months": payback, "roi": roi}


def compound_success(step_success_pct, steps):
    """Chance an agent finishes when every one of `steps` must succeed independently."""
    return (step_success_pct / 100) ** steps


def weeks_to_finish(total_hours, hours_per_week):
    return total_hours / hours_per_week if hours_per_week > 0 else None


def study_schedule(items, hours_per_week, start):
    """Start and finish dates for each (title, hours) studied one after another."""
    if hours_per_week <= 0:
        return None
    rows = []
    day = start
    for title, hours in items:
        days = max(1, math.ceil(hours * 7 / hours_per_week))
        finish = day + timedelta(days=days - 1)
        rows.append({"Resource": title, "Hours (≈)": hours, "Start": day, "Finish": finish})
        day = finish + timedelta(days=1)
    return rows


def shuffled_options(item):
    """Options in a stable shuffled order (same every run) and the new index of the right answer."""
    order = list(range(len(item["options"])))
    random.Random(zlib.crc32(item["q"].encode())).shuffle(order)
    return [item["options"][i] for i in order], order.index(item["answer"])


def quiz_score(items, picks):
    """Number of picks (shown option text, or None) matching each item's correct answer."""
    return sum(1 for item, pick in zip(items, picks) if pick == item["options"][item["answer"]])
