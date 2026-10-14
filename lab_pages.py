"""Streamlit renderers for each stage's interactive lab (math lives in labs.py)."""
from functools import partial

import numpy as np
import streamlit as st

import labs

# Bars keep the order of the data (Streamlit sorts category labels alphabetically by default).
bar_chart = partial(st.bar_chart, sort=False)


def lab_overfitting():
    st.caption("Fit curves of growing complexity to 15 noisy points, then test on 200 new points. Watch test error rise once the model starts memorizing noise.")
    noise = st.slider("Noise in the data", 0.05, 0.6, 0.3, 0.05, key="lab_overfit_noise")
    degrees, train, test = labs.overfit_curve(noise)
    best = degrees[int(np.argmin(test))]
    a, b, c = st.columns(3)
    a.metric("Best complexity (lowest test error)", f"degree {best}")
    b.metric("Train error at degree 12", f"{train[-1]:.2f}")
    c.metric("Test error at degree 12", f"{min(test[-1], 99):.2f}", delta=f"{min(test[-1], 99) - min(test):+.2f} vs best", delta_color="inverse")
    st.line_chart({"Model complexity (degree)": degrees, "Train error": train, "Test error": [min(t, 3) for t in test]},
                  x="Model complexity (degree)", y_label="Error (RMSE, capped at 3)")
    st.caption("Left of the best point: underfitting. Right: overfitting. Train error keeps falling, which is why it can't be trusted on its own.")


def lab_threshold():
    st.caption("A synthetic model scores 20,000 cases. Move the threshold and see precision, recall, alert volume and the cost of errors change.")
    a, b = st.columns(2)
    prevalence = a.slider("Share of real positives (%)", 0.5, 30.0, 5.0, 0.5, key="lab_thr_prev")
    separation = a.slider("Model quality (score separation)", 0.05, 0.6, 0.3, 0.05, key="lab_thr_sep")
    cost_fp = b.number_input("Cost of a false alarm ($)", 0.0, 10_000.0, 5.0, key="lab_thr_fp")
    cost_fn = b.number_input("Cost of a miss ($)", 0.0, 100_000.0, 200.0, key="lab_thr_fn")
    rows, best = labs.threshold_sweep(prevalence, separation, cost_fp, cost_fn)
    t = st.select_slider("Threshold", [r["threshold"] for r in rows], 0.5, key="lab_thr_t")
    row = next(r for r in rows if r["threshold"] == t)
    x, y, z, w = st.columns(4)
    x.metric("Precision", "n/a" if row["precision"] is None else f"{row['precision']:.0%}")
    y.metric("Recall", f"{row['recall']:.0%}")
    z.metric("Alerts per 1,000", f"{row['alerts_per_1k']:.0f}")
    w.metric("Error cost per 1,000", f"${row['cost_per_1k']:,.0f}", delta=f"best ${best['cost_per_1k']:,.0f} at {best['threshold']}", delta_color="off")
    st.line_chart({"Threshold": [r["threshold"] for r in rows], "Precision": [r["precision"] or 0 for r in rows], "Recall": [r["recall"] for r in rows]},
                  x="Threshold", y_label="Rate")
    bar_chart({"Threshold": [r["threshold"] for r in rows], "Error cost per 1,000 ($)": [r["cost_per_1k"] for r in rows]}, x="Threshold", y="Error cost per 1,000 ($)")
    st.success(f"💡 Lowest-cost threshold here: **{best['threshold']}**. Notice it is usually not 0.5, and it moves when error costs change.")


