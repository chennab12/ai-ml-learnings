"""Catalog integrity: every topic is complete, references resolve, quizzes are well formed."""
from collections import Counter

from calculations import shuffled_options
from content import FAST_TRACK, GLOSSARY, SKILL_LADDER, STAGE_LEVELS, STAGES
from lab_pages import LABS
from practice import PRACTICE, TIPS
from resources import KINDS, LEVELS, RESOURCES


def all_topics():
    return [t for s in STAGES for t in s["topics"]]


def test_stages_go_from_basics_to_advanced():
    order = [STAGE_LEVELS.index(s["level"]) for s in STAGES]
    assert order == sorted(order)
    assert set(order) == {0, 1, 2}
    for s in STAGES:
        assert s["why"] and s["outcome"] and s["weeks"] > 0 and len(s["key_number"]) == 2


def test_topics_are_complete():
    for s in STAGES:
        assert len(s["topics"]) >= 3, s["title"]
        for t in s["topics"]:
            for field in ("gist", "purpose", "plain", "example", "metric"):
                assert t[field].strip(), (t["title"], field)
            assert len(t["insights"]) == 3, t["title"]
            assert len(t["experiments"]) >= 2, t["title"]
            assert len(t["actions"]) == 3, t["title"]
            assert len(t["quiz"]) >= 3, t["title"]


def test_topics_mix_reading_and_listening_resources():
    for t in all_topics():
        kinds = {RESOURCES[k]["kind"] for k in t["resources"]}
        assert kinds & {"book", "course", "cert"}, t["title"]
        assert len(set(t["resources"])) == len(t["resources"]), t["title"]


def test_references_resolve_and_everything_is_used():
    used = {k for t in all_topics() for k in t["resources"]}
    assert used <= set(RESOURCES)
    assert used == set(RESOURCES), set(RESOURCES) - used
    assert set(FAST_TRACK) <= set(RESOURCES) and len(FAST_TRACK) == 10


def test_quiz_questions_are_well_formed():
    questions = [item for t in all_topics() for item in t["quiz"]]
    assert len({item["q"] for item in questions}) == len(questions)
    for item in questions:
        assert 3 <= len(item["options"]) <= 4, item["q"]
        assert len(set(item["options"])) == len(item["options"]), item["q"]
        assert 0 <= item["answer"] < len(item["options"]), item["q"]
        assert item["why"].strip(), item["q"]


def test_shown_answer_positions_are_spread_out():
    positions = Counter(shuffled_options(item)[1] for t in all_topics() for item in t["quiz"])
    assert max(positions.values()) < 0.5 * sum(positions.values())


def test_resources_are_complete_and_linked():
    for r in RESOURCES.values():
        assert r["kind"] in KINDS and r["level"] in LEVELS, r["title"]
        assert r["gist"] and r["try"] and len(r["ideas"]) == 3, r["title"]
        assert r["link"].startswith(("https://", "http://")), r["title"]
        if r["kind"] == "book":
            assert r["link"].startswith("https://openlibrary.org/search?q=")
            assert r["year"] and r["hours"]
        if r["kind"] == "youtube":
            assert r["link"].startswith("https://www.youtube.com/results?search_query=")
        if r["kind"] in ("course", "cert"):
            assert r["hours"], r["title"]


def test_titles_and_glossary_are_unique():
    titles = [t["title"] for t in all_topics()]
    assert len(titles) == len(set(titles))
    terms = [term for term, _ in GLOSSARY]
    assert len(terms) == len(set(terms)) and len(terms) >= 30
    assert all(len(row) == 4 for row in SKILL_LADDER)


def test_every_stage_has_practice_layer():
    titles = {s["title"] for s in STAGES}
    assert set(PRACTICE) == titles and set(LABS) == titles
    for s in STAGES:
        p = PRACTICE[s["title"]]
        assert len(p["kpis"]) >= 3 and all(len(k) == 3 for k in p["kpis"]), s["title"]
        assert len(p["mistakes"]) >= 5 and all(len(m) == 3 for m in p["mistakes"]), s["title"]
        pr = p["project"]
        assert pr["title"] and pr["goal"] and pr["stack"] and pr["your_turn"], s["title"]
        assert len(pr["steps"]) >= 5 and len(pr["your_steps"]) >= 3 and pr["results"], s["title"]


def test_every_concept_has_tips():
    assert set(TIPS) == {t["title"] for t in all_topics()}
    assert all(len(v) >= 2 for v in TIPS.values())
