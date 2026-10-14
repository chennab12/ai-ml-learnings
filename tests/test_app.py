"""Smoke tests: every section and calculator renders, navigation, plan and quiz work."""
from streamlit.testing.v1 import AppTest

from content import FAST_TRACK, STAGES
from resources import RESOURCES

CALCS = ["🎯 Precision & recall", "💸 LLM cost", "🔢 Tokens & context", "🖥️ GPU memory",
         "🧪 A/B sample size", "📈 AI project ROI", "🦾 Agent reliability", "⏱️ Study time",
         "🎲 Schedule risk (P50/P80)", "👥 Human review load"]


def run(section=None):
    at = AppTest.from_file("../app.py", default_timeout=30)
    if section is not None:
        at.session_state["section"] = section
    at.run()
    assert not at.exception, at.exception
    return at


def test_every_section_renders():
    at = run()
    for section in at.sidebar.radio[0].options:
        run(section)


def test_next_stage_button_advances():
    at = run(STAGES[0]["name"])
    [b for b in at.button if b.label == "Next stage →"][0].click().run()
    assert at.session_state["section"] == STAGES[1]["name"]


def test_fast_track_fills_plan():
    at = run()
    [b for b in at.button if b.label.startswith("➕ Add the fast track")][0].click().run()
    assert at.session_state["plan"] == [k for k in FAST_TRACK if RESOURCES[k]["hours"]]
    at.session_state["section"] = "🗓️ My learning plan"
    at.run()
    assert not at.exception, at.exception


def test_quick_check_gives_feedback():
    at = run(STAGES[0]["name"])
    at.radio(key=f"tq_{STAGES[0]['topics'][0]['title']}_0").set_value(at.radio(key=f"tq_{STAGES[0]['topics'][0]['title']}_0").options[0]).run()
    assert not at.exception, at.exception
    assert len(at.success) + len(at.error) >= 2  # gist banner plus the answer feedback


def test_stage_quiz_button_filters_quiz_and_scores():
    at = run(STAGES[2]["name"])
    [b for b in at.button if b.label.startswith("📝 Take the full")][0].click().run()
    assert at.session_state["section"] == "📝 Quiz center"
    assert at.session_state["quiz_stages"] == [STAGES[2]["name"]]
    radios = [r for r in at.radio if r.key and r.key.startswith("quiz_")]
    assert radios
    for r in radios:
        r.set_value(r.options[0])
    [b for b in at.button if b.label == "✅ Check my answers"][0].click().run()
    assert not at.exception, at.exception
    assert len(at.session_state["quiz_history"]) == 1
    score, total = at.session_state["quiz_history"][0]
    assert total == len(radios) and 0 <= score <= total


def test_each_calculator_renders():
    at = run("🧮 Calculators")
    for option in CALCS:
        at.button_group[0].set_value(option).run()
        assert not at.exception, at.exception


def test_deep_link_opens_section():
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.query_params["page"] = "generative-ai-llms"
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["section"] == STAGES[4]["name"]


def test_missed_questions_feed_review_mode():
    at = run("📝 Quiz center")
    [b for b in at.button if b.label == "✅ Check my answers"][0].click().run()  # all unanswered = all missed
    missed = at.session_state["missed"]
    assert len(missed) == 10
    at.button_group(key="quiz_mode").set_value("🔁 My missed questions (10)").run()
    assert not at.exception, at.exception
    shown = [r.label for r in at.radio if r.key and r.key.startswith("quiz_")]
    assert shown and all(any(q in label for q in missed) for label in shown)
    assert at.session_state["quiz_stats"]


def test_search_finds_concepts():
    at = run("🔎 Search everything")
    at.text_input[0].set_value("drift").run()
    assert not at.exception, at.exception
    assert any(b.label == "Open stage →" for b in at.button)


def test_continue_button_opens_first_unmastered_stage():
    at = run()
    [b for b in at.button if b.label.startswith("▶️ Continue")][0].click().run()
    assert at.session_state["section"] == STAGES[0]["name"]


def test_every_stage_lab_responds_to_input():
    at = run(STAGES[6]["name"])
    at.slider(key="lab_drift_shift").set_value(15.0).run()
    assert not at.exception, at.exception
    at = run(STAGES[2]["name"])
    at.select_slider(key="lab_gd_lr").set_value(1.0).run()
    assert not at.exception, at.exception
    assert any("too large" in e.value for e in at.error)


def test_prerequisite_review_button_goes_to_earlier_stage():
    at = run(STAGES[4]["name"])
    [b for b in at.button if b.label == f"↩️ Review {STAGES[3]['name']}"][0].click().run()
    assert at.session_state["section"] == STAGES[3]["name"]
