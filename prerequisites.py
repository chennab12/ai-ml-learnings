"""Prerequisite knowledge for each stage: what to know first, the core ideas in one line,
where to learn it (an earlier stage or a resource key from resources.RESOURCES) and the TPM takeaway.

Keyed by stage title (content.STAGES[i]["title"]). All text is original.
"""


def prereq(topic, core, learn, takeaway):
    return {"topic": topic, "core": core, "learn": learn, "takeaway": takeaway}


PREREQS = {
    "AI & ML foundations": [
        prereq("📊 Basic statistics", "Mean, median, spread, percentages and the idea that a sample stands in for a bigger population.",
               "b_nakedstats", "Ask 'how many examples, and are they representative?' before trusting any number."),
        prereq("🧮 Spreadsheet comfort", "Rows are examples, columns are features; sorting, filtering and simple charts.",
               "c_kaggle", "If you can read a table of examples, you can review training data with your team."),
        prereq("🐍 Python literacy (reading, not writing)", "Variables, lists, functions and notebooks; enough to follow a data scientist's notebook.",
               "c_kaggle", "Reading a notebook lets you see what was really measured instead of trusting a slide."),
        prereq("🧭 Software delivery basics", "How code goes from idea to production: requirements, testing, releases.",
               "b_inspired", "ML adds data and experimentation on top of the delivery process you already run."),
    ],
    "Measuring models": [
        prereq("🧱 Training vs test data", "Models are judged on data they never saw during training.",
               "AI & ML foundations", "Every metric you report must come from held-out data."),
        prereq("➗ Ratios and rates", "Fractions, percentages and the difference between a count and a rate.",
               "b_nakedstats", "Precision and recall are just two different ratios of the same four counts."),
        prereq("🎲 Probability basics", "Chance, base rates and why rare events are hard to predict.",
               "b_nakedstats", "With rare events, accuracy hides failure; always ask for the base rate."),
        prereq("💼 Business KPIs", "The outcome metrics your org already tracks (cost, time, revenue, risk).",
               "b_dsbiz", "Tie model metrics to a KPI leadership already cares about."),
    ],
    "Classic ML algorithms": [
        prereq("📏 Model metrics", "Precision, recall, baselines and error costs.",
               "Measuring models", "You can't compare algorithms without agreeing how to score them."),
        prereq("📈 Lines and slopes", "A straight line y = w·x + b; slope as 'change per unit'.",
               "c_mlcc", "Regression is fitting that line; weights are the slopes."),
        prereq("🗃️ Features and labels", "Inputs, the answer to predict and how data is split.",
               "AI & ML foundations", "Most algorithm debates are really data and feature debates."),
        prereq("⛰️ Optimization intuition", "Finding the lowest point of an error curve by small steps.",
               "y_3b1b", "Training time and cost come from how many steps the optimizer needs."),
    ],
    "Deep learning": [
        prereq("📉 Gradient descent", "Loss, gradients, learning rate and epochs.",
               "Classic ML algorithms", "Neural networks train the same way, just with far more parameters."),
        prereq("🧮 Vectors and matrices", "Lists of numbers and multiplying them; the shape of data.",
               "y_3b1b", "'Parameters' and 'embeddings' are just large tables of numbers; size drives memory and cost."),
        prereq("🎯 Overfitting and regularization", "Why bigger models need more data or constraints.",
               "AI & ML foundations", "More capacity means more data, compute and validation effort in the plan."),
        prereq("🖥️ Compute basics", "CPU vs GPU and why parallel hardware speeds up matrix math.",
               "y_karpathy", "Deep learning programs are often compute-bound; plan GPU access early."),
    ],
    "Generative AI & LLMs": [
        prereq("⚡ Transformers and attention", "How tokens look at each other; context length and its cost.",
               "Deep learning", "Context window and token counts set both quality limits and cost."),
        prereq("🧩 Embeddings", "Text as vectors where similar meaning sits close together.",
               "Deep learning", "Embeddings power semantic search, the core of RAG."),
        prereq("🎯 Evaluation habits", "Test sets, baselines and error analysis.",
               "Measuring models", "LLM features need test sets too; demos are not evidence."),
        prereq("🔐 Data sensitivity", "What counts as personal or confidential data in your company.",
               "c_gcsb", "Know what may be sent to an external model before prototyping."),
    ],
    "Building LLM products": [
        prereq("✍️ Prompting and RAG", "Structured prompts, few-shot examples, retrieval and citations.",
               "Generative AI & LLMs", "Most product quality comes from prompts and retrieval, not model choice."),
        prereq("🧪 Experiments and A/B tests", "Controlled comparisons and guardrail metrics.",
               "Measuring models", "Prove an LLM feature helps users, not just that it looks good."),
        prereq("🔌 APIs and latency", "How services call each other; request/response time and rate limits.",
               "c_anthropic", "Latency budgets and rate limits shape UX and capacity plans."),
        prereq("🛡️ Product risk", "Value, usability, feasibility and viability risks.",
               "b_inspired", "Agent autonomy is a product risk decision, not only a technical one."),
    ],
    "MLOps & AI infrastructure": [
        prereq("🔁 CI/CD and DevOps", "Version control, automated tests, deployment pipelines and rollback.",
               "c_madewithml", "MLOps is DevOps plus versioned data and models; reuse your release process."),
        prereq("☁️ Cloud fundamentals", "Compute, storage, networking and cost models in the cloud.",
               "x_awsaip", "Inference cost scales with traffic; forecast it like any cloud bill."),
        prereq("📡 Monitoring and SLOs", "Dashboards, alerts, on-call and service level objectives.",
               "b_reliable", "Add model-quality SLOs next to uptime SLOs, with named owners."),
        prereq("⚡ Model size and precision", "Parameters, bytes per parameter, quantization.",
               "Deep learning", "Memory math decides how many GPUs, and how much money, a model needs."),
    ],
    "Responsible AI & governance": [
        prereq("📏 Sliced metrics", "Computing precision and recall separately per group.",
               "Measuring models", "Fairness reviews start from metrics you already know how to read."),
        prereq("🗃️ Data provenance", "Where data came from, consent and who is represented in it.",
               "Classic ML algorithms", "Biased or unconsented data is a launch risk; track sources early."),
        prereq("🔐 Privacy and security basics", "Personal data, access control, threat modeling.",
               "c_msgenai", "Plan security and privacy reviews as milestones, not end-of-project gates."),
        prereq("⚖️ Your company's policies", "Internal AI, privacy and compliance policies and their owners.",
               "x_aigp", "Know who signs off on AI risk before you need the signature."),
    ],
    "AI program management": [
        prereq("📋 Core program management", "Scope, milestones, RACI, risk logs and status reporting.",
               "x_cpmai", "Your existing TPM toolkit applies; ML adds uncertainty and data work."),
        prereq("🔄 ML lifecycle", "Data, training, evaluation, deployment, monitoring and retraining.",
               "MLOps & AI infrastructure", "Each lifecycle step is a workstream with an owner and a gate."),
        prereq("🧪 Experimentation mindset", "Hypotheses, timeboxed spikes and learning from failed experiments.",
               "Measuring models", "Plan learning milestones before delivery dates."),
        prereq("🛡️ Risk and compliance", "Fairness, safety, privacy and regulatory obligations.",
               "Responsible AI & governance", "Build compliance lead time into the schedule from day one."),
    ],
    "Senior AI TPM career": [
        prereq("🗺️ End-to-end AI literacy", "Comfort with every earlier stage, from data to governance.",
               "AI program management", "Breadth across the lifecycle is the entry ticket to senior scope."),
        prereq("📣 Written communication", "One-page proposals, decision docs and clear status updates.",
               "b_staffpath", "Writing is how senior TPMs scale influence beyond meetings."),
        prereq("📊 Business acumen", "ROI, cost models and how your company makes money.",
               "b_prediction", "Frame AI work as business outcomes leaders can fund."),
        prereq("🤝 Stakeholder management", "Aligning engineering, product, legal and executives.",
               "p_lenny", "Senior impact is measured by decisions you move across teams."),
    ],
}
