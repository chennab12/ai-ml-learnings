"""Curated AI/ML learning resources: books, courses, certifications, podcasts and YouTube channels.

Every summary here is an original paraphrase written for this app, not text
copied from the source. "Top 20%" is a curated editorial judgement (see
README.md), not a measured ranking. Prices, exam codes and course availability
change often: always check the official page before you pay or plan.
"""
from urllib.parse import quote_plus

KINDS = {
    "book": "📖 Books",
    "course": "🎓 Courses",
    "cert": "🏅 Certifications",
    "podcast": "🎧 Podcasts",
    "youtube": "▶️ YouTube",
}
LEVELS = ["🟢 Beginner", "🟡 Intermediate", "🔴 Advanced"]
_LEVEL = {"B": LEVELS[0], "I": LEVELS[1], "A": LEVELS[2]}


def _openlibrary(title, author):
    first = author.split(" & ")[0].split(",")[0]
    return "https://openlibrary.org/search?q=" + quote_plus(f"{title} {first}")


def _podcast_search(name):
    return "https://podcasts.apple.com/us/search?term=" + quote_plus(name)


def _youtube_search(query):
    return "https://www.youtube.com/results?search_query=" + quote_plus(query)


def _make(kind, title, by, level, hours, cost, link, gist, ideas, try_, year=None, cost_usd=None, minutes=None):
    return {
        "kind": kind, "title": title, "by": by, "level": _LEVEL[level], "hours": hours, "cost": cost,
        "link": link, "gist": gist, "ideas": ideas, "try": try_, "year": year, "cost_usd": cost_usd, "minutes": minutes,
    }


def book(title, author, year, hours, level, gist, ideas, try_):
    return _make("book", title, author, level, hours, "Paid (library copies often free)", _openlibrary(title, author), gist, ideas, try_, year=year)


def course(title, provider, hours, level, cost, link, gist, ideas, try_):
    return _make("course", title, provider, level, hours, cost, link, gist, ideas, try_)


def cert(title, issuer, hours, level, cost_usd, link, gist, ideas, try_):
    cost = f"≈ ${cost_usd} exam" if cost_usd else "Varies (often bundled with training)"
    return _make("cert", title, issuer, level, hours, cost, link, gist, ideas, try_, cost_usd=cost_usd)


def podcast(name, host, level, minutes, link, gist, ideas, try_):
    return _make("podcast", name, host, level, None, "Free", link or _podcast_search(name), gist, ideas, try_, minutes=minutes)


def youtube(name, by, level, minutes, search, gist, ideas, try_):
    return _make("youtube", name, by, level, None, "Free", _youtube_search(search), gist, ideas, try_, minutes=minutes)


