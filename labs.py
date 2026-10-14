"""Small, real implementations behind each stage's interactive lab. Pure functions, no Streamlit.

Data is synthetic or toy-sized on purpose, so every lab runs instantly in the browser
session and shows the core idea. Real systems use real data and proper libraries.
"""
import math
import re
import warnings

import numpy as np

# ── 🧱 Foundations: overfitting ───────────────────────────────────────────


def overfit_curve(noise=0.3, n_train=15, n_test=200, max_degree=12, seed=7):
    """Fit polynomials of growing degree to noisy sine data; return train and test RMSE per degree."""
    rng = np.random.default_rng(seed)
    x_tr, x_te = rng.uniform(0, 1, n_train), rng.uniform(0, 1, n_test)
    truth = lambda x: np.sin(2 * np.pi * x)  # noqa: E731
    y_tr = truth(x_tr) + rng.normal(0, noise, n_train)
    y_te = truth(x_te) + rng.normal(0, noise, n_test)
    degrees, train_err, test_err = [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for d in range(1, max_degree + 1):
            coef = np.polyfit(x_tr, y_tr, d)
            degrees.append(d)
            train_err.append(float(np.sqrt(np.mean((np.polyval(coef, x_tr) - y_tr) ** 2))))
            test_err.append(float(np.sqrt(np.mean((np.polyval(coef, x_te) - y_te) ** 2))))
    return degrees, train_err, test_err


# ── 📏 Measuring: threshold trade-off ─────────────────────────────────────


def threshold_sweep(prevalence_pct=5.0, separation=0.3, cost_fp=5.0, cost_fn=200.0, n=20_000, seed=1):
    """Synthetic model scores; precision, recall and error cost per 1,000 cases for each threshold."""
    rng = np.random.default_rng(seed)
    n_pos = max(1, int(n * prevalence_pct / 100))
    neg = np.clip(rng.normal(0.35, 0.15, n - n_pos), 0, 1)
    pos = np.clip(rng.normal(0.35 + separation, 0.15, n_pos), 0, 1)
    rows = []
    for t in np.round(np.arange(0.05, 0.96, 0.05), 2):
        tp, fn = int((pos >= t).sum()), int((pos < t).sum())
        fp = int((neg >= t).sum())
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / n_pos
        cost = (fp * cost_fp + fn * cost_fn) / n * 1000
        rows.append({"threshold": float(t), "precision": precision, "recall": recall, "cost_per_1k": cost, "alerts_per_1k": (tp + fp) / n * 1000})
    best = min(rows, key=lambda r: r["cost_per_1k"])
    return rows, best


# ── 🧮 Classic ML: gradient descent ───────────────────────────────────────


def gradient_descent(learning_rate=0.1, steps=50, seed=3, true_w=3.0, true_b=2.0):
    """Fit y = w·x + b to noisy data with plain gradient descent; return losses and final (w, b)."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 2, 100)
    y = true_w * x + true_b + rng.normal(0, 0.3, 100)
    w = b = 0.0
    losses = []
    for _ in range(steps):
        err = w * x + b - y
        loss = float(np.mean(err ** 2))
        if not math.isfinite(loss) or loss > 1e9:
            losses.append(1e9)
            return losses, (float("nan"), float("nan")), True
        losses.append(loss)
        w -= learning_rate * float(np.mean(2 * err * x))
        b -= learning_rate * float(np.mean(2 * err))
    return losses, (w, b), False


# ── 🕸️ Deep learning: toy attention ───────────────────────────────────────

ATTN_TOKENS = ["The", "animal", "didn't", "cross", "the", "street", "because", "it", "was", "tired"]
# Hand-made 4-d vectors: [living thing, place, function word, state/feeling]. A toy, not trained values.
_ATTN_VECS = np.array([
    [0.0, 0.0, 1.0, 0.0], [1.0, 0.1, 0.0, 0.3], [0.1, 0.0, 0.8, 0.1], [0.3, 0.4, 0.2, 0.0], [0.0, 0.0, 1.0, 0.0],
    [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.9, 0.1], [0.9, 0.1, 0.3, 0.5], [0.1, 0.0, 0.7, 0.3], [0.5, 0.0, 0.0, 1.0],
])


def attention_weights(query_index, temperature=0.5):
    """Softmax of scaled dot products between one token and every token in the sentence."""
    scores = _ATTN_VECS @ _ATTN_VECS[query_index] / max(temperature, 1e-3)
    exp = np.exp(scores - scores.max())
    return (exp / exp.sum()).tolist()


# ── ✨ GenAI: a tiny retriever, the 'R' in RAG ────────────────────────────

POLICY_DOCS = {
    "Travel: booking flights": "Book flights through the company travel portal at least 14 days before departure. Economy class is standard for flights under six hours.",
    "Travel: hotel limits": "Hotel stays are reimbursed up to the city rate listed in the travel portal. Share the receipt within 30 days.",
    "Expenses: meals": "Meals while travelling are reimbursed up to a daily limit. Alcohol is not reimbursed. Attach itemized receipts.",
    "Expenses: submitting claims": "Submit expense claims in the finance tool within 30 days with receipts. Your manager approves claims.",
    "Leave: vacation days": "Full-time employees get vacation days that accrue monthly. Request leave in the HR portal two weeks ahead.",
    "Leave: sick days": "Sick days do not need advance approval. Tell your manager the same day and log it in the HR portal.",
    "Equipment: laptops": "New laptops are issued by IT on your first day. Report lost or stolen laptops to IT security immediately.",
    "Remote work": "Remote work is allowed up to three days a week with manager agreement. Home office equipment can be requested from IT.",
}
_STOP = set("a an the of to in for on at by is are be with your you and or it this that do does can i my how what when who where".split())


def _words(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in _STOP]


def retrieve(query, docs=None, k=3):
    """Rank documents by cosine similarity of word counts (a simple stand-in for embedding search)."""
    docs = docs or POLICY_DOCS
    q = _words(query)
    if not q:
        return []
    vocab = sorted(set(q) | {w for t, body in docs.items() for w in _words(t + " " + body)})
    index = {w: i for i, w in enumerate(vocab)}

    def vec(words):
        v = np.zeros(len(vocab))
        for w in words:
            v[index[w]] += 1
        return v

    qv = vec(q)
    scored = []
    for title, body in docs.items():
        dv = vec(_words(title + " " + body))
        denom = np.linalg.norm(qv) * np.linalg.norm(dv)
        scored.append((title, float(qv @ dv / denom) if denom else 0.0, body))
    scored.sort(key=lambda r: -r[1])
    return scored[:k]


def build_prompt(question, passages):
    sources = "\n".join(f"[{i}] {title}: {body}" for i, (title, _, body) in enumerate(passages, 1))
    return (
        "Answer the question using only the sources below. Cite sources like [1]. "
        "If the sources don't contain the answer, say you don't know.\n\n"
        f"Sources:\n{sources}\n\nQuestion: {question}"
    )


# ── 🤖 LLM products: a tiny eval harness ─────────────────────────────────

# (question, facts a good answer must contain, illustrative output from model A, from model B)
EVAL_CASES = [
    ("How far ahead should I book flights?", ["14 days", "portal"], "Book in the travel portal at least 14 days ahead.", "Book early through the portal."),
    ("Is alcohol reimbursed?", ["not reimbursed"], "No, alcohol is not reimbursed.", "Alcohol is not reimbursed with meals."),
    ("When must I submit expenses?", ["30 days", "receipts"], "Within 30 days, with receipts.", "Within 30 days in the finance tool."),
    ("Who approves expense claims?", ["manager"], "Your manager approves them.", "Your manager approves claims."),
    ("How do I request vacation?", ["HR portal", "two weeks"], "In the HR portal, two weeks ahead.", "Use the HR portal two weeks ahead."),
    ("Do sick days need approval?", ["no", "same day"], "No advance approval; tell your manager the same day.", "They need approval from HR."),
    ("What if my laptop is stolen?", ["IT security", "immediately"], "Report it to IT security immediately.", "Report it to IT security immediately."),
    ("How many remote days are allowed?", ["three days"], "Up to three days a week with manager agreement.", "Two days a week."),
    ("What class can I fly for a 4-hour flight?", ["economy"], "Economy class for flights under six hours.", "Economy class is standard."),
    ("What is the hotel limit?", ["city rate"], "Up to the city rate in the travel portal.", "Up to the city rate listed in the portal."),
]


def run_evals(cases=None):
    """Score each model's output: a case passes if it contains every required fact (case-insensitive)."""
    cases = cases or EVAL_CASES
    rows = []
    for question, facts, out_a, out_b in cases:
        rows.append({
            "Question": question,
            "Must include": ", ".join(facts),
            "Model A": out_a, "A ✅": all(f.lower() in out_a.lower() for f in facts),
            "Model B": out_b, "B ✅": all(f.lower() in out_b.lower() for f in facts),
        })
    return rows


def cost_per_success(pass_rate, cost_per_call):
    return cost_per_call / pass_rate if pass_rate else None


# ── ⚙️ MLOps: drift with the population stability index ──────────────────


def drift_samples(shift=0.0, spread=1.0, n=5_000, seed=11):
    """Training-time and production samples of one feature (production can shift and widen)."""
    rng = np.random.default_rng(seed)
    return rng.normal(50, 10, n), rng.normal(50 + shift, 10 * spread, n)


def psi(expected, actual, bins=10):
    """Population stability index using quantile bins of the expected (training) data."""
    edges = np.quantile(expected, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    e = np.histogram(expected, edges)[0] / len(expected)
    a = np.histogram(actual, edges)[0] / len(actual)
    e, a = np.clip(e, 1e-6, None), np.clip(a, 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))


def psi_status(value):
    if value < 0.1:
        return "🟢 Stable"
    if value < 0.25:
        return "🟡 Investigate"
    return "🔴 Act now"


# ── 🛡️ Responsible AI: fairness slices ───────────────────────────────────


def group_rates(threshold=0.5, gap=0.1, n=4_000, seed=5):
    """True and false positive rates for two groups when group B's positives score `gap` lower."""
    rng = np.random.default_rng(seed)
    out = {}
    for group, shift in (("Group A", 0.0), ("Group B", gap)):
        pos = np.clip(rng.normal(0.65 - shift, 0.15, n), 0, 1)
        neg = np.clip(rng.normal(0.35, 0.15, n), 0, 1)
        out[group] = {"TPR (recall)": float((pos >= threshold).mean()), "FPR (false alarms)": float((neg >= threshold).mean())}
    return out


# ── 🧭 Program management: Monte Carlo schedule ──────────────────────────


def monte_carlo_schedule(phases, runs=5_000, seed=42):
    """Total weeks across sequential phases, each drawn from a triangular (min, likely, max) estimate."""
    rng = np.random.default_rng(seed)
    total = np.zeros(runs)
    for low, likely, high in phases:
        low, high = min(low, likely, high), max(low, likely, high)
        likely = min(max(likely, low), high)
        total += low if high == low else rng.triangular(low, likely, high, runs)
    return total


def percentiles(values, points=(50, 80, 95)):
    return {p: float(np.percentile(values, p)) for p in points}


# ── 🚀 Career: evidence scorecard ────────────────────────────────────────

EVIDENCE = [
    ("Led a cross-team AI program end to end", 3),
    ("Owned an AI launch decision with evals", 3),
    ("Wrote a strategy or design doc leaders acted on", 2),
    ("Built a hands-on demo (RAG, evals, agent)", 1),
    ("Mentored or trained others on AI", 2),
    ("Earned a relevant certification", 1),
]


def readiness(scores, items=None):
    """Weighted readiness (0-1) from 0-3 scores per evidence item."""
    items = items or EVIDENCE
    total = sum(w * 3 for _, w in items)
    return sum(w * s for (_, w), s in zip(items, scores)) / total if total else 0.0