def lab_gradient():
    st.caption("Gradient descent fits a line to 100 points generated from y = 3x + 2 plus noise. Try a tiny, a good and a too-large learning rate.")
    a, b = st.columns(2)
    lr = a.select_slider("Learning rate", [0.001, 0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 1.0], 0.1, key="lab_gd_lr")
    steps = b.slider("Steps", 5, 200, 50, 5, key="lab_gd_steps")
    losses, (w, bias), diverged = labs.gradient_descent(lr, steps)
    x, y, z = st.columns(3)
    x.metric("Final loss (MSE)", "diverged 💥" if diverged else f"{losses[-1]:.3f}")
    y.metric("Learned slope (true 3)", "—" if diverged else f"{w:.2f}")
    z.metric("Learned intercept (true 2)", "—" if diverged else f"{bias:.2f}")
    st.line_chart({"Step": list(range(len(losses))), "Loss": [min(v, 50) for v in losses]}, x="Step", y_label="Loss (capped at 50)")
    if diverged:
        st.error("The learning rate is too large: each step overshoots the valley and the loss explodes.")
    elif losses[-1] > 0.2:
        st.warning("Still learning: the learning rate is small or there are too few steps.")
    else:
        st.success("Converged: the model found a line close to the true one.")


def lab_attention():
    st.caption("A toy self-attention step on one sentence. Each word is a hand-made 4-number vector (living thing, place, function word, feeling), not trained values.")
    a, b = st.columns(2)
    idx = a.selectbox("Word that is 'looking' at the sentence", range(len(labs.ATTN_TOKENS)), index=7, format_func=lambda i: f"{i + 1}. {labs.ATTN_TOKENS[i]}", key="lab_attn_word")
    temp = b.slider("Temperature (lower = sharper focus)", 0.1, 2.0, 0.5, 0.1, key="lab_attn_temp")
    weights = labs.attention_weights(idx, temp)
    bar_chart({"Word": [f"{i + 1:02}. {t}" for i, t in enumerate(labs.ATTN_TOKENS)], "Attention weight": weights}, x="Word", y="Attention weight")
    others = [(w, t) for i, (w, t) in enumerate(zip(weights, labs.ATTN_TOKENS)) if i != idx]
    top_w, top_t = max(others)
    st.metric(f"Strongest link from '{labs.ATTN_TOKENS[idx]}' (excluding itself)", top_t, delta=f"{top_w:.0%} of attention", delta_color="off")
    st.caption("With 'it' selected, attention points to 'animal' and 'tired': the model uses context to resolve what 'it' means. Real models learn these vectors and use many attention heads.")


def lab_retriever():
    st.caption("The retrieval step of RAG on eight short sample policies. Scores use word overlap (cosine similarity of word counts); real systems use embeddings, which also match synonyms.")
    q = st.text_input("Ask a policy question", "How many days do I have to submit expense receipts?", key="lab_rag_q")
    k = st.slider("Passages to retrieve (top k)", 1, 5, 3, key="lab_rag_k")
    hits = labs.retrieve(q, k=k)
    if not hits:
        st.info("Type a question with at least one meaningful word.")
        return
    bar_chart({"Document": [t for t, _, _ in hits], "Similarity": [s for _, s, _ in hits]}, x="Document", y="Similarity", horizontal=True)
    st.dataframe([{"Rank": i, "Document": t, "Score": round(s, 3), "Passage": body} for i, (t, s, body) in enumerate(hits, 1)], hide_index=True, width="stretch")
    with st.expander("🧾 The prompt that would be sent to the LLM"):
        st.code(labs.build_prompt(q, hits), language="text")
    st.caption("Try 'Can I fly business class?' or 'What if I lose my computer?'. The second one shows why keyword matching misses synonyms ('computer' vs 'laptop').")