_RESOURCES = {
    # ───────────── 📖 Books ─────────────
    "b_prediction": book(
        "Prediction Machines", "Ajay Agrawal, Joshua Gans & Avi Goldfarb", 2018, 6, "B",
        "Three economists explain AI as a drop in the cost of prediction, and show how that changes decisions, jobs and strategy.",
        ["When prediction gets cheap, human judgement (deciding what an outcome is worth) becomes more valuable.",
         "Break a workflow into decisions, then ask which ones are really prediction problems.",
         "An 'AI canvas' (prediction, judgement, action, outcome, training data) makes use cases concrete."],
        "Pick one workflow on your team and list every decision in it; mark the ones that are a guess about the future."),
    "b_cointel": book(
        "Co-Intelligence", "Ethan Mollick", 2024, 5, "B",
        "A Wharton professor's practical guide to working alongside large language models as a coworker, tutor and creative partner.",
        ["Invite AI into every task you are allowed to, so you learn where it helps and where it fails.",
         "Stay the human in the loop: you own the result and the judgement calls.",
         "Assume today's model is the weakest you will ever use; plan for capability to keep rising."],
        "For one week, try an LLM first on every writing or analysis task and log where it saved time and where it misled you."),
    "b_100page": book(
        "The Hundred-Page Machine Learning Book", "Andriy Burkov", 2019, 5, "B",
        "A compact tour of machine learning: the main algorithms, how they are trained and evaluated, and the practical traps.",
        ["Most ML is choosing a model family, a loss to minimize and a way to check generalization.",
         "Feature engineering and data quality often matter more than the algorithm.",
         "Regularization and validation sets are the everyday tools against overfitting."],
        "Read one chapter, then explain that algorithm to a colleague in three sentences without jargon."),
    "b_nakedstats": book(
        "Naked Statistics", "Charles Wheelan", 2013, 7, "B",
        "A funny, intuition-first explanation of the statistics behind data, polls and experiments, with almost no formulas.",
        ["Averages hide spread; always ask for the distribution.",
         "Correlation is not causation; look for the hidden third factor.",
         "Sample size and selection bias decide whether a result can be trusted."],
        "Find one metric in a recent status report and ask: what is the sample size, and could selection bias explain it?"),
    "b_dsbiz": book(
        "Data Science for Business", "Foster Provost & Tom Fawcett", 2013, 12, "B",
        "A classic on 'data-analytic thinking': how to frame business problems so data and models can answer them.",
        ["Start from the business decision, then choose the data mining task (classification, regression, clustering).",
         "Use expected value (probability times benefit or cost) to compare models in money, not accuracy.",
         "Overfitting is the central danger; holdout data is how you see it."],
        "Write an expected-value table (benefit of a true positive, cost of a false positive) for one AI use case."),
    "b_handson": book(
        "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow", "Aurélien Géron", 2022, 25, "I",
        "The most popular practical ML book: an end-to-end project first, then classic algorithms and deep learning in code.",
        ["Follow a checklist: frame the problem, get data, explore, prepare, shortlist models, fine-tune, launch, monitor.",
         "Pipelines keep data preparation reproducible and avoid leaking test data into training.",
         "Start simple (linear models, trees) before reaching for neural networks."],
        "Run the chapter 2 housing project notebook end to end and write down every decision the author makes."),
    "b_dlpython": book(
        "Deep Learning with Python", "François Chollet", 2021, 15, "I",
        "The creator of Keras explains deep learning with clear intuition and short, runnable examples.",
        ["A neural network is a chain of simple geometric transformations learned from data.",
         "Most practical progress comes from good data, a sensible baseline and careful validation.",
         "Deep learning generalizes by interpolating between examples it has seen, which explains both its power and its limits."],
        "Train the book's first image classifier in a free notebook, then double the data and compare accuracy."),
    "b_goodfellow": book(
        "Deep Learning", "Ian Goodfellow, Yoshua Bengio & Aaron Courville", 2016, 30, "A",
        "The standard textbook on the math and theory of deep learning, from linear algebra to generative models.",
        ["Optimization, regularization and architecture are the three levers of deep learning.",
         "Probability and information theory explain loss functions such as cross-entropy.",
         "Representation learning is the core idea: models learn their own features."],
        "Use it as a reference: when a term confuses you in a design review, read only that section."),
    "b_handsonllm": book(
        "Hands-On Large Language Models", "Jay Alammar & Maarten Grootendorst", 2024, 14, "I",
        "A highly visual guide to how LLMs work and how to use them for search, classification, RAG and fine-tuning.",
        ["Tokens and embeddings are the foundation: text becomes numbers that capture meaning.",
         "Many useful applications need no training: embeddings plus semantic search go a long way.",
         "Fine-tuning is the last resort after prompting and retrieval, not the first step."],
        "Recreate the semantic search example on 50 of your team's documents and test five real questions."),
    "b_raschka": book(
        "Build a Large Language Model (From Scratch)", "Sebastian Raschka", 2024, 18, "A",
        "Step-by-step code that builds a small GPT-style model: tokenizer, attention, pretraining and fine-tuning.",
        ["Attention is just weighted averaging, where the weights are learned from the data.",
         "Pretraining teaches next-token prediction; instruction tuning teaches the model to follow requests.",
         "Seeing every layer in code removes the mystery from model size, context length and compute."],
        "Work through the attention chapter, then explain to an engineer why longer context costs more compute."),
    "b_promptllm": book(
        "Prompt Engineering for LLMs", "John Berryman & Albert Ziegler", 2024, 8, "I",
        "Two engineers who built GitHub Copilot explain prompting as assembling the right document for a model to complete.",
        ["An LLM continues a document; a good prompt makes the desired answer the natural continuation.",
         "Choose, rank and trim context to fit the window; the order of information matters.",
         "Evaluate prompts with test sets, not by feel."],
        "Rewrite one prompt you use at work with a clear role, context, examples and output format; compare 10 outputs."),
    "b_aieng": book(
        "AI Engineering", "Chip Huyen", 2025, 16, "A",
        "A practical guide to building products on foundation models: evaluation, prompting, RAG, agents, fine-tuning and inference.",
        ["Evaluation is the hardest and most important part of building with foundation models.",
         "Try prompting first, then retrieval, then fine-tuning, measuring at each step.",
         "Latency, cost and user feedback loops shape the architecture as much as model quality."],
        "Use the book's evaluation chapter to draft an eval plan for one LLM feature your team is shipping."),
    "b_dmls": book(
        "Designing Machine Learning Systems", "Chip Huyen", 2022, 12, "A",
        "How production ML systems really work: data pipelines, features, deployment, distribution shift, monitoring and teams.",
        ["Models in production fail quietly because the data changes, not the code.",
         "Batch versus online prediction is a major design choice with cost and latency trade-offs.",
         "Continual learning and monitoring need to be planned from day one."],
        "Draw your team's ML system end to end (data, features, training, serving, monitoring) and mark who owns each box."),
    "b_mlpatterns": book(
        "Machine Learning Design Patterns", "Valliappa Lakshmanan, Sara Robinson & Michael Munn", 2020, 12, "A",
        "Thirty named solutions to recurring ML problems, from data representation to reproducibility and responsible AI.",
        ["Named patterns (feature store, checkpoints, model versioning) give teams a shared vocabulary.",
         "Many patterns exist to keep training and serving consistent.",
         "Responsible AI patterns (explainable predictions, fairness lens) belong in the design, not after launch."],
        "Pick three patterns and check whether your current ML project uses them; add missing ones to the risk log."),
    "b_reliable": book(
        "Reliable Machine Learning", "Cathy Chen, Niall Richard Murphy et al.", 2022, 12, "A",
        "Site reliability engineering applied to ML: how to run models in production with SLOs, incidents and on-call.",
        ["ML systems need service level objectives for model quality, not just uptime.",
         "Incidents often come from data pipelines; give data the same rigor as code.",
         "Organizations, not just models, decide whether ML is reliable."],
        "Write one service level objective for a model your team owns (for example, weekly precision above a threshold)."),
    "b_kohavi": book(
        "Trustworthy Online Controlled Experiments", "Ron Kohavi, Diane Tang & Ya Xu", 2020, 10, "I",
        "Leaders of experimentation at Microsoft, Google and LinkedIn explain how to run A/B tests you can trust.",
        ["Agree on one overall evaluation criterion before the test starts.",
         "Most ideas do not improve the metric; experiments protect you from your own optimism.",
         "Guardrail metrics and sanity checks catch broken experiments; surprising results deserve suspicion first."],
        "For your next AI feature launch, write the primary metric, two guardrail metrics and the minimum effect you care about."),
    "b_alignment": book(
        "The Alignment Problem", "Brian Christian", 2020, 10, "I",
        "A readable history of how machine learning systems can learn the wrong lessons, and how researchers try to fix it.",
        ["Models optimize exactly what you measure, which is often not what you meant.",
         "Biased training data produces biased models, even with good intentions.",
         "Learning from human feedback and demonstrations is one path to aligning systems with human values."],
        "Find one metric your AI feature optimizes and write down a way the model could score well while failing users."),
    "b_wmd": book(
        "Weapons of Math Destruction", "Cathy O'Neil", 2016, 6, "B",
        "A data scientist shows how opaque, large-scale models in hiring, lending and policing can harm people.",
        ["Harmful models share three traits: opacity, scale and damage.",
         "Feedback loops can make a biased model look more accurate over time.",
         "People affected by a model deserve a way to understand and appeal its decisions."],
        "For one model your org uses on people, check: can the affected person see why, and can they appeal?"),
    "b_aima": book(
        "Artificial Intelligence: A Modern Approach", "Stuart Russell & Peter Norvig", 2020, 40, "A",
        "The definitive university textbook on AI: agents, search, logic, probability, learning and ethics.",
        ["AI is framed as building rational agents that act to achieve the best expected outcome.",
         "Machine learning is one part of AI; search, planning and reasoning matter too, especially for agents.",
         "Uncertainty is handled with probability, which underpins modern ML."],
        "Read the chapter on intelligent agents before your first agent design review."),
    "b_mly": book(
        "Machine Learning Yearning", "Andrew Ng", 2018, 3, "I",
        "Short chapters of practical strategy for ML projects: how to set up data splits, metrics and error analysis.",
        ["Dev and test sets should look like the data you will see in the future.",
         "Pick a single-number evaluation metric so the team can decide quickly.",
         "Error analysis on 100 misclassified examples tells you what to fix next."],
        "Run an error-analysis session: review 50 model mistakes with the team and tally the causes."),
    "b_inspired": book(
        "Inspired", "Marty Cagan", 2017, 8, "I",
        "How strong tech product teams discover products worth building before they commit engineering time.",
        ["Address four risks early: value, usability, feasibility and business viability.",
         "Prototype and test ideas cheaply before planning delivery.",
         "Empowered teams are given problems to solve, not features to build."],
        "For your AI roadmap item, write one sentence on each of the four risks and how you will test it this month."),
    "b_staffpath": book(
        "The Staff Engineer's Path", "Tanya Reilly", 2022, 9, "A",
        "A guide to senior technical leadership beyond management: big-picture thinking, executing large projects and growing others.",
        ["Senior technical roles are about the big picture, project execution and leveling up others.",
         "Maps of the technical, organizational and political landscape guide where to invest.",
         "Writing (design docs, strategies) scales your influence beyond the meetings you attend."],
        "Write a one-page 'map' of your AI program: goals, systems, teams, risks and open decisions."),
    "b_molnar": book(
        "Interpretable Machine Learning", "Christoph Molnar", 2019, 10, "A",
        "A free online book on how to explain model predictions, from simple interpretable models to SHAP values.",
        ["Some models are interpretable by design; others need post-hoc explanation methods.",
         "Feature importance and partial dependence show what drives predictions overall.",
         "Local explanations (such as SHAP) explain one prediction, which helps with appeals and debugging."],
        "Ask your data scientist for the top five features of a model and check each one makes business sense."),
    "b_comingwave": book(
        "The Coming Wave", "Mustafa Suleyman", 2023, 8, "B",
        "A co-founder of DeepMind argues that AI and biotech will spread fast and need new forms of containment and governance.",
        ["Powerful technologies tend to spread and get cheaper, which makes control hard.",
         "Governance needs technical safety, audits, regulation and international cooperation together.",
         "Builders have a responsibility to slow down where risks are severe."],
        "List three safeguards your team's AI product already has and one it should add."),

    # ───────────── 🎓 Courses ─────────────
    "c_aife": course(
        "AI For Everyone", "DeepLearning.AI (Andrew Ng) on Coursera", 6, "B", "Free to audit",
        "https://www.coursera.org/learn/ai-for-everyone",
        "A non-technical course on what AI can and cannot do, and how to run AI projects in a company.",
        ["Machine learning is mostly supervised learning: learning a mapping from inputs to outputs.",
         "AI projects follow a workflow: collect data, train, deploy, then iterate with new data.",
         "Start AI transformation with small pilot projects that show value quickly."],
        "After week 2, list three tasks on your team that take one second of human thought; those are AI candidates."),
    "c_genaife": course(
        "Generative AI for Everyone", "DeepLearning.AI (Andrew Ng) on Coursera", 5, "B", "Free to audit",
        "https://www.coursera.org/learn/generative-ai-for-everyone",
        "A short, non-technical course on how generative AI works, what it is good at, and how to build projects with it.",
        ["LLMs are trained to predict the next word, which lets them write, summarize and answer questions.",
         "A generative AI project cycle is: scope, build a prototype, evaluate, deploy and monitor.",
         "Analyze jobs as tasks: AI augments or automates tasks, not whole jobs."],
        "Break your own job into 10 tasks and rate how much an LLM could help each one."),
    "c_elements": course(
        "Elements of AI", "University of Helsinki & MinnaLearn", 30, "B", "Free",
        "https://www.elementsofai.com",
        "A free, beginner-friendly online course on AI basics, taken by over a million people in many languages.",
        ["AI is a set of techniques, not a single thing; autonomy and adaptivity are its key properties.",
         "Probability and simple models explain much of how AI handles uncertainty.",
         "AI's societal impact depends on human choices."],
        "Complete one chapter per week and write a one-line takeaway for each."),
    "c_mlcc": course(
        "Machine Learning Crash Course", "Google", 15, "B", "Free",
        "https://developers.google.com/machine-learning/crash-course",
        "Google's fast-paced introduction to ML with short videos, interactive visualizations and exercises.",
        ["Linear and logistic regression teach loss, gradient descent and learning rate.",
         "Classification thresholds trade precision against recall.",
         "Production ML and fairness modules cover what happens after the model is trained."],
        "Play with the interactive learning-rate exercise until you can predict when training will diverge."),
    "c_mlspec": course(
        "Machine Learning Specialization", "DeepLearning.AI & Stanford Online on Coursera", 60, "I", "Free to audit; certificate paid",
        "https://www.coursera.org/specializations/machine-learning-introduction",
        "Andrew Ng's updated three-course foundation in supervised learning, advanced algorithms and unsupervised learning, in Python.",
        ["Gradient descent is the engine behind most ML training.",
         "Bias and variance diagnosis tells you whether to get more data or a bigger model.",
         "Decision trees, clustering, recommenders and reinforcement learning complete the toolkit."],
        "Do the optional labs, then change one hyperparameter in each and predict the effect before running it."),
    "c_dlspec": course(
        "Deep Learning Specialization", "DeepLearning.AI on Coursera", 120, "I", "Free to audit; certificate paid",
        "https://www.coursera.org/specializations/deep-learning",
        "Five courses on neural networks, tuning, structuring ML projects, convolutional networks and sequence models.",
        ["Initialization, regularization and optimization choices make deep networks trainable.",
         "Structuring ML projects (data splits, error analysis) is a core skill for leads and TPMs.",
         "CNNs handle images and sequence models handle text and time series."],
        "Take course 3 (Structuring ML Projects) first; it is short and directly useful for program managers."),
    "c_fastai": course(
        "Practical Deep Learning for Coders", "fast.ai (Jeremy Howard)", 40, "I", "Free",
        "https://course.fast.ai",
        "A top-down, code-first course where you train working deep learning models from the first lesson.",
        ["You can build useful models before you understand all the math.",
         "Transfer learning from pretrained models gives strong results with little data.",
         "Look at your data and your model's errors constantly."],
        "Train the lesson 1 image classifier on a topic you choose, then deploy it as a small demo."),
    "c_kaggle": course(
        "Kaggle Learn micro-courses", "Kaggle", 20, "B", "Free",
        "https://www.kaggle.com/learn",
        "Short, hands-on courses in browser notebooks: Python, pandas, intro and intermediate ML, feature engineering.",
        ["Learning by editing working notebooks is the fastest way to lose fear of code.",
         "Data leakage and missing values are the most common real-world traps.",
         "Competitions show what strong baselines look like."],
        "Finish Intro to Machine Learning and submit one entry to the beginner housing-price competition."),
    "c_hfllm": course(
        "Hugging Face LLM Course", "Hugging Face", 30, "I", "Free",
        "https://huggingface.co/learn",
        "A free course on transformers, tokenizers, datasets and fine-tuning using the Hugging Face ecosystem.",
        ["Pretrained models plus pipelines solve many tasks in a few lines of code.",
         "Tokenizers decide how text is split, which affects cost and quality.",
         "Fine-tuning adapts a pretrained model to your task with relatively little data."],
        "Run a sentiment or summarization pipeline on 20 real customer comments and judge the output yourself."),
    "c_hfagents": course(
        "Hugging Face AI Agents Course", "Hugging Face", 20, "A", "Free",
        "https://huggingface.co/learn",
        "A free course on how AI agents think, call tools and act, with hands-on work in popular agent frameworks.",
        ["Agents loop through thought, action and observation until a task is done.",
         "Tools (search, code, APIs) extend what a model can do, and also what can go wrong.",
         "Agent frameworks differ mostly in how they manage state, memory and control flow."],
        "Build the course's first agent with one tool, then write down every failure you see in 10 runs."),
    "c_dlai_short": course(
        "DeepLearning.AI short courses", "DeepLearning.AI with industry partners", 2, "I", "Mostly free",
        "https://www.deeplearning.ai/short-courses/",
        "One- to two-hour hands-on courses on prompting, RAG, agents, evaluation and fine-tuning, often taught with the tool makers.",
        ["Short, focused courses fit a busy TPM's week.",
         "Each course comes with notebooks you can run and adapt.",
         "They track new techniques faster than long specializations."],
        "Take one short course per month on whatever your team is building next."),
    "c_msgenai": course(
        "Generative AI for Beginners", "Microsoft (open source on GitHub)", 25, "B", "Free",
        "https://github.com/microsoft/generative-ai-for-beginners",
        "Twenty-plus lessons covering prompts, chat and search apps, RAG, agents, fine-tuning and responsible AI.",
        ["Each lesson pairs a concept with a small runnable app.",
         "Responsible AI is taught alongside building, not as an afterthought.",
         "Patterns carry across model providers."],
        "Pick the RAG lesson, run it, and swap in your own small document set."),
    "c_anthropic": course(
        "Anthropic courses", "Anthropic (open source on GitHub)", 10, "I", "Free (API usage may cost)",
        "https://github.com/anthropics/courses",
        "Free notebooks on API basics, interactive prompt engineering, real-world prompting, prompt evaluations and tool use.",
        ["Clear, direct instructions and examples beat clever tricks.",
         "Structure prompts with tags and ask for structured outputs to make results easier to check.",
         "Build prompt evaluations so you know when a change helped."],
        "Complete the prompt engineering tutorial and apply three techniques to a prompt your team actually uses."),
    "c_cs229": course(
        "CS229: Machine Learning", "Stanford University", 60, "A", "Free lecture videos",
        "https://cs229.stanford.edu",
        "Stanford's math-heavy graduate ML course covering supervised, unsupervised and reinforcement learning.",
        ["The math (linear algebra, probability, optimization) explains why algorithms work.",
         "Generalization theory explains bias, variance and regularization.",
         "Seeing derivations helps you judge claims in research papers."],
        "Watch only the lectures on topics your team uses, with the lecture notes open."),
    "c_cs224n": course(
        "CS224N: Natural Language Processing with Deep Learning", "Stanford University", 60, "A", "Free lecture videos",
        "https://web.stanford.edu/class/cs224n/",
        "Stanford's course on word vectors, neural networks, transformers, pretraining and large language models.",
        ["Word vectors capture meaning as positions in space.",
         "Transformers replaced recurrent networks because attention parallelizes and handles long context better.",
         "Pretraining plus adaptation is the dominant recipe for language models."],
        "Watch the transformers and pretraining lectures before your next LLM architecture review."),
    "c_mit191": course(
        "MIT 6.S191: Introduction to Deep Learning", "MIT (Alexander Amini & Ava Amini)", 15, "I", "Free",
        "http://introtodeeplearning.com",
        "MIT's fast, updated-yearly bootcamp on deep learning, with lectures and hands-on labs.",
        ["One week of lectures covers networks, sequence models, vision, generative models and reinforcement learning.",
         "Labs make each idea concrete in code.",
         "Guest lectures show current industry practice."],
        "Watch the first two lectures in one weekend and do the first lab."),
    "c_madewithml": course(
        "Made With ML", "Goku Mohandas", 30, "A", "Free",
        "https://madewithml.com",
        "A free course on building production-grade ML: design, data, training, testing, serving and CI/CD.",
        ["Treat ML as software: version data, code and models, and test all three.",
         "Start with a product framing and success metrics before any modeling.",
         "Automate training and deployment so iteration is cheap."],
        "Use its project design template to write a one-page plan for your next ML feature."),
    "c_fsdl": course(
        "Full Stack Deep Learning & LLM Bootcamp", "Full Stack Deep Learning", 20, "A", "Free archived lectures",
        "https://fullstackdeeplearning.com",
        "Free lectures on shipping deep learning and LLM products: tooling, deployment, monitoring, UX and team structure.",
        ["Shipping ML is mostly engineering and process, not modeling.",
         "LLM apps need prompt management, evaluation and monitoring (often called LLMOps).",
         "UX choices, such as showing sources and allowing edits, make AI features trusted."],
        "Watch the LLM Bootcamp lecture on deployment or UX and compare it with your product."),
    "c_aipm": course(
        "AI Product Management Specialization", "Duke University on Coursera", 30, "I", "Free to audit; certificate paid",
        "https://www.coursera.org/search?query=AI%20Product%20Management%20Duke",
        "Three courses for managers on ML fundamentals, managing ML projects, and human factors and privacy in AI.",
        ["ML projects follow the CRISP-DM style cycle: understand, prepare, model, evaluate, deploy.",
         "Design for user trust and handle privacy from the start.",
         "Program managers need enough ML to ask the right questions, not to build models."],
        "Use the course's project lifecycle to audit one in-flight AI project for skipped steps."),
    "c_gcsb": course(
        "Generative AI learning path", "Google Cloud Skills Boost", 8, "B", "Free intro courses",
        "https://www.cloudskillsboost.google",
        "Short free courses including Introduction to Generative AI, Introduction to LLMs and Introduction to Responsible AI.",
        ["Each intro course takes under an hour and ends with a quiz.",
         "Responsible AI principles are presented as product requirements.",
         "A good primer before the Google Cloud Generative AI Leader exam."],
        "Do the three intro courses in one week and note one idea per course you can use at work."),

    # ───────────── 🏅 Certifications ─────────────
    "x_awsaip": cert(
        "AWS Certified AI Practitioner (AIF-C01)", "Amazon Web Services", 20, "B", 100,
        "https://aws.amazon.com/certification/",
        "A foundational exam on AI, ML and generative AI concepts, AWS AI services and responsible AI.",
        ["Covers ML basics, generative AI use cases, prompt engineering and foundation model customization.",
         "Tests knowledge of responsible AI, security and governance on AWS.",
         "No coding; well suited to TPMs and product roles."],
        "Use AWS Skill Builder's free exam prep plan; budget about 20 hours over three weeks."),
    "x_awsmle": cert(
        "AWS Certified Machine Learning Engineer – Associate (MLA-C01)", "Amazon Web Services", 60, "I", 150,
        "https://aws.amazon.com/certification/",
        "An associate-level exam on preparing data, building, deploying and monitoring ML models on AWS.",
        ["Heavy on SageMaker workflows and ML pipelines.",
         "Covers deployment, scaling, monitoring and cost optimization.",
         "Signals hands-on ML engineering literacy for senior technical TPMs."],
        "Take it after the AI Practitioner exam and one hands-on SageMaker project."),
    "x_ai900": cert(
        "Microsoft Azure AI Fundamentals (AI-900)", "Microsoft", 15, "B", 99,
        "https://learn.microsoft.com/credentials/",
        "A fundamentals exam on AI workloads, ML principles, computer vision, NLP and generative AI on Azure.",
        ["Concept-focused; little or no coding.",
         "Free Microsoft Learn modules cover the whole syllabus.",
         "Microsoft refreshes exams and codes often, so check the current version before booking."],
        "Complete the free Microsoft Learn path and practice assessment, then book the exam."),
    "x_ai102": cert(
        "Microsoft Azure AI Engineer Associate (AI-102)", "Microsoft", 60, "I", 165,
        "https://learn.microsoft.com/credentials/",
        "An associate exam on designing and implementing AI solutions with Azure AI services, including generative AI.",
        ["Covers planning, managing and securing Azure AI solutions.",
         "Includes generative AI, agents, search and document intelligence.",
         "Requires some coding familiarity (Python or C#)."],
        "Pair the Microsoft Learn path with building one small Azure AI app before the exam."),
    "x_gcpgenai": cert(
        "Google Cloud Generative AI Leader", "Google Cloud", 15, "B", 99,
        "https://cloud.google.com/learn/certification",
        "A non-technical exam on generative AI fundamentals, Google Cloud's AI offerings and leading AI adoption.",
        ["Aimed at business and program leaders rather than engineers.",
         "Covers gen AI concepts, business strategy and responsible AI.",
         "A quick, credible signal for a TPM moving into AI programs."],
        "Do the free Google Cloud Skills Boost learning path, then sit the exam within two weeks."),
    "x_gcpmle": cert(
        "Google Cloud Professional Machine Learning Engineer", "Google Cloud", 80, "A", 200,
        "https://cloud.google.com/learn/certification",
        "A professional exam on designing, building and productionizing ML solutions on Google Cloud.",
        ["Covers ML problem framing, data pipelines, model development, MLOps and monitoring.",
         "Includes generative AI and Vertex AI topics.",
         "One of the more demanding cloud ML exams; best after real project experience."],
        "Attempt only after you have shipped or closely managed one ML system end to end."),
    "x_nvgenl": cert(
        "NVIDIA Certified Associate: Generative AI LLMs (NCA-GENL)", "NVIDIA", 30, "I", 135,
        "https://www.nvidia.com/en-us/learn/certification/",
        "An associate exam on the fundamentals of developing, integrating and maintaining LLM-based applications.",
        ["Covers ML and transformer basics, prompt engineering and LLM deployment.",
         "Touches on GPU acceleration and NVIDIA tooling.",
         "Useful for TPMs working near AI infrastructure."],
        "Review NVIDIA's free exam guide and the related Deep Learning Institute courses."),
    "x_cpmai": cert(
        "PMI Certified Professional in Managing AI (PMI-CPMAI)", "Project Management Institute", 30, "I", None,
        "https://www.pmi.org",
        "A certification on managing AI projects using a data-centric, iterative methodology adapted from CRISP-DM.",
        ["Six phases: business understanding, data understanding, data preparation, model development, evaluation, operationalization.",
         "Teaches when not to use AI and how to scope projects to avoid common failures.",
         "The closest match to the AI TPM role among well-known certifications."],
        "Check PMI's site for the current training and exam bundle price before planning."),
    "x_aigp": cert(
        "Artificial Intelligence Governance Professional (AIGP)", "IAPP", 40, "A", 799,
        "https://iapp.org/certify/aigp/",
        "A certification on AI governance: laws and standards, risk management and governing the AI lifecycle.",
        ["Covers the EU AI Act, NIST AI RMF and other frameworks.",
         "Focuses on policies, impact assessments and accountability.",
         "Valued for AI TPMs working on compliance-heavy programs (members pay less than the listed non-member fee)."],
        "Start with IAPP's free body of knowledge document to judge fit before buying training."),
    "x_dbml": cert(
        "Databricks Certified Machine Learning Associate", "Databricks", 30, "I", 200,
        "https://www.databricks.com/learn/certification",
        "An associate exam on running ML workflows on Databricks, including MLflow, feature engineering and model management.",
        ["Covers the lakehouse ML workflow and experiment tracking.",
         "Tests practical skills with MLflow and model registries.",
         "Most useful if your company runs data and ML on Databricks."],
        "Use Databricks Academy's free self-paced courses, then practice in a trial workspace."),

    # ───────────── 🎧 Podcasts ─────────────
    "p_practical": podcast(
        "Practical AI", "Daniel Whitenack & Chris Benson", "B", 45, "https://practicalai.fm",
        "Accessible conversations on making AI practical, productive and accessible to everyone.",
        ["Friendly for beginners; explains terms as it goes.",
         "Covers tools, MLOps and real-world deployments.",
         "Good mix of technical and business guests."],
        "Search the archive for an episode on the tool or problem your team is working on."),
    "p_twiml": podcast(
        "The TWIML AI Podcast", "Sam Charrington", "I", 50, "https://twimlai.com",
        "Long-running interviews with ML researchers and practitioners about their work.",
        ["Deep yet approachable explanations of new research.",
         "Many episodes on enterprise ML in production.",
         "A large archive covering almost every ML topic."],
        "Pick one episode per week on a topic from this app's current stage."),
    "p_latent": podcast(
        "Latent Space", "swyx & Alessio Fanelli", "A", 60, "https://www.latent.space",
        "Technical conversations for AI engineers building with foundation models.",
        ["Tracks the newest tools, agents and model releases.",
         "Guests are builders, so episodes are practical.",
         "Useful vocabulary for talking with AI engineering teams."],
        "Choose an episode on evals, agents or inference and write down three terms to look up."),
    "p_dwarkesh": podcast(
        "Dwarkesh Podcast", "Dwarkesh Patel", "A", 120, "https://www.dwarkesh.com",
        "Long, well-researched interviews with AI researchers, lab leaders and economists.",
        ["Explores scaling, AI progress and long-term impact.",
         "The host prepares deeply, so questions are sharp.",
         "Transcripts make it easy to skim."],
        "Read the transcript of one AI researcher interview and summarize the guest's view of scaling."),
    "p_lex": podcast(
        "Lex Fridman Podcast", "Lex Fridman", "I", 180, "https://lexfridman.com/podcast/",
        "Very long conversations with AI researchers, founders and scientists.",
        ["Many landmark interviews with AI pioneers.",
         "Good for the big picture and history.",
         "Timestamps let you jump to the AI segment."],
        "Use timestamps to listen to one 30-minute AI segment instead of the whole episode."),
    "p_hardfork": podcast(
        "Hard Fork", "Kevin Roose & Casey Newton", "B", 60, "https://www.nytimes.com/column/hard-fork",
        "A weekly show on tech and AI news with context and humor.",
        ["Keeps you current on AI in under an hour a week.",
         "Explains why news matters to ordinary users and companies.",
         "Good conversation starters with non-technical stakeholders."],
        "Listen weekly on your commute and share one takeaway with your team."),
    "p_nopriors": podcast(
        "No Priors", "Sarah Guo & Elad Gil", "I", 45, None,
        "Investors interview AI founders and researchers about where AI is going and how companies are built on it.",
        ["Strong on AI business models and strategy.",
         "Guests include leaders of major AI labs and startups.",
         "Helps a TPM understand build-versus-buy markets."],
        "Pick an episode with a company whose product your team uses or competes with."),
    "p_cogrev": podcast(
        "The Cognitive Revolution", "Nathan Labenz", "I", 90, None,
        "In-depth interviews about AI capabilities, applications and safety.",
        ["Balances practical use with safety and policy.",
         "Guests explain how they build and evaluate AI products.",
         "Good for staying current on frontier capabilities."],
        "Choose an episode on AI safety or evaluation and compare it with your team's practices."),
    "p_lenny": podcast(
        "Lenny's Podcast", "Lenny Rachitsky", "I", 75, "https://www.lennysnewsletter.com/podcast",
        "Product and growth lessons from tech leaders, with many episodes on building AI products.",
        ["Practical advice on AI product strategy and evals from product leaders.",
         "Career advice for product and program roles.",
         "Frameworks you can reuse in planning documents."],
        "Search the archive for 'AI evals' or 'AI product' and take notes on one framework."),
    "p_gradient": podcast(
        "Gradient Dissent", "Lukas Biewald (Weights & Biases)", "A", 50, None,
        "Interviews with ML practitioners about how models are built and deployed in industry.",
        ["Focus on real production ML stories.",
         "Covers MLOps, tooling and team practices.",
         "Useful for TPMs who coordinate ML engineering teams."],
        "Pick an episode from a company in your industry and note how they run ML in production."),

    # ───────────── ▶️ YouTube ─────────────
    "y_3b1b": youtube(
        "3Blue1Brown", "Grant Sanderson", "B", 20, "3Blue1Brown neural networks",
        "Beautiful animated explanations of the math behind neural networks, gradient descent and transformers.",
        ["Builds intuition with visuals instead of formulas.",
         "The neural networks series is one of the best introductions anywhere.",
         "Newer videos explain how transformers and attention work."],
        "Watch the first four neural network videos in order, pausing to sketch each idea."),
    "y_statquest": youtube(
        "StatQuest with Josh Starmer", "Josh Starmer", "B", 15, "StatQuest Josh Starmer",
        "Clear, step-by-step explanations of statistics and ML algorithms, from p-values to transformers.",
        ["Breaks every algorithm into small, simple steps.",
         "Excellent for precision, recall, ROC curves and trees.",
         "Short videos fit between meetings."],
        "Watch the confusion matrix and ROC videos before the metrics stage quiz."),
    "y_karpathy": youtube(
        "Andrej Karpathy", "Andrej Karpathy", "I", 60, "Andrej Karpathy intro to large language models",
        "A leading AI researcher explains LLMs, from a one-hour general-audience intro to building GPT from scratch.",
        ["'Intro to Large Language Models' is a top one-hour primer for TPMs.",
         "'Neural Networks: Zero to Hero' builds models step by step in code.",
         "Longer deep dives explain how chat assistants are trained."],
        "Watch the one-hour LLM intro and write a five-bullet summary for your team."),
    "y_dlai": youtube(
        "DeepLearning.AI", "DeepLearning.AI", "B", 15, "DeepLearning.AI",
        "Short lectures, course previews and talks from Andrew Ng's education company.",
        ["Free lecture clips from popular courses.",
         "Talks on AI strategy and careers.",
         "Good companion to the Coursera courses."],
        "Search the channel for Andrew Ng's talks on AI careers or opportunities."),
    "y_ibm": youtube(
        "IBM Technology", "IBM", "B", 10, "IBM Technology RAG explained",
        "Short whiteboard explainers on AI concepts such as RAG, agents, vector databases and fine-tuning.",
        ["Most videos are under 10 minutes.",
         "Explains enterprise AI terms in plain language.",
         "Great to share with non-technical stakeholders."],
        "Watch the RAG and AI agents explainers and reuse the diagrams in your next status update."),
    "y_stanford": youtube(
        "Stanford Online", "Stanford University", "A", 75, "Stanford Online CS229 CS224N lecture",
        "Full university lectures, including machine learning, NLP and transformer seminar courses.",
        ["University depth for free.",
         "Lectures come with public slides and notes.",
         "Seminar series feature researchers presenting their own work."],
        "Watch one lecture at 1.5x speed with the slides open and write three questions."),
    "y_twominute": youtube(
        "Two Minute Papers", "Károly Zsolnai-Fehér", "B", 7, "Two Minute Papers",
        "Short, enthusiastic summaries of new AI research papers with visuals.",
        ["A quick way to see what new research can do.",
         "Covers graphics, simulation and generative AI.",
         "Links to the original papers."],
        "Watch one video a week and note one capability that could matter for your product."),
    "y_yannic": youtube(
        "Yannic Kilcher", "Yannic Kilcher", "A", 45, "Yannic Kilcher paper explained",
        "Detailed walkthroughs of influential AI papers, read and annotated on screen.",
        ["Teaches you how to read a research paper.",
         "Covers landmark papers such as 'Attention Is All You Need'.",
         "Critical commentary helps separate hype from substance."],
        "Watch the 'Attention Is All You Need' walkthrough after the transformers topic."),
    "y_umar": youtube(
        "Umar Jamil", "Umar Jamil", "A", 90, "Umar Jamil transformer from scratch",
        "Long, careful coding videos that implement transformers, diffusion models and LLM techniques from scratch.",
        ["Explains the math and the code side by side.",
         "Covers attention, quantization and fine-tuning methods.",
         "Ideal if you want real technical depth."],
        "Watch the first 30 minutes of the transformer-from-scratch video and sketch the architecture."),
    "y_welch": youtube(
        "Welch Labs", "Stephen Welch", "I", 20, "Welch Labs machine learning",
        "Story-driven, visual videos on how machine learning and neural networks actually work.",
        ["Uses history and visuals to build intuition.",
         "Explains why deep learning works, not just how.",
         "High production quality, low jargon."],
        "Watch one video and explain its main idea to someone outside tech."),
    "y_aiexplained": youtube(
        "AI Explained", "AI Explained", "I", 20, "AI Explained channel new model analysis",
        "Careful analysis of new AI models, benchmarks and research, with less hype than most news channels.",
        ["Reads the papers and model reports so you don't have to.",
         "Questions benchmark claims instead of repeating them.",
         "A good weekly way to stay current on frontier models."],
        "Watch one video after each major model release and note what changed for your use cases."),
}

RESOURCES = {key: {"key": key, **value} for key, value in _RESOURCES.items()}
