import numpy as np

import labs


def test_overfitting_shows_u_shaped_test_error():
    degrees, train, test = labs.overfit_curve()
    assert train[-1] < train[0]  # more complexity always fits training data better
    best = int(np.argmin(test))
    assert 0 < best < len(degrees) - 1 and test[-1] > test[best]


def test_threshold_sweep_trades_precision_for_recall():
    rows, best = labs.threshold_sweep()
    recalls = [r["recall"] for r in rows]
    assert recalls == sorted(recalls, reverse=True)
    assert best["cost_per_1k"] == min(r["cost_per_1k"] for r in rows)
    _, cheap_misses = labs.threshold_sweep(cost_fn=1, cost_fp=50)
    assert cheap_misses["threshold"] > best["threshold"]  # costly false alarms push the threshold up


def test_gradient_descent_converges_or_diverges():
    losses, (w, b), diverged = labs.gradient_descent(0.1, 200)
    assert not diverged and abs(w - 3) < 0.3 and abs(b - 2) < 0.3
    assert labs.gradient_descent(1.0, 50)[2]


def test_attention_is_a_distribution_and_it_links_to_animal():
    weights = labs.attention_weights(labs.ATTN_TOKENS.index("it"))
    assert abs(sum(weights) - 1) < 1e-9
    others = [(w, t) for w, t in zip(weights, labs.ATTN_TOKENS) if t != "it"]
    assert max(others)[1] == "animal"


def test_retriever_ranks_the_right_policy_first():
    assert labs.retrieve("submit expense claims receipts")[0][0] == "Expenses: submitting claims"
    assert labs.retrieve("the of")[:1] == []
    assert "[1]" in labs.build_prompt("q", labs.retrieve("laptop stolen"))


def test_eval_harness():
    rows = labs.run_evals()
    assert sum(r["A ✅"] for r in rows) > sum(r["B ✅"] for r in rows)
    assert labs.cost_per_success(0.5, 0.002) == 0.004 and labs.cost_per_success(0, 1) is None


def test_psi_grows_with_drift():
    small = labs.psi(*labs.drift_samples(0))
    big = labs.psi(*labs.drift_samples(10))
    assert small < 0.1 < 0.25 < big
    assert labs.psi_status(small).startswith("🟢") and labs.psi_status(big).startswith("🔴")


def test_fairness_gap_appears_when_group_b_scores_lower():
    same = labs.group_rates(gap=0.0)
    lower = labs.group_rates(gap=0.2)
    assert abs(same["Group A"]["TPR (recall)"] - same["Group B"]["TPR (recall)"]) < 0.03
    assert lower["Group A"]["TPR (recall)"] - lower["Group B"]["TPR (recall)"] > 0.3


def test_monte_carlo_is_skewed_late():
    phases = [(3, 5, 10), (2, 3, 5), (4, 6, 10), (5, 8, 14)]
    p = labs.percentiles(labs.monte_carlo_schedule(phases))
    assert p[50] > sum(ml for _, ml, _ in phases) and p[50] < p[80] < p[95]
    assert labs.percentiles(labs.monte_carlo_schedule([(4, 4, 4)]))[80] == 4


def test_readiness():
    assert labs.readiness([3] * len(labs.EVIDENCE)) == 1
    assert labs.readiness([0] * len(labs.EVIDENCE)) == 0