def lab_evals():
    st.caption("A tiny eval harness: 10 questions with the facts a correct answer must contain, run against two illustrative model outputs. Real eval sets start at 50-100 cases.")
    rows = labs.run_evals()
    a_rate = sum(r["A ✅"] for r in rows) / len(rows)
    b_rate = sum(r["B ✅"] for r in rows) / len(rows)
    a, b = st.columns(2)
    cost_a = a.number_input("Model A cost per call ($)", 0.0001, 1.0, 0.004, 0.001, format="%.4f", key="lab_eval_ca")
    cost_b = b.number_input("Model B cost per call ($)", 0.0001, 1.0, 0.001, 0.001, format="%.4f", key="lab_eval_cb")
    x, y, z, w = st.columns(4)
    x.metric("Model A pass rate", f"{a_rate:.0%}")
    y.metric("Model B pass rate", f"{b_rate:.0%}")
    z.metric("A cost per correct answer", f"${labs.cost_per_success(a_rate, cost_a):.4f}")
    w.metric("B cost per correct answer", f"${labs.cost_per_success(b_rate, cost_b):.4f}")
    bar_chart({"Model": ["Model A", "Model B"], "Pass rate": [a_rate, b_rate]}, x="Model", y="Pass rate")
    st.dataframe(rows, hide_index=True, width="stretch")
    launch_bar = st.slider("Launch bar: minimum pass rate", 0.5, 1.0, 0.9, 0.05, key="lab_eval_bar")
    ok = [m for m, r in (("Model A", a_rate), ("Model B", b_rate)) if r >= launch_bar]
    if ok:
        st.success(f"✅ Meets the launch bar: {', '.join(ok)}")
    else:
        st.error("❌ Neither model meets the launch bar.")
    st.caption("Cheaper per call is not cheaper per correct answer. Look at B's failures: missing facts, which a RAG step or better prompt could fix.")


def lab_drift():
    st.caption("Compare one input feature at training time with production. Shift or widen production data and watch the population stability index (PSI).")
    a, b = st.columns(2)
    shift = a.slider("Production mean shift", -20.0, 20.0, 4.0, 1.0, key="lab_drift_shift")
    spread = b.slider("Production spread (× training)", 0.5, 2.0, 1.0, 0.1, key="lab_drift_spread")
    train, prod = labs.drift_samples(shift, spread)
    value = labs.psi(train, prod)
    x, y = st.columns(2)
    x.metric("PSI", f"{value:.3f}")
    y.metric("Status", labs.psi_status(value))
    edges = np.linspace(0, 100, 26)
    centers = ((edges[:-1] + edges[1:]) / 2).round(0)
    bar_chart({"Feature value": centers,
                  "Training": np.histogram(train, edges)[0] / len(train),
                  "Production": np.histogram(prod, edges)[0] / len(prod)},
                 x="Feature value", y=["Training", "Production"], stack=False)
    st.caption("Rule of thumb: PSI under 0.1 stable, 0.1-0.25 investigate, above 0.25 act. Pair input drift with business-outcome monitoring.")


def lab_fairness():
    st.caption("One threshold, two groups. Group B's real positives score lower (for example, because they were under-represented in training data).")
    a, b = st.columns(2)
    threshold = a.slider("Decision threshold", 0.2, 0.8, 0.5, 0.05, key="lab_fair_t")
    gap = b.slider("How much lower group B's positives score", 0.0, 0.3, 0.1, 0.02, key="lab_fair_gap")
    rates = labs.group_rates(threshold, gap)
    tpr_gap = rates["Group A"]["TPR (recall)"] - rates["Group B"]["TPR (recall)"]
    x, y, z = st.columns(3)
    x.metric("Recall, group A", f"{rates['Group A']['TPR (recall)']:.0%}")
    y.metric("Recall, group B", f"{rates['Group B']['TPR (recall)']:.0%}")
    z.metric("Recall gap", f"{tpr_gap:.0%}", delta="above 5 points: review" if tpr_gap > 0.05 else "within 5 points", delta_color="inverse" if tpr_gap > 0.05 else "normal")
    bar_chart({"Group": ["Group A", "Group B"],
                  "Recall": [rates[g]["TPR (recall)"] for g in ("Group A", "Group B")],
                  "False alarm rate": [rates[g]["FPR (false alarms)"] for g in ("Group A", "Group B")]},
                 x="Group", y=["Recall", "False alarm rate"], stack=False)
    st.caption("The overall average hides the gap. Fixes include better data for group B and reviewing thresholds with legal; the 5-point limit is an example, set yours with your policy team.")


