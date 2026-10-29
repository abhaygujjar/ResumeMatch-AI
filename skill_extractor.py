"""Skill extraction with aliases, word-boundary matching and required/preferred split."""

import re

# (Display name, [aliases in lowercase])
SKILLS = [
    # Programming languages
    ("Python", ["python", "python3"]),
    ("Java", ["java"]),
    ("JavaScript", ["javascript", "js", "ecmascript", "es6"]),
    ("TypeScript", ["typescript"]),
    ("C++", ["c++"]),
    ("C#", ["c#"]),
    ("C", ["c programming", "c language"]),
    ("Go", ["golang", "go language"]),
    ("Rust", ["rust"]),
    ("PHP", ["php"]),
    ("Ruby", ["ruby"]),
    ("Kotlin", ["kotlin"]),
    ("Swift", ["swift"]),
    ("R", ["r programming", "rstudio"]),
    ("MATLAB", ["matlab"]),
    ("Bash", ["bash", "shell scripting"]),
    ("SQL", ["sql", "structured query language"]),
    ("HTML", ["html", "html5"]),
    ("CSS", ["css", "css3"]),
    # Web
    ("React", ["react", "reactjs", "react.js"]),
    ("Angular", ["angular", "angularjs"]),
    ("Vue.js", ["vue", "vuejs", "vue.js"]),
    ("Node.js", ["node.js", "nodejs", "node js"]),
    ("Express.js", ["express.js", "expressjs"]),
    ("Django", ["django"]),
    ("Flask", ["flask"]),
    ("FastAPI", ["fastapi"]),
    ("Spring Boot", ["spring boot", "springboot"]),
    ("Streamlit", ["streamlit"]),
    ("REST API", ["rest api", "rest apis", "restful", "restful api", "restful apis"]),
    ("GraphQL", ["graphql"]),
    ("Tailwind CSS", ["tailwind", "tailwindcss"]),
    ("Bootstrap", ["bootstrap"]),
    # Data / AI
    ("Machine Learning", ["machine learning", "ml"]),
    ("Deep Learning", ["deep learning"]),
    ("NLP", ["nlp", "natural language processing"]),
    ("Computer Vision", ["computer vision"]),
    ("Generative AI", ["generative ai", "genai", "gen ai"]),
    ("LLM", ["llm", "llms", "large language model", "large language models"]),
    ("Data Analysis", ["data analysis", "data analytics", "data analyst"]),
    ("Data Science", ["data science"]),
    ("Data Visualization", ["data visualization", "data visualisation"]),
    ("Statistics", ["statistics", "statistical analysis"]),
    ("Pandas", ["pandas"]),
    ("NumPy", ["numpy"]),
    ("Scikit-learn", ["scikit-learn", "scikit learn", "sklearn"]),
    ("TensorFlow", ["tensorflow"]),
    ("Keras", ["keras"]),
    ("PyTorch", ["pytorch", "torch"]),
    ("OpenCV", ["opencv"]),
    ("YOLO", ["yolo", "yolov8", "yolov5"]),
    ("Hugging Face", ["hugging face", "huggingface"]),
    ("LangChain", ["langchain"]),
    ("Matplotlib", ["matplotlib"]),
    ("Seaborn", ["seaborn"]),
    ("Plotly", ["plotly"]),
    ("Tableau", ["tableau"]),
    ("Power BI", ["power bi", "powerbi"]),
    ("Excel", ["excel", "microsoft excel", "ms excel", "advanced excel"]),
    ("Spark", ["spark", "pyspark", "apache spark"]),
    ("Hadoop", ["hadoop"]),
    ("ETL", ["etl"]),
    # Databases
    ("MySQL", ["mysql"]),
    ("PostgreSQL", ["postgresql", "postgres"]),
    ("MongoDB", ["mongodb", "mongo"]),
    ("SQLite", ["sqlite"]),
    ("Redis", ["redis"]),
    ("Firebase", ["firebase"]),
    ("Oracle", ["oracle"]),
    # DevOps / Cloud / Tools
    ("Git", ["git"]),
    ("GitHub", ["github"]),
    ("GitLab", ["gitlab"]),
    ("Docker", ["docker"]),
    ("Kubernetes", ["kubernetes", "k8s"]),
    ("AWS", ["aws", "amazon web services"]),
    ("Azure", ["azure", "microsoft azure"]),
    ("Google Cloud", ["gcp", "google cloud", "google cloud platform"]),
    ("CI/CD", ["ci/cd", "ci cd", "cicd", "continuous integration"]),
    ("Jenkins", ["jenkins"]),
    ("Linux", ["linux", "unix"]),
    ("Jira", ["jira"]),
    ("Postman", ["postman"]),
    ("Agile", ["agile", "scrum", "kanban"]),
    ("Data Structures", ["data structures", "dsa", "data structures and algorithms"]),
    ("Algorithms", ["algorithms"]),
    ("OOP", ["oop", "object oriented programming", "object-oriented programming"]),
    ("Unit Testing", ["unit testing", "pytest", "unittest", "junit"]),
    ("Figma", ["figma"]),
    # Business / Finance / General
    ("Accounting", ["accounting", "accountant"]),
    ("Auditing", ["auditing", "audit", "audits", "auditor"]),
    ("Bookkeeping", ["bookkeeping"]),
    ("Financial Reporting", ["financial reporting", "financial reports"]),
    ("Financial Analysis", ["financial analysis", "financial modeling", "financial modelling"]),
    ("Budgeting", ["budgeting", "budget management", "budgets"]),
    ("Accounts Payable", ["accounts payable"]),
    ("Accounts Receivable", ["accounts receivable"]),
    ("Reconciliation", ["reconciliation", "reconciliations", "balancing", "balance"]),
    ("QuickBooks", ["quickbooks"]),
    ("SAP", ["sap"]),
    ("Tally", ["tally", "tally erp"]),
    ("GAAP", ["gaap"]),
    ("Payroll", ["payroll"]),
    ("Taxation", ["taxation", "tax preparation"]),
    ("Project Management", ["project management", "project manager"]),
    ("Product Management", ["product management"]),
    ("Customer Service", ["customer service", "customer support", "client service"]),
    ("Sales", ["sales"]),
    ("Marketing", ["marketing", "digital marketing"]),
    ("SEO", ["seo", "search engine optimization"]),
    ("Content Writing", ["content writing", "copywriting"]),
    ("Recruitment", ["recruitment", "recruiting", "talent acquisition"]),
    ("Operations", ["operations management"]),
    ("Communication", ["communication", "communicate", "communication skills", "written communication", "verbal communication"]),
    ("Leadership", ["leadership", "team leadership"]),
    ("Teamwork", ["teamwork", "collaboration", "team player"]),
    ("Problem Solving", ["problem solving", "problem-solving"]),
    ("Time Management", ["time management"]),
    ("Attention to Detail", ["attention to detail", "detail-oriented", "detail oriented"]),
    ("Microsoft Office", ["microsoft office", "ms office", "office suite"]),
    ("Presentation", ["presentation skills", "public speaking"]),
]

