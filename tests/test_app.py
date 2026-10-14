"""Smoke tests: every section and calculator renders, navigation, plan and quiz work."""
from streamlit.testing.v1 import AppTest

from content import FAST_TRACK, STAGES
from resources import RESOURCES

CALCS = ["🎯 Precision & recall", "💸 LLM cost", "🔢 Tokens & context", "🖥️ GPU memory",
         "🧪 A/B sample size", "📈 AI project ROI", "🦾 Agent reliability", "⏱️ Study time"]


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