def lab_schedule():
    st.caption("Monte Carlo forecast: each phase gets a min / most likely / max estimate in weeks; 5,000 simulated runs give the odds of each finish time.")
    defaults = [("Data access & labeling", 3, 5, 10), ("Feasibility spike", 2, 3, 5), ("Pilot", 4, 6, 10), ("Scale & launch", 5, 8, 14)]
    phases = []
    for i, (name, lo, ml, hi) in enumerate(defaults):
        c0, c1, c2, c3 = st.columns([2, 1, 1, 1])
        c0.markdown(f"**{name}**")
        phases.append((c1.number_input("Min", 0, 52, lo, key=f"lab_mc_{i}_lo"), c2.number_input("Likely", 0, 52, ml, key=f"lab_mc_{i}_ml"),
                       c3.number_input("Max", 0, 104, hi, key=f"lab_mc_{i}_hi")))
    totals = labs.monte_carlo_schedule(phases)
    p = labs.percentiles(totals)
    naive = sum(ml for _, ml, _ in phases)
    x, y, z, w = st.columns(4)
    x.metric("Sum of 'likely'", f"{naive} wk")
    y.metric("P50", f"{p[50]:.1f} wk")
    z.metric("P80 (commit to this)", f"{p[80]:.1f} wk")
    w.metric("P95", f"{p[95]:.1f} wk")
    counts, edges = np.histogram(totals, bins=20)
    bar_chart({"Weeks": ((edges[:-1] + edges[1:]) / 2).round(1), "Simulated runs": counts}, x="Weeks", y="Simulated runs")
    st.info(f"📌 Adding up 'most likely' estimates gives {naive} weeks, but there is only about a {(totals <= naive).mean():.0%} chance of finishing by then. Uncertainty is skewed late.")


def lab_scorecard():
    st.caption("Rate your evidence for each senior-level signal: 0 none, 1 partial, 2 solid, 3 strong and visible. Weights reflect what promotion committees usually value most.")
    scores = []
    for i, (item, weight) in enumerate(labs.EVIDENCE):
        scores.append(st.select_slider(f"{item} (weight {weight})", [0, 1, 2, 3], 1, key=f"lab_card_{i}"))
    ready = labs.readiness(scores)
    st.metric("Readiness", f"{ready:.0%}", delta="strong case" if ready >= 0.7 else "build more evidence", delta_color="normal" if ready >= 0.7 else "off")
    st.progress(ready)
    bar_chart({"Evidence": [e for e, _ in labs.EVIDENCE], "Weighted gap": [w * (3 - s) for (_, w), s in zip(labs.EVIDENCE, scores)]}, x="Evidence", y="Weighted gap", horizontal=True)
    worst = max(zip([w * (3 - s) for (_, w), s in zip(labs.EVIDENCE, scores)], [e for e, _ in labs.EVIDENCE]))
    st.success(f"🎯 Biggest weighted gap to close next: **{worst[1]}**")


# (lab title, renderer), keyed by stage title.
LABS = {
    "AI & ML foundations": ("Overfitting in action", lab_overfitting),
    "Measuring models": ("Threshold trade-off explorer", lab_threshold),
    "Classic ML algorithms": ("Gradient descent, step by step", lab_gradient),
    "Deep learning": ("Toy attention: what does 'it' look at?", lab_attention),
    "Generative AI & LLMs": ("Mini retriever: the 'R' in RAG", lab_retriever),
    "Building LLM products": ("Mini eval harness: which model ships?", lab_evals),
    "MLOps & AI infrastructure": ("Drift detector (PSI)", lab_drift),
    "Responsible AI & governance": ("Fairness slices", lab_fairness),
    "AI program management": ("Monte Carlo schedule forecast", lab_schedule),
    "Senior AI TPM career": ("Promotion evidence scorecard", lab_scorecard),
}