PREFERRED_MARKERS = (
    "preferred", "nice to have", "nice-to-have", "good to have", "a plus",
    "is a plus", "bonus", "desirable", "optional", "advantage", "familiarity with",
    "exposure to", "plus:",
)


def _build_patterns():
    compiled = []
    for display, aliases in SKILLS:
        parts = [re.escape(a) for a in sorted(aliases, key=len, reverse=True)]
        pattern = r"(?<![a-z0-9+#.])(?:" + "|".join(parts) + r")(?![a-z0-9+#])"
        compiled.append((display, re.compile(pattern)))
    return compiled


_PATTERNS = _build_patterns()


def _normalize(text):
    text = text.lower()
    text = text.replace("\u2022", " ").replace("\u2013", "-").replace("\u2014", "-")
    text = re.sub(r"[\t\r]+", " ", text)
    return text


def extract_skills(text):
    """Return a sorted list of skill display names found in the text."""
    normalized = _normalize(text)
    found = {display for display, pattern in _PATTERNS if pattern.search(normalized)}
    return sorted(found)


def extract_jd_skills(job_description):
    """Split job description skills into required and preferred.

    A skill is 'preferred' only if every line mentioning it contains a
    preferred-style marker (e.g. 'nice to have', 'is a plus').
    """
    lines = [l for l in re.split(r"[\n.;]+", job_description) if l.strip()]
    required, preferred = set(), set()
    in_preferred_block = False

    for line in lines:
        low = _normalize(line)
        # Headings like "Nice to have:" switch the block on; "Requirements:" switches it off
        if re.match(r"^\s*(nice to have|preferred|bonus|good to have)[^a-z]*$", low) or \
           re.match(r"^\s*(preferred|nice to have|bonus)[a-z ]*:?\s*$", low):
            in_preferred_block = True
            continue
        if re.match(r"^\s*(requirements?|qualifications?|must have|responsibilities|required)[^a-z]*$", low):
            in_preferred_block = False
            continue

        is_pref_line = in_preferred_block or any(m in low for m in PREFERRED_MARKERS)
        for display, pattern in _PATTERNS:
            if pattern.search(low):
                (preferred if is_pref_line else required).add(display)

    preferred -= required
    return sorted(required), sorted(preferred)
