# 🤖 AI/ML TPM Learning Hub

One place to learn AI and machine learning as a technical program manager, from beginner to senior technical AI/ML TPM. It follows the layout of [books-summarizer](https://github.com/chennab12/books-summarizer): a sidebar menu, one page per stage, previous/next buttons, a master cheatsheet, a learning plan and calculators.

## Pages

- 🏠 **Start here**: totals, a 30-minutes-a-day routine, the 10 stages grouped by level, and a ten-item fast track.
- 🗺️ **Roadmap & skill ladder**: stage dates for your weekly hours, and a beginner-to-senior self-assessment that names your two biggest gaps.
- 📌 **Master cheatsheet**: one row per concept, key numbers, a 32-term glossary and every resource in one line, with CSV downloads.
- **10 stages, 30 core concepts**, ordered basics → intermediate → advanced:
  - 🟢 AI & ML foundations · Measuring models
  - 🟡 Classic ML algorithms · Deep learning · Generative AI & LLMs
  - 🔴 Building LLM products · MLOps & AI infrastructure · Responsible AI & governance · AI program management · Senior AI TPM career

  Every concept has a gist, why it matters for a TPM, a plain-words explanation, an example, three insights, two experiments to try, three timed next steps, a metric to track, the best resources and a three-question quick check.
- 📚 **Resource library**: 75 resources (24 books, 20 courses, 10 certifications, 10 podcasts, 11 YouTube channels) with filters by type, level, stage, cost and keyword. Each has a gist, three insights and one thing to try.
- 🏅 **Certification guide**: exam fees, prep hours, a fee chart and a suggested order for an AI/ML TPM.
- 📝 **Quiz center**: 90 multiple-choice questions with explanations, filtered by stage, scored with a review list.
- 🗓️ **My learning plan**: pick books, courses and certifications and set weekly hours to get finish dates; download as CSV.
- 🧮 **Calculators**: precision & recall, LLM cost, tokens & context, GPU memory, A/B test sample size, AI project ROI, agent reliability, study time.

## About the content

"Top 20%" is a curated editorial judgement, not a measured ranking: picks were chosen because practitioners widely recommend them, they stay useful, and they give a TPM the most understanding per hour. All summaries and quiz questions are original text, not quotes. Book links search [Open Library](https://openlibrary.org); course, certification and podcast links go to official pages or a search; YouTube links search for the channel. **Certification fees, exam codes and course availability change often**, so check the official page before paying. Calculators are back-of-envelope illustrations, not vendor quotes.

Content lives in `content.py` (stages, concepts, quizzes, glossary, skill ladder) and `resources.py` (catalog). The math is in `calculations.py`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pip install pytest && python -m pytest -q`. GitHub Actions runs them on every push. For Streamlit Community Cloud, deploy this repository with `app.py` as the entry point.
