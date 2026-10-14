"""AI/ML TPM Learning Hub: the highest-ROI AI/ML learning path for a TPM growing from beginner to senior."""
import csv
import io
import json
import random
import re
from datetime import date, timedelta
from functools import partial

import streamlit as st

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
from content import FAST_TRACK, GLOSSARY, REVIEWED, SKILL_LADDER, STAGE_LEVELS, STAGES, TOP_20_NOTE
from lab_pages import LABS, lab_schedule
from practice import PRACTICE, TIPS
from resources import KINDS, LEVELS, RESOURCES
from visuals import show

st.set_page_config(page_title="AI/ML TPM Learning Hub", page_icon="🤖", layout="wide")
# Bars keep the order of the data (Streamlit sorts category labels alphabetically by default).
bar_chart = partial(st.bar_chart, sort=False)

HOME = "🏠 Start here"
ROADMAP = "🗺️ Roadmap & skill ladder"
CHEATSHEET = "📌 Master cheatsheet"
STAGE_NAMES = [s["name"] for s in STAGES]
LIBRARY = "📚 Resource library"
CERTS = "🏅 Certification guide"
QUIZ = "📝 Quiz center"
PLAN = "🗓️ My learning plan"
CALCULATORS = "🧮 Calculators"
SEARCH = "🔎 Search everything"
ABOUT = "ℹ️ About & method"
SECTIONS = [HOME, ROADMAP, CHEATSHEET] + STAGE_NAMES + [LIBRARY, CERTS, QUIZ, PLAN, CALCULATORS, SEARCH, ABOUT]
SLUGS = {name: re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") for name in SECTIONS}
BY_SLUG = {slug: name for name, slug in SLUGS.items()}
CALCS = [
    "🎯 Precision & recall",
    "💸 LLM cost",
    "🔢 Tokens & context",
    "🖥️ GPU memory",
    "🧪 A/B sample size",
    "📈 AI project ROI",
    "🦾 Agent reliability",
    "⏱️ Study time",
    "🎲 Schedule risk (P50/P80)",
    "👥 Human review load",
]
TOPICS = [(s, t) for s in STAGES for t in s["topics"]]
QUESTIONS = [{**item, "stage": s["name"], "level": s["level"], "topic": t["title"]} for s, t in TOPICS for item in t["quiz"]]
PLANNABLE = [k for k, r in RESOURCES.items() if r["hours"]]
RESOURCE_STAGES = {k: [s["name"] for s in STAGES if any(k in t["resources"] for t in s["topics"])] for k in RESOURCES}
LEVEL_BADGE = {"🟢 Basics": "🟢", "🟡 Intermediate": "🟡", "🔴 Advanced": "🔴"}
HOURS_PER_STAGE_WEEK = 5  # suggested stage durations assume about 5 study hours a week

if "section" not in st.session_state:
    # Deep links: ?page=generative-ai-llms opens that section directly.
    st.session_state.section = BY_SLUG.get(st.query_params.get("page", ""), HOME)
st.session_state.setdefault("done", set())
st.session_state.setdefault("finished", set())
st.session_state.setdefault("plan", [])
st.session_state.setdefault("quiz_seed", 0)
st.session_state.setdefault("quiz_history", [])
st.session_state.setdefault("quiz_stages", [])
st.session_state.setdefault("missed", set())
st.session_state.setdefault("quiz_stats", {})


def go_to(section):
    st.session_state.section = section


def go_quiz(stage_name):
    st.session_state.quiz_stages = [stage_name]
    st.session_state.quiz_seed += 1
    st.session_state.section = QUIZ


def add_to_plan(keys):
    for key in keys:
        if key in PLANNABLE and key not in st.session_state.plan:
            st.session_state.plan.append(key)


def toggle(store, item, widget_key):
    if st.session_state[widget_key]:
        st.session_state[store].add(item)
    else:
        st.session_state[store].discard(item)


def new_quiz():
    st.session_state.quiz_seed += 1


def to_csv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def progress_json():
    return json.dumps({
        "done": sorted(st.session_state.done), "finished": sorted(st.session_state.finished), "plan": st.session_state.plan,
        "quiz_history": st.session_state.quiz_history, "missed": sorted(st.session_state.missed), "quiz_stats": st.session_state.quiz_stats,
    }, indent=1)


def load_progress():
    upload = st.session_state.get("progress_upload")
    if upload is None:
        return
    try:
        data = json.loads(upload.getvalue())
    except (ValueError, UnicodeDecodeError):
        st.session_state.load_error = True
        return
    titles = {t["title"] for _, t in TOPICS}
    questions = {q["q"] for q in QUESTIONS}
    st.session_state.done = {t for t in data.get("done", []) if t in titles}
    st.session_state.finished = {k for k in data.get("finished", []) if k in RESOURCES}
    st.session_state.plan = [k for k in data.get("plan", []) if k in PLANNABLE]
    st.session_state.quiz_history = [tuple(x) for x in data.get("quiz_history", []) if len(x) == 2]
    st.session_state.missed = {q for q in data.get("missed", []) if q in questions}
    st.session_state.quiz_stats = {k: v for k, v in data.get("quiz_stats", {}).items() if k in STAGE_NAMES}
    st.session_state.load_error = False


def next_concept():
    """First concept, in path order, not yet marked as mastered."""
    return next(((s, t) for s, t in TOPICS if t["title"] not in st.session_state.done), None)


def pct(x):
    return "n/a" if x is None else f"{x:.1%}"


def progress():
    done, finished = len(st.session_state.done), len(st.session_state.finished)
    st.progress(done / len(TOPICS), text=f"✅ {done} of {len(TOPICS)} concepts mastered")
    st.progress(finished / len(RESOURCES), text=f"📚 {finished} of {len(RESOURCES)} resources finished")
    history = st.session_state.quiz_history
    if history:
        best = max(score / total for score, total in history)
        st.progress(best, text=f"📝 Best quiz score {best:.0%} ({len(history)} attempts)")


def link_cfg(name="Open"):
    return {name: st.column_config.LinkColumn(name, display_text="Open ↗")}


def resource_meta(r):
    bits = [KINDS[r["kind"]].split()[0], r["by"], r["level"]]
    if r["year"]:
        bits.append(str(r["year"]))
    if r["hours"]:
        bits.append(f"≈ {r['hours']} h")
    if r["minutes"]:
        bits.append(f"≈ {r['minutes']} min")
    bits.append(r["cost"])
    return " · ".join(bits)


def resource_card(r, context):
    with st.container(border=True):
        badge = " ✅" if r["key"] in st.session_state.finished else ""
        st.markdown(f"**[{r['title']}]({r['link']})**{badge}  \n{resource_meta(r)}")
        st.markdown(f"🎯 {r['gist']}")
        st.markdown("\n".join(f"- 💡 {idea}" for idea in r["ideas"]))
        st.markdown(f"👉 **Try this:** {r['try']}")
        a, b = st.columns(2)
        if r["key"] in PLANNABLE:
            in_plan = r["key"] in st.session_state.plan
            a.button("📌 In your plan" if in_plan else "➕ Add to my plan", key=f"add_{context}_{r['key']}", on_click=add_to_plan,
                     args=([r["key"]],), disabled=in_plan, width="stretch")
        widget = f"fin_{context}_{r['key']}"
        b.checkbox("Finished ✅", value=r["key"] in st.session_state.finished, key=widget, on_change=toggle, args=("finished", r["key"], widget))


# Only the selected section runs on each rerun, so the app stays fast.
with st.sidebar:
    st.title("🤖 AI/ML TPM Hub")
    st.radio("Section", SECTIONS, key="section")
    sidebar_progress = st.empty()
    with st.expander("💾 Save or restore progress"):
        st.caption("Progress lives in this browser session only. Download it, then upload it next time to pick up where you left off.")
        st.download_button("⬇️ Download my progress", progress_json(), file_name="ai-ml-tpm-progress.json", mime="application/json")
        st.file_uploader("Restore from a progress file", type="json", key="progress_upload", on_change=load_progress)
        if st.session_state.get("load_error"):
            st.error("That file couldn't be read. Upload a progress file downloaded from this app.")

st.query_params["page"] = SLUGS[st.session_state.section]

st.title("🤖 AI/ML TPM Learning Hub")
st.caption(f"From beginner AI/ML TPM to senior technical AI/ML TPM · {len(STAGES)} stages · {len(TOPICS)} core concepts · reviewed {REVIEWED}")
section = st.session_state.section


def render_home():
    st.header("🏠 One place to learn AI/ML, fast and for the long run")
    a, b, c, d, e = st.columns(5)
    a.metric("Stages", len(STAGES), help="Basics → Intermediate → Advanced")
    b.metric("Core concepts", len(TOPICS))
    c.metric("Quiz questions", len(QUESTIONS))
    d.metric("Curated resources", len(RESOURCES))
    e.metric("Suggested path", f"≈ {sum(s['weeks'] for s in STAGES)} weeks", help=f"At about {HOURS_PER_STAGE_WEEK} hours a week")
    st.info("⭐ " + TOP_20_NOTE)
    st.subheader("🚦 How to use it in 30 minutes a day")
    show("30 minutes a day", ["Open the next concept", "Read gist & plain words", "Run one experiment", "Take the quick check", "Learn from one resource", "Track one metric"])
    progress()
    nxt = next_concept()
    if nxt:
        s, t = nxt
        st.button(f"▶️ Continue where you left off: {s['icon']} {s['title']} → {t['icon']} {t['title']}", on_click=go_to, args=(s["name"],), type="primary")
    else:
        st.success("🏆 You've mastered all 30 concepts. Keep sharp with the Quiz center and your portfolio.")
    st.dataframe(
        [{"Level": s["level"], "Stage": s["name"], "Mastered": sum(t["title"] in st.session_state.done for t in s["topics"]) / len(s["topics"]),
          "Quiz accuracy": (lambda c: c[0] / c[1] if c else None)(st.session_state.quiz_stats.get(s["name"]))} for s in STAGES],
        hide_index=True, width="stretch",
        column_config={"Mastered": st.column_config.ProgressColumn("Concepts mastered", format="percent", min_value=0, max_value=1),
                       "Quiz accuracy": st.column_config.ProgressColumn("Quiz accuracy", format="percent", min_value=0, max_value=1)},
    )

    st.subheader("🧗 The path: basics → intermediate → advanced")
    cols = st.columns(3)
    for col, level in zip(cols, STAGE_LEVELS):
        with col:
            st.markdown(f"### {level}")
            for s in [s for s in STAGES if s["level"] == level]:
                with st.container(border=True):
                    done = sum(1 for t in s["topics"] if t["title"] in st.session_state.done)
                    st.markdown(f"**{s['name']}** · ≈ {s['weeks']} weeks · ✅ {done}/{len(s['topics'])}")
                    value, label = s["key_number"]
                    st.caption(f"🔢 {value}: {label}")
                    st.button("Open →", key="open_" + s["name"], on_click=go_to, args=(s["name"],), width="stretch")

    st.subheader("⚡ Fast track: the ten resources with the highest return for a TPM")
    rows = [{"#": i, "Resource": RESOURCES[k]["title"], "Type": KINDS[RESOURCES[k]["kind"]], "Level": RESOURCES[k]["level"],
             "Why": RESOURCES[k]["gist"], "Cost": RESOURCES[k]["cost"], "Open": RESOURCES[k]["link"]} for i, k in enumerate(FAST_TRACK, 1)]
    st.dataframe(rows, hide_index=True, width="stretch", column_config=link_cfg())
    hours = sum(RESOURCES[k]["hours"] or 1 for k in FAST_TRACK)
    st.caption(f"≈ {hours} hours in total: about {hours / 5:.0f} weeks at 5 hours a week.")
    st.button("➕ Add the fast track to my learning plan", on_click=add_to_plan, args=(FAST_TRACK,), type="primary")


def render_roadmap():
    st.header("🗺️ Roadmap & skill ladder")
    hours = st.slider("Hours per week you can study", 1, 20, HOURS_PER_STAGE_WEEK)
    start = st.date_input("Start date", value=date.today(), key="roadmap_start")
    rows, day = [], start
    for i, s in enumerate(STAGES, 1):
        weeks = s["weeks"] * HOURS_PER_STAGE_WEEK / hours
        finish = day + timedelta(days=max(1, round(weeks * 7)) - 1)
        rows.append({"#": i, "Level": s["level"], "Stage": s["name"], "Weeks ≈": round(weeks, 1), "Start": day, "Finish": finish, "You will be able to": s["outcome"]})
        day = finish + timedelta(days=1)
    a, b, c = st.columns(3)
    a.metric("Total weeks", f"{sum(r['Weeks ≈'] for r in rows):.0f}")
    b.metric("Total study hours", f"≈ {sum(s['weeks'] for s in STAGES) * HOURS_PER_STAGE_WEEK}")
    c.metric("Path finishes", rows[-1]["Finish"].strftime("%b %d, %Y"))
    st.dataframe(rows, hide_index=True, width="stretch")
    bar_chart({"Stage": [r["Stage"] for r in rows], "Weeks": [r["Weeks ≈"] for r in rows]}, x="Stage", y="Weeks", horizontal=True)
    st.download_button("⬇️ Download my roadmap (CSV)", to_csv(rows), file_name="ai-ml-tpm-roadmap.csv", mime="text/csv")

    st.subheader("🪜 Beginner → senior technical AI/ML TPM")
    st.caption("Rate yourself 1 (beginner) to 5 (senior) on each skill. Re-rate every quarter and aim learning at the lowest two.")
    scores = []
    for i, (skill, beginner, senior, proof) in enumerate(SKILL_LADDER):
        with st.container(border=True):
            left, right = st.columns([3, 1])
            left.markdown(f"**{skill}**  \n🌱 **Beginner:** {beginner}  \n🏆 **Senior:** {senior}  \n🧾 **Proof:** {proof}")
            scores.append(right.slider("My level", 1, 5, 2, key=f"ladder_{i}"))
    avg = sum(scores) / len(scores)
    st.metric("Average skill level", f"{avg:.1f} / 5", delta=f"{avg - 5:.1f} to senior")
    bar_chart({"Skill": [s[0] for s in SKILL_LADDER], "My level": scores}, x="Skill", y="My level")
    gaps = sorted(zip(scores, [s[0] for s in SKILL_LADDER]))[:2]
    st.success("🎯 **Focus next on:** " + " and ".join(name for _, name in gaps))


def render_cheatsheet():
    st.header("📌 Master cheatsheet")
    st.caption("One row per core concept: the idea, plain words, an experiment, the first step, the number to track and the best resource. Scroll sideways for all columns.")
    rows = [
        {
            "Level": s["level"],
            "Stage": s["name"],
            "Concept": f"{t['icon']} {t['title']}",
            "Gist 🎯": t["gist"],
            "In plain words 🗣️": t["plain"],
            "Intuition tip 🧠": TIPS[t["title"]][0],
            "Experiment 🧪": t["experiments"][0][1],
            "Do first ✅": f"{t['actions'][0][0]}: {t['actions'][0][1]}",
            "Track 📏": t["metric"],
            "Best resource 📚": RESOURCES[t["resources"][0]]["title"],
        }
        for s, t in TOPICS
    ]
    st.dataframe(rows, hide_index=True, width="stretch", height=520)
    st.download_button("⬇️ Download concepts cheatsheet (CSV)", to_csv(rows), file_name="ai-ml-tpm-concepts.csv", mime="text/csv")

    st.subheader("🔢 Key numbers")
    st.dataframe([{"Stage": s["name"], "Number": s["key_number"][0], "Meaning": s["key_number"][1]} for s in STAGES], hide_index=True, width="stretch")

    st.subheader("📊 KPI library")
    kpis = [{"Stage": s["name"], "KPI": k, "How to calculate": f, "Good sign": g} for s in STAGES for k, f, g in PRACTICE[s["title"]]["kpis"]]
    st.dataframe(kpis, hide_index=True, width="stretch")
    st.download_button("⬇️ Download KPI library (CSV)", to_csv(kpis), file_name="ai-ml-tpm-kpis.csv", mime="text/csv")

    st.subheader("🛠️ Practice projects")
    st.dataframe([{"Stage": s["name"], "Worked project": PRACTICE[s["title"]]["project"]["title"], "Lab": LABS[s["title"]][0],
                   "Your turn": PRACTICE[s["title"]]["project"]["your_turn"]} for s in STAGES], hide_index=True, width="stretch")

    st.subheader("⚠️ Common mistakes, all stages")
    mistakes = [{"Stage": s["name"], "Mistake": m, "Why it hurts": w, "Fix": f} for s in STAGES for m, w, f in PRACTICE[s["title"]]["mistakes"]]
    st.dataframe(mistakes, hide_index=True, width="stretch", height=400)
    st.download_button("⬇️ Download mistakes checklist (CSV)", to_csv(mistakes), file_name="ai-ml-tpm-mistakes.csv", mime="text/csv")

    st.subheader("🔤 Glossary")
    term = st.text_input("Filter terms", placeholder="e.g. RAG, drift, token")
    glossary = [{"Term": t, "Meaning": m} for t, m in GLOSSARY if term.lower() in (t + m).lower()]
    st.dataframe(glossary, hide_index=True, width="stretch")

    st.subheader("📚 Every resource in one line")
    res = [{"Type": KINDS[r["kind"]], "Resource": r["title"], "By": r["by"], "Level": r["level"], "Gist": r["gist"], "Try this": r["try"], "Cost": r["cost"], "Open": r["link"]}
           for r in RESOURCES.values()]
    st.dataframe(res, hide_index=True, width="stretch", height=420, column_config=link_cfg())
    st.download_button("⬇️ Download resources cheatsheet (CSV)", to_csv(res), file_name="ai-ml-tpm-resources.csv", mime="text/csv")


def render_quick_check(s, t):
    st.markdown("#### 📝 Quick check")
    for i, item in enumerate(t["quiz"]):
        options, answer = shuffled_options(item)
        pick = st.radio(f"**Q{i + 1}.** {item['q']}", options, index=None, key=f"tq_{t['title']}_{i}")
        if pick is not None:
            if pick == options[answer]:
                st.success(f"✅ Correct. {item['why']}")
            else:
                st.error(f"❌ Not quite. The answer is **{options[answer]}**. {item['why']}")
    st.button(f"📝 Take the full {s['title']} quiz →", key=f"quiz_{t['title']}", on_click=go_quiz, args=(s["name"],))


def render_topic(s, t):
    st.success(f"🎯 **Gist:** {t['gist']}")
    left, right = st.columns(2)
    left.markdown(f"🧭 **Why it matters for a TPM:** {t['purpose']}")
    right.markdown(f"🗣️ **In plain words:** {t['plain']}")
    st.info(f"💡 **Example:** {t['example']}")
    st.markdown("#### 🔑 Key insights")
    st.markdown("\n".join(f"{n}. {x}" for n, x in enumerate(t["insights"], 1)))
    st.markdown("#### 🧠 Intuition tips")
    st.markdown("\n".join(f"- 💡 {tip}" for tip in TIPS[t["title"]]))
    st.markdown("#### 🧪 Experiments to try")
    cols = st.columns(len(t["experiments"]))
    for col, (name, how) in zip(cols, t["experiments"]):
        with col.container(border=True):
            st.markdown(f"**{name}**  \n{how}")
    st.markdown("#### ✅ Next steps for fast, sustainable growth")
    st.dataframe([{"When": w, "Action": a} for w, a in t["actions"]], hide_index=True, width="stretch")
    st.markdown(f"📏 **Track this:** {t['metric']}")
    st.markdown("#### 📚 Best resources for this concept")
    cols = st.columns(2)
    for i, key in enumerate(t["resources"]):
        with cols[i % 2]:
            resource_card(RESOURCES[key], t["title"])
    render_quick_check(s, t)
    widget = "done_" + t["title"]
    st.toggle("I've mastered this concept", value=t["title"] in st.session_state.done, key=widget, on_change=toggle, args=("done", t["title"], widget))


def render_stage(index):
    s = STAGES[index]
    st.header(f"{s['name']} · {s['level']}")
    st.caption(s["why"])
    st.markdown(f"🏁 **After this stage you can:** {s['outcome']}")
    keys = {k for t in s["topics"] for k in t["resources"]}
    a, b, c, d = st.columns(4)
    a.metric("Key number", s["key_number"][0], help=s["key_number"][1])
    b.metric("Concepts", len(s["topics"]))
    c.metric("Resources", len(keys))
    d.metric("Suggested time", f"≈ {s['weeks']} weeks", help=f"At about {HOURS_PER_STAGE_WEEK} hours a week")
    st.caption(f"🔢 {s['key_number'][0]}: {s['key_number'][1]}")
    tabs = st.tabs([f"{t['icon']} {t['title']}" + (" ✅" if t["title"] in st.session_state.done else "") for t in s["topics"]])
    for tab, t in zip(tabs, s["topics"]):
        with tab:
            render_topic(s, t)
    show(s["title"], [t["title"] for t in s["topics"]])
    render_practice(s)
    prev_col, next_col = st.columns(2)
    if index > 0:
        prev_col.button("← Previous stage", on_click=go_to, args=(STAGE_NAMES[index - 1],), width="stretch")
    if index + 1 < len(STAGES):
        next_col.button("Next stage →", on_click=go_to, args=(STAGE_NAMES[index + 1],), type="primary", width="stretch")
    else:
        next_col.button("Build my learning plan →", on_click=go_to, args=(PLAN,), type="primary", width="stretch")


def render_practice(s):
    """Bottom of every stage: KPIs, an interactive lab, a worked project, a 'your turn' project and common mistakes."""
    p = PRACTICE[s["title"]]
    st.divider()
    st.subheader("📊 KPIs to track at this stage")
    st.dataframe([{"KPI": k, "How to calculate": f, "Good sign": g} for k, f, g in p["kpis"]], hide_index=True, width="stretch")

    lab_title, lab = LABS[s["title"]]
    st.subheader(f"🔬 Interactive lab: {lab_title}")
    with st.container(border=True):
        lab()

    pr = p["project"]
    st.subheader(f"🛠️ Worked project: {pr['title']}")
    st.markdown(f"🎯 **Goal:** {pr['goal']}  \n🧰 **Typical stack:** {pr['stack']}")
    st.dataframe([{"Step": f"{i}. {name}", "What was done": how} for i, (name, how) in enumerate(pr["steps"], 1)], hide_index=True, width="stretch")
    cols = st.columns(len(pr["results"]))
    for col, (label, value) in zip(cols, pr["results"]):
        col.metric(label, value)
    st.caption("A typical implementation written as a teaching example; numbers are illustrative, not from a specific company.")
    with st.container(border=True):
        st.markdown(f"🔁 **Your turn: {pr['your_turn']}**")
        st.markdown("\n".join(f"{i}. {step}" for i, step in enumerate(pr["your_steps"], 1)))

    st.subheader("⚠️ Most common mistakes and how to fix them")
    st.dataframe([{"Mistake": m, "Why it hurts": w, "How to fix or manage it": f} for m, w, f in p["mistakes"]], hide_index=True, width="stretch")


def render_library():
    st.header("📚 Resource library")
    st.caption("Books link to Open Library search so you can find any edition or a library copy. Courses, certifications and podcasts link to official pages "
               "where known, otherwise to a search. YouTube links search the channel. Check prices and availability on the official page.")
    kind = st.segmented_control("Type", ["All"] + list(KINDS.values()), default="All")
    a, b, c = st.columns([2, 2, 2])
    levels = a.multiselect("Level", LEVELS, placeholder="All levels")
    stages = b.multiselect("Stage", STAGE_NAMES, placeholder="All stages")
    query = c.text_input("Search", placeholder="e.g. RAG, evals, Karpathy")
    free = st.toggle("Free only")
    q = query.lower().strip()
    picks = [
        r for r in RESOURCES.values()
        if (kind in (None, "All") or KINDS[r["kind"]] == kind)
        and (not levels or r["level"] in levels)
        and (not stages or set(stages) & set(RESOURCE_STAGES[r["key"]]))
        and (not free or r["cost"].lower().startswith(("free", "mostly free")))
        and (not q or q in " ".join([r["title"], r["by"], r["gist"], *r["ideas"]]).lower())
    ]
    picks.sort(key=lambda r: (LEVELS.index(r["level"]), list(KINDS).index(r["kind"]), r["title"]))
    x, y = st.columns(2)
    x.metric("Matching resources", len(picks))
    y.metric("Study hours (books, courses, certs)", f"≈ {sum(r['hours'] or 0 for r in picks)}")
    if not picks:
        st.info("Nothing matches. Clear a filter.")
        return
    st.button(f"➕ Add the {sum(1 for r in picks if r['key'] in PLANNABLE)} plannable matches to my plan", on_click=add_to_plan, args=([r["key"] for r in picks],))
    cols = st.columns(2)
    for i, r in enumerate(picks):
        with cols[i % 2]:
            st.caption(", ".join(RESOURCE_STAGES[r["key"]]))
            resource_card(r, "library")


def render_certs():
    st.header("🏅 Certification guide")
    st.warning("💲 Exam fees are approximate US list prices when this app was reviewed. Vendors change prices, exam codes and retire exams often, so confirm on the official page before booking.")
    certs = sorted((r for r in RESOURCES.values() if r["kind"] == "cert"), key=lambda r: (LEVELS.index(r["level"]), r["cost_usd"] or 0))
    rows = [{"Level": r["level"], "Certification": r["title"], "Issuer": r["by"], "Exam fee": r["cost"], "Prep ≈ h": r["hours"], "What it proves": r["gist"], "Official page": r["link"]} for r in certs]
    st.dataframe(rows, hide_index=True, width="stretch", column_config=link_cfg("Official page"))
    priced = [r for r in certs if r["cost_usd"]]
    bar_chart({"Certification": [r["title"].split(" (")[0] for r in priced], "Exam fee ≈ USD": [r["cost_usd"] for r in priced]}, x="Certification", y="Exam fee ≈ USD", horizontal=True)
    st.subheader("🧭 A suggested order for an AI/ML TPM")
    path = ["x_gcpgenai", "x_awsaip", "x_cpmai", "x_awsmle", "x_aigp"]
    show("Certification path", [RESOURCES[k]["title"].split(" (")[0] for k in path])
    st.markdown(
        "1. 🟢 **Start with one foundational exam** (Google Cloud Generative AI Leader or AWS Certified AI Practitioner) to prove AI literacy.\n"
        "2. 🟡 **Add PMI-CPMAI** to show you can run AI projects with a proven method.\n"
        "3. 🟡 **Pick one associate technical exam on your company's cloud** (AWS ML Engineer, Azure AI Engineer or NVIDIA GenAI LLMs).\n"
        "4. 🔴 **Specialize**: Google Cloud Professional ML Engineer for depth, or IAPP AIGP for governance-heavy programs.\n\n"
        "Certifications open doors, but shipped programs and a portfolio get you promoted. Pair each exam with one real project."
    )
    a, b = st.columns(2)
    a.metric("Suggested path exam fees ≈", f"${sum(RESOURCES[k]['cost_usd'] or 0 for k in path):,} + CPMAI")
    b.metric("Suggested path prep ≈", f"{sum(RESOURCES[k]['hours'] for k in path)} h")
    st.subheader("📋 Details")
    cols = st.columns(2)
    for i, r in enumerate(certs):
        with cols[i % 2]:
            resource_card(r, "certs")


def render_quiz_stats():
    stats = st.session_state.quiz_stats
    if not stats:
        return
    st.subheader("📊 My accuracy by stage")
    names = [n for n in STAGE_NAMES if n in stats]
    bar_chart({"Stage": names, "Accuracy": [stats[n][0] / stats[n][1] for n in names]}, x="Stage", y="Accuracy", horizontal=True)
    weakest = min(names, key=lambda n: stats[n][0] / stats[n][1])
    st.caption(f"Weakest so far: **{weakest}**. Revisit its concepts, then retry your missed questions.")


def render_quiz():
    st.header("📝 Quiz center")
    st.caption("Pick stages, answer, then check. Each new set draws a fresh random mix. Questions you miss go to a review list so you can retry them (spaced practice).")
    missed = st.session_state.missed
    mode = st.segmented_control("Mode", ["🎲 New mix", f"🔁 My missed questions ({len(missed)})"], default="🎲 New mix", key="quiz_mode")
    review = bool(mode) and mode.startswith("🔁")
    a, b = st.columns([3, 1])
    stages = a.multiselect("Stages", STAGE_NAMES, key="quiz_stages", placeholder="All stages")
    count = b.slider("Questions", 5, 30, 10)
    pool = [item for item in QUESTIONS if (not stages or item["stage"] in stages) and (not review or item["q"] in missed)]
    if not pool:
        if review:
            st.success("🎉 No missed questions to review here. Take a new mix.")
        else:
            st.info("No questions match. Clear the stage filter.")
        render_quiz_stats()
        return
    rng = random.Random(st.session_state.quiz_seed)
    items = rng.sample(pool, min(count, len(pool)))
    st.button("🔀 New question set", on_click=new_quiz)
    seed = st.session_state.quiz_seed
    with st.form("quiz"):
        shown = []
        for i, item in enumerate(items):
            options, answer = shuffled_options(item)
            shown.append((options, answer))
            st.markdown(f"{LEVEL_BADGE[item['level']]} *{item['stage']} · {item['topic']}*")
            st.radio(f"**Q{i + 1}.** {item['q']}", options, index=None, key=f"quiz_{seed}_{i}")
        submitted = st.form_submit_button("✅ Check my answers", type="primary")
    if not submitted:
        render_quiz_stats()
        return
    picks = [st.session_state.get(f"quiz_{seed}_{i}") for i in range(len(items))]
    score = quiz_score(items, picks)
    st.session_state.quiz_history.append((score, len(items)))
    for item, pick, (options, answer) in zip(items, picks, shown):
        right = pick == options[answer]
        if right:
            missed.discard(item["q"])
        else:
            missed.add(item["q"])
        correct, total = st.session_state.quiz_stats.get(item["stage"], (0, 0))
        st.session_state.quiz_stats[item["stage"]] = (correct + right, total + 1)
    x, y, z, w = st.columns(4)
    x.metric("Score", f"{score} / {len(items)}")
    y.metric("Percent", f"{score / len(items):.0%}")
    z.metric("Unanswered", sum(1 for p in picks if p is None))
    w.metric("In review list", len(missed))
    if score / len(items) >= 0.8:
        st.success("🎉 Strong result. Move to the next stage, or try a harder set.")
    else:
        st.info("📖 Review the concepts you missed below, then retry them with 'My missed questions'.")
    for i, (item, pick, (options, answer)) in enumerate(zip(items, picks, shown), 1):
        mark = "✅" if pick == options[answer] else "❌"
        st.markdown(f"{mark} **Q{i}. {item['q']}**  \nAnswer: **{options[answer]}**. {item['why']}  \n_Review: {item['stage']} → {item['topic']}_")
    render_quiz_stats()


def render_plan():
    st.header("🗓️ My learning plan")
    st.caption("Pick books, courses and certifications, set your weekly hours, and get finish dates. Nothing is saved on the server: download your plan to keep it.")
    chosen = st.multiselect(
        "Resources in my plan (in study order)", PLANNABLE, default=st.session_state.plan,
        format_func=lambda k: f"{KINDS[RESOURCES[k]['kind']].split()[0]} {RESOURCES[k]['title']} (≈ {RESOURCES[k]['hours']} h)", placeholder="Add resources",
    )
    st.session_state.plan = chosen
    a, b = st.columns(2)
    hours = a.slider("Study hours per week", 1, 20, 5)
    start = b.date_input("Start date", value=date.today())
    if not chosen:
        st.info("Your plan is empty. Add resources here, from any concept, or the fast track.")
        st.button("➕ Add the fast track", on_click=add_to_plan, args=(FAST_TRACK,), type="primary")
        return
    rows = study_schedule([(RESOURCES[k]["title"], RESOURCES[k]["hours"]) for k in chosen], hours, start)
    total = sum(RESOURCES[k]["hours"] for k in chosen)
    done = sum(1 for k in chosen if k in st.session_state.finished)
    x, y, z, w = st.columns(4)
    x.metric("Resources", len(chosen))
    y.metric("Study time", f"≈ {total} h")
    z.metric("Plan finishes", rows[-1]["Finish"].strftime("%b %d, %Y"))
    w.metric("Finished", f"{done} of {len(chosen)}")
    for row, key in zip(rows, chosen):
        row["Type"] = KINDS[RESOURCES[key]["kind"]]
        row["Done ✅"] = "✅" if key in st.session_state.finished else ""
        row["Open"] = RESOURCES[key]["link"]
    st.dataframe(rows, hide_index=True, width="stretch", column_config=link_cfg())
    bar_chart({"Resource": [r["Resource"] for r in rows], "Hours ≈": [r["Hours (≈)"] for r in rows]}, x="Resource", y="Hours ≈", horizontal=True)
    st.download_button("⬇️ Download my plan (CSV)", to_csv(rows), file_name="my-ai-ml-learning-plan.csv", mime="text/csv", type="primary")


def calc_precision():
    st.caption("Enter a confusion matrix. Try a rare-event case to see why accuracy misleads.")
    a, b = st.columns(2)
    tp = a.number_input("✅ True positives (caught real cases)", 0, 1_000_000, 40)
    fp = b.number_input("⚠️ False positives (false alarms)", 0, 1_000_000, 10)
    fn = a.number_input("❌ False negatives (missed cases)", 0, 1_000_000, 20)
    tn = b.number_input("✅ True negatives (correctly ignored)", 0, 1_000_000, 930)
    m = classification_metrics(tp, fp, fn, tn)
    cols = st.columns(5)
    for col, (name, key) in zip(cols, [("Accuracy", "accuracy"), ("Precision", "precision"), ("Recall", "recall"), ("F1", "f1"), ("Specificity", "specificity")]):
        col.metric(name, pct(m[key]))
    bar_chart({"Metric": ["Accuracy", "Precision", "Recall", "F1"], "Value": [m[k] or 0 for k in ("accuracy", "precision", "recall", "f1")]}, x="Metric", y="Value")
    total = tp + fp + fn + tn
    if total and (tp + fn) / total < 0.05:
        st.warning(f"Only {(tp + fn) / total:.1%} of cases are positive. Always predicting 'no' would score {pct((fp + tn) / total)} accuracy, so judge by precision and recall.")
    a, b = st.columns(2)
    cost_fp = a.number_input("Cost of one false positive ($)", 0, 1_000_000, 5)
    cost_fn = b.number_input("Cost of one false negative ($)", 0, 1_000_000, 200)
    st.metric("Cost of errors at this threshold", f"${fp * cost_fp + fn * cost_fn:,}")


def calc_llm_cost():
    st.caption("Example prices only. Check your provider's pricing page; prices differ by model and change often.")
    a, b = st.columns(2)
    reqs = a.number_input("Requests per day", 1, 100_000_000, 10_000)
    tin = a.number_input("Input tokens per request (prompt + context)", 1, 2_000_000, 2_000)
    tout = a.number_input("Output tokens per request", 1, 200_000, 400)
    pin = b.number_input("Price per 1M input tokens ($)", 0.0, 1000.0, 3.0, 0.25)
    pout = b.number_input("Price per 1M output tokens ($)", 0.0, 1000.0, 15.0, 0.5)
    cached = b.slider("Share of input tokens served from the prompt cache (%)", 0, 100, 0)
    c = llm_cost(reqs, tin, tout, pin, pout, cached)
    x, y, z, w = st.columns(4)
    x.metric("Per 1,000 requests", f"${c['per_1k']:,.2f}")
    y.metric("Per day", f"${c['per_day']:,.0f}")
    z.metric("Per month", f"${c['per_month']:,.0f}")
    w.metric("Per year", f"${c['per_year']:,.0f}")
    growth = [1, 2, 5, 10]
    bar_chart({"Traffic": [f"{g:02}×" for g in growth], "Monthly cost ($)": [c["per_month"] * g for g in growth]}, x="Traffic", y="Monthly cost ($)")
    st.caption("Assumes cached input is billed at a 90% discount, a common level for prompt caching. Excludes hosting, engineering and eval costs.")


def calc_tokens():
    words = st.number_input("Words of text", 1, 10_000_000, 5_000)
    pages = st.number_input("…or pages (≈ 500 words each)", 0, 100_000, 0)
    total_words = words + pages * 500
    tokens = words_to_tokens(total_words)
    window = st.select_slider("Context window (tokens)", [8_000, 32_000, 128_000, 200_000, 1_000_000], 128_000)
    a, b, c = st.columns(3)
    a.metric("Estimated tokens", f"{tokens:,}")
    b.metric("Share of context window", f"{tokens / window:.0%}")
    c.metric("Words that fit in the window", f"≈ {tokens_to_words(window):,}")
    if tokens > window:
        st.error("Doesn't fit. Use retrieval (RAG) to send only the relevant parts, or summarize in chunks.")
    else:
        st.success("Fits. Long prompts still cost more and can be slower, so send only what's needed.")
    st.caption("Rule of thumb: about 0.75 English words per token. Code, numbers and other languages often use more tokens.")


def calc_gpu():
    a, b = st.columns(2)
    params = a.select_slider("Model size (billion parameters)", [1, 3, 7, 8, 13, 34, 70, 180, 405], 7)
    precision = b.selectbox("Precision", ["16-bit (2 bytes)", "8-bit (1 byte)", "4-bit (0.5 bytes)"])
    bytes_per = {"16-bit (2 bytes)": 2, "8-bit (1 byte)": 1, "4-bit (0.5 bytes)": 0.5}[precision]
    gpu = st.selectbox("GPU memory", [24, 48, 80, 141], index=2, format_func=lambda g: f"{g} GB")
    weights, total = model_memory_gb(params, bytes_per)
    train = training_memory_gb(params)
    x, y, z = st.columns(3)
    x.metric("Weights", f"{weights:,.1f} GB")
    y.metric("Inference ≈ (+20%)", f"{total:,.1f} GB", help="Rough allowance for activations and KV cache; long contexts need more")
    z.metric(f"GPUs of {gpu} GB to serve", gpus_needed(total, gpu))
    st.metric("Full fine-tuning ≈ (16 bytes/param)", f"{train:,.0f} GB · {gpus_needed(train, gpu)} GPUs")
    bar_chart({"Precision": ["16-bit", "8-bit", "4-bit"], "Weights GB": [params * 2, params * 1, params * 0.5]}, x="Precision", y="Weights GB")
    st.caption("Back-of-envelope only. Real needs depend on context length, batch size, framework and parallelism. Parameter-efficient fine-tuning needs far less memory.")


def calc_ab():
    a, b = st.columns(2)
    base = a.number_input("Baseline conversion rate (%)", 0.1, 99.0, 5.0, 0.1)
    mde = b.number_input("Smallest relative lift worth detecting (%)", 0.5, 200.0, 10.0, 0.5)
    alpha = a.select_slider("Significance level", [0.01, 0.05, 0.1], 0.05)
    power = b.select_slider("Power", [0.7, 0.8, 0.9], 0.8)
    traffic = st.number_input("Eligible users per day (both variants together)", 1, 100_000_000, 5_000)
    n = ab_sample_size(base, mde, alpha, power)
    if n is None:
        st.error("Check inputs: the improved rate must stay below 100%.")
        return
    x, y, z = st.columns(3)
    x.metric("Users per variant", f"{n:,}")
    y.metric("Total users", f"{2 * n:,}")
    z.metric("Days needed", f"{2 * n / traffic:,.1f}")
    lifts = [5, 10, 20, 30, 50]
    bar_chart({"Relative lift (%)": lifts, "Users per variant": [ab_sample_size(base, m, alpha, power) for m in lifts]}, x="Relative lift (%)", y="Users per variant")
    st.caption("Two-sided test of two proportions. Run for whole weeks to cover weekday patterns, and decide the duration before you start.")


def calc_roi():
    a, b = st.columns(2)
    volume = a.number_input("Items per year (tickets, documents, reviews)", 1, 100_000_000, 120_000)
    manual = a.number_input("Manual cost per item ($)", 0.0, 10_000.0, 4.0, 0.5)
    auto = a.slider("Share handled by AI (%)", 0, 100, 60)
    err = b.slider("AI error rate on handled items (%)", 0.0, 30.0, 3.0, 0.5)
    cost_err = b.number_input("Cost per AI error ($)", 0.0, 100_000.0, 25.0, 1.0)
    build = b.number_input("One-time build cost ($)", 0, 100_000_000, 250_000, 10_000)
    run = st.number_input("Yearly run cost (inference, hosting, monitoring, people) ($)", 0, 100_000_000, 60_000, 5_000)
    r = project_roi(volume, manual, auto, err, cost_err, build, run)
    x, y, z, w = st.columns(4)
    x.metric("Yearly savings", f"${r['savings']:,.0f}")
    y.metric("Yearly net benefit", f"${r['net']:,.0f}")
    z.metric("Payback", "Never" if r["payback_months"] is None else f"{r['payback_months']:.1f} months")
    w.metric("3-year ROI", pct(r["roi"]))
    years = list(range(4))
    st.line_chart({"Year": years, "Cumulative net ($)": [-build + r["net"] * y_ for y_ in years]}, x="Year", y="Cumulative net ($)")
    st.caption("A simple model to structure the business case. Replace guesses with measured pilot numbers before asking for budget.")


def calc_agent():
    step = st.slider("Success rate of each agent step (%)", 50.0, 99.9, 95.0, 0.1)
    steps = st.slider("Steps in the task", 1, 50, 10)
    p = compound_success(step, steps)
    a, b = st.columns(2)
    a.metric("Chance the whole task succeeds", f"{p:.1%}")
    b.metric("Failures per 1,000 tasks", f"{(1 - p) * 1000:,.0f}")
    xs = list(range(1, 51))
    st.line_chart({"Steps": xs, f"{step}% per step": [compound_success(step, n) for n in xs], "99% per step": [compound_success(99, n) for n in xs]}, x="Steps", y_label="Task success rate")
    st.caption("Assumes independent steps. Fewer steps, retries, verification and human checkpoints raise real-world success.")


def calc_study():
    hours = st.slider("Study hours per week", 1, 20, 5)
    total = sum(s["weeks"] for s in STAGES) * HOURS_PER_STAGE_WEEK
    weeks = weeks_to_finish(total, hours)
    a, b, c = st.columns(3)
    a.metric("Path hours ≈", total)
    b.metric("Weeks to finish", f"{weeks:.0f}")
    c.metric("Finish date", (date.today() + timedelta(weeks=weeks)).strftime("%b %Y"))
    options = [2, 3, 5, 8, 10, 15]
    bar_chart({"Hours per week": options, "Weeks": [weeks_to_finish(total, h) for h in options]}, x="Hours per week", y="Weeks")
    st.caption("Sustainable beats intense: 5 steady hours a week finishes the path in about half a year without burnout.")


def calc_review_load():
    st.caption("How many people are needed to review the AI's low-confidence or flagged cases (human in the loop).")
    a, b = st.columns(2)
    volume = a.number_input("Items per day", 1, 10_000_000, 5_000)
    share = a.slider("Share sent to human review (%)", 0.0, 100.0, 15.0, 0.5)
    minutes = b.number_input("Minutes per review", 0.1, 120.0, 2.0, 0.5)
    hours_per_person = b.number_input("Productive review hours per person per day", 1.0, 8.0, 6.0, 0.5)
    reviews, hours, people = review_load(volume, share, minutes, hours_per_person)
    x, y, z = st.columns(3)
    x.metric("Reviews per day", f"{reviews:,.0f}")
    y.metric("Review hours per day", f"{hours:,.1f}")
    z.metric("Reviewers needed", f"{people:,.1f}")
    shares = [5, 10, 15, 25, 40]
    bar_chart({"Share reviewed (%)": shares, "Reviewers needed": [review_load(volume, v, minutes, hours_per_person)[2] for v in shares]},
                 x="Share reviewed (%)", y="Reviewers needed")
    st.caption("Raising the model's confidence threshold cuts review load but lets more errors through: tune it with the threshold lab in Measuring models.")


CALC_FUNCS = dict(zip(CALCS, [calc_precision, calc_llm_cost, calc_tokens, calc_gpu, calc_ab, calc_roi, calc_agent, calc_study, lab_schedule, calc_review_load]))


def render_calculators():
    st.header("🧮 Calculators")
    st.caption("Numbers stay in your browser session and are not saved. Results are back-of-envelope illustrations.")
    tool = st.segmented_control("Choose a calculator", CALCS, default=CALCS[0])
    if tool is None:
        st.info("Pick a calculator above.")
    else:
        CALC_FUNCS[tool]()


def render_search():
    st.header("🔎 Search everything")
    query = st.text_input("Search concepts, tips, mistakes, glossary and resources", placeholder="e.g. drift, threshold, RAG, overfitting").strip().lower()
    if len(query) < 2:
        st.info("Type at least two letters.")
        return
    concepts = [(s, t) for s, t in TOPICS if query in " ".join([t["title"], t["gist"], t["plain"], t["example"], *t["insights"], *TIPS[t["title"]]]).lower()]
    mistakes = [(s, m) for s in STAGES for m in PRACTICE[s["title"]]["mistakes"] if query in " ".join(m).lower()]
    terms = [(t, m) for t, m in GLOSSARY if query in (t + " " + m).lower()]
    found = [r for r in RESOURCES.values() if query in " ".join([r["title"], r["by"], r["gist"], *r["ideas"]]).lower()]
    a, b, c, d = st.columns(4)
    a.metric("Concepts", len(concepts))
    b.metric("Mistakes", len(mistakes))
    c.metric("Glossary terms", len(terms))
    d.metric("Resources", len(found))
    for s, t in concepts:
        with st.container(border=True):
            st.markdown(f"**{t['icon']} {t['title']}** · {s['name']} · {s['level']}  \n🎯 {t['gist']}")
            st.button("Open stage →", key=f"search_{t['title']}", on_click=go_to, args=(s["name"],))
    if mistakes:
        st.subheader("⚠️ Mistakes")
        st.dataframe([{"Stage": s["name"], "Mistake": m, "Fix": f} for s, (m, _, f) in mistakes], hide_index=True, width="stretch")
    if terms:
        st.subheader("🔤 Glossary")
        st.dataframe([{"Term": t, "Meaning": m} for t, m in terms], hide_index=True, width="stretch")
    if found:
        st.subheader("📚 Resources")
        st.dataframe([{"Type": KINDS[r["kind"]], "Resource": r["title"], "Gist": r["gist"], "Open": r["link"]} for r in found],
                     hide_index=True, width="stretch", column_config=link_cfg())


def render_about():
    st.header("ℹ️ About & method")
    st.markdown(f"⭐ {TOP_20_NOTE}")
    st.markdown(
        "**How picks were chosen**\n"
        "- 🏛️ **Widely recommended:** frequently suggested by practitioners and educators, and still useful years later.\n"
        "- 🎯 **TPM fit:** builds the judgement a technical program manager needs, not research-level math.\n"
        "- ⏱️ **Return per hour:** short, high-signal resources first; deep references are marked Advanced.\n"
        "- 🧗 **Order:** stages go from basics to intermediate to advanced, and each concept builds on earlier ones.\n\n"
        "**About the summaries:** all gists, ideas, examples and quiz questions are original text written for this app. "
        "Read the book, take the course or watch the video for the creators' own words.\n\n"
        "**About the links:** books search Open Library so you can find any edition or a library copy. Courses and certifications "
        "link to official pages (or a search on the provider's site), and YouTube links search for the channel. If a page has moved, search its name.\n\n"
        "**About the numbers:** study hours and exam fees are rough estimates. Calculators are simplified illustrations, "
        "not vendor quotes or financial advice."
    )
    st.subheader("Catalog by stage")
    st.dataframe(
        [{"Level": s["level"], "Stage": s["name"], "Concepts": len(s["topics"]), "Quiz questions": sum(len(t["quiz"]) for t in s["topics"]),
          "Resources": len({k for t in s["topics"] for k in t["resources"]})} for s in STAGES],
        hide_index=True, width="stretch",
    )
    st.dataframe([{"Type": label, "Count": sum(1 for r in RESOURCES.values() if r["kind"] == kind)} for kind, label in KINDS.items()], hide_index=True)
    st.caption(f"Content reviewed {REVIEWED}. Suggestions welcome via the GitHub repository.")


if section == HOME:
    render_home()
elif section == ROADMAP:
    render_roadmap()
elif section == CHEATSHEET:
    render_cheatsheet()
elif section in STAGE_NAMES:
    render_stage(STAGE_NAMES.index(section))
elif section == LIBRARY:
    render_library()
elif section == CERTS:
    render_certs()
elif section == QUIZ:
    render_quiz()
elif section == PLAN:
    render_plan()
elif section == CALCULATORS:
    render_calculators()
elif section == SEARCH:
    render_search()
else:
    render_about()

with sidebar_progress.container():
    progress()
