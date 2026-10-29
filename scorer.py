"""ATS-style scoring.

No real ATS (Workday, Taleo, Greenhouse, Lever...) publishes its formula, so this
is a transparent estimate built from what ATS systems are known to check:

  1. Keyword / skill match (required skills count more than preferred)  - 45%
  2. Text relevance to the job description (TF-IDF)                      - 15%
  3. Standard resume sections found                                      - 15%
  4. Parse-friendliness (contact info, dates, bullets, length)           - 10%
  5. Impact (action verbs + numbers)                                     - 15%
"""

import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills, extract_jd_skills

WEIGHTS = {"skill": 45, "similarity": 15, "section": 15, "format": 10, "impact": 15}

# ---------- Sections ----------

SECTION_HEADINGS = {
    "Education": {"education", "academic background", "academics", "qualifications",
                  "educational background", "academic qualifications"},
    "Experience": {"experience", "work experience", "professional experience",
                   "employment history", "employment", "work history",
                   "career history", "internships", "internship experience",
                   "relevant experience", "professional background"},
    "Skills": {"skills", "technical skills", "key skills", "core competencies",
               "skills summary", "areas of expertise", "technologies",
               "skills and tools", "tools and technologies", "competencies"},
    "Projects": {"projects", "personal projects", "academic projects", "key projects",
                 "selected projects", "certifications", "certificates",
                 "licenses and certifications", "achievements", "awards"},
    "Summary": {"summary", "professional summary", "profile", "objective",
                "career objective", "about me", "about"},
}

# Words that make a short line count as a heading (e.g. "Technical Skills & Tools")
SECTION_KEYWORDS = {
    "Education": ("education", "academic", "qualification"),
    "Experience": ("experience", "employment", "work history", "internship", "career history"),
    "Skills": ("skills", "competenc", "expertise", "technologies", "tech stack"),
    "Projects": ("project", "certification", "certificate", "achievement", "award"),
}

# Weight of each section in the section score (sums to 100)
SECTION_WEIGHTS = {
    "Contact Info": 15, "Experience": 30, "Education": 20, "Skills": 25, "Projects": 10,
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")
DATE_RE = re.compile(
    r"((jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{4})"
    r"|(\b(19|20)\d{2}\s*[-\u2013to]+\s*((19|20)\d{2}|present|current))"
    r"|(\b\d{1,2}/\d{4}\b)",
    re.IGNORECASE,
)
BULLET_RE = re.compile(r"^\s*[\u2022\u25cf\u25aa\u2023\-*\u00b7o]\s+")

ACTION_VERBS = (
    "achiev", "analy", "architect", "audit", "automat", "balanc", "build", "built",
    "collaborat", "conduct", "configur", "coordinat", "creat", "deliver", "deploy",
    "design", "develop", "direct", "drove", "engineer", "establish", "evaluat",
    "execut", "generat", "implement", "improv", "increas", "initiat", "integrat",
    "launch", "lead", "led", "maintain", "manag", "migrat", "monitor", "negotiat",
    "optimi", "organi", "perform", "plan", "prepar", "present", "process", "reconcil",
    "record", "reduc", "research", "resolv", "review", "run", "schedul", "streamlin",
    "supervis", "test", "train", "verif", "wrote", "write", "work", "communicat",
    "respons",
)


def _clean_heading(line):
    return re.sub(r"[^a-z& ]", "", line.lower()).strip()


def detect_sections(text):
    """Return {section_name: 0 or 100} for every section we look for."""
    found = {name: 0 for name in SECTION_WEIGHTS}
    found["Contact Info"] = 100 if (EMAIL_RE.search(text) and PHONE_RE.search(text)) else 0

    for line in text.splitlines():
        clean = _clean_heading(line)
        words = clean.split()
        # A heading is a short line (max 6 words) that contains a section keyword
        if not words or len(words) > 6:
            continue
        for section, keywords in SECTION_KEYWORDS.items():
            if clean in SECTION_HEADINGS.get(section, ()) or any(k in clean for k in keywords):
                found[section] = 100

    # Fallback: detect sections from content when no clear heading was found
    low = text.lower()
    if not found["Education"] and re.search(
            r"\b(b\.?\s?tech|bachelor|master|m\.?\s?tech|b\.?sc|m\.?sc|b\.?e\b|mba|university|college|cgpa|gpa)\b", low):
        found["Education"] = 100
    if not found["Experience"] and re.search(r"\b(intern|internship|worked as|employment|work experience)\b", low) \
            and len(DATE_RE.findall(text)) >= 1:
        found["Experience"] = 100
    if not found["Skills"] and re.search(r"\b(skills|technologies|tools)\s*[:\-]", low):
        found["Skills"] = 100
    if not found["Projects"] and re.search(r"\b(projects?|certifications?)\s*[:\-]", low):
        found["Projects"] = 100
    return found


def _section_score(details):
    return sum(SECTION_WEIGHTS[s] for s, v in details.items() if v == 100)


# ---------- Parse-friendliness ----------

def _format_check(text):
    lines = [l for l in text.splitlines() if l.strip()]
    words = text.split()
    issues = []
    passed = 0
    total = 6

    if EMAIL_RE.search(text):
        passed += 1
    else:
        issues.append("Add a clear email address at the top of your resume.")

    if PHONE_RE.search(text):
        passed += 1
    else:
        issues.append("Add a phone number at the top of your resume.")

    if len(DATE_RE.findall(text)) >= 2:
        passed += 1
    else:
        issues.append("Add dates (for example 'Jun 2024 - Aug 2024') to each job or education entry.")

    if sum(1 for l in lines if BULLET_RE.match(l)) >= 3:
        passed += 1
    else:
        issues.append("Use simple bullet points to describe your work. They are easier for ATS to read.")

    if 250 <= len(words) <= 1000:
        passed += 1
    elif len(words) < 250:
        issues.append("Your resume looks very short. Add more detail about your work and projects.")
    else:
        issues.append("Your resume is very long. Try to keep it to 1-2 pages.")

    non_ascii = sum(1 for ch in text if ord(ch) > 127 and ch not in "\u2022\u2013\u2014\u2019\u201c\u201d\u25cf\u00b7")
    if len(text) and non_ascii / len(text) < 0.02:
        passed += 1
    else:
        issues.append("Some characters may not be read correctly by ATS. Avoid special symbols and icons.")

    return passed / total * 100, issues


# ---------- Impact ----------

def _impact_check(text):
    lines = [BULLET_RE.sub("", l).strip() for l in text.splitlines() if l.strip()]
    candidate = [l for l in lines if len(l.split()) >= 4]

    verb_lines = 0
    for l in candidate:
        first = re.sub(r"[^a-z]", "", l.split()[0].lower())
        if first.startswith(ACTION_VERBS):
            verb_lines += 1

    number_lines = sum(1 for l in candidate if re.search(r"\d+\s*%|\$\s*\d|\u20b9\s*\d|\b\d{2,}\b|\b\d+x\b", l)
                       and not DATE_RE.search(l))

    verb_part = min(verb_lines / 5, 1.0)
    number_part = min(number_lines / 3, 1.0)
    return (verb_part * 0.5 + number_part * 0.5) * 100, verb_lines, number_lines


# ---------- Text similarity ----------

def _text_similarity(resume, jd):
    try:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        matrix = vec.fit_transform([resume, jd])
        raw = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except ValueError:
        return 0.0
    # Real resume/JD pairs rarely go above ~0.45, so scale to make 0.45 = 100%
    return min(raw / 0.45, 1.0) * 100


# ---------- Main ----------

def calculate_score(resume_text, job_description):
    resume_skills = set(extract_skills(resume_text))
    required, preferred = extract_jd_skills(job_description)

    matched_req = [s for s in required if s in resume_skills]
    missing_req = [s for s in required if s not in resume_skills]
    matched_pref = [s for s in preferred if s in resume_skills]
    missing_pref = [s for s in preferred if s not in resume_skills]

    total_weight = len(required) + 0.5 * len(preferred)
    got_weight = len(matched_req) + 0.5 * len(matched_pref)
    skill_score = (got_weight / total_weight * 100) if total_weight else None

    similarity = _text_similarity(resume_text, job_description)
    section_details = detect_sections(resume_text)
    section_score = _section_score(section_details)
    format_score, format_issues = _format_check(resume_text)
    impact_score, verb_lines, number_lines = _impact_check(resume_text)

    components = {
        "skill": skill_score,
        "similarity": similarity,
        "section": section_score,
        "format": format_score,
        "impact": impact_score,
    }
    used = {k: v for k, v in components.items() if v is not None}
    overall = sum(WEIGHTS[k] * v for k, v in used.items()) / sum(WEIGHTS[k] for k in used)

    # ---- Suggestions ----
    suggestions = []
    if missing_req:
        suggestions.append(
            "Add these REQUIRED skills if you really have them: " + ", ".join(missing_req) + "."
        )
    if missing_pref:
        suggestions.append(
            "These skills are 'nice to have' in the job: " + ", ".join(missing_pref) + "."
        )
    for name, v in section_details.items():
        if v == 0:
            if name == "Contact Info":
                suggestions.append("Put your email and phone number at the top of the resume.")
            else:
                suggestions.append(f"Add a clear '{name}' section with a standard heading.")
    suggestions.extend(format_issues)
    if verb_lines < 5:
        suggestions.append("Start more bullet points with action words like Built, Led, Reduced, Managed.")
    if number_lines < 3:
        suggestions.append("Add numbers to your results (for example 'reduced errors by 20%').")
    if similarity < 40:
        suggestions.append("Use words from the job description naturally in your summary and bullet points.")
    if skill_score is None:
        suggestions.append("No known skills were found in the job description, so the skill score is not used.")

    return {
        "overall_score": round(overall, 1),
        "skill_score": round(skill_score, 1) if skill_score is not None else 0.0,
        "text_similarity": round(similarity, 1),
        "section_score": round(section_score, 1),
        "section_details": section_details,
        "format_score": round(format_score, 1),
        "impact_score": round(impact_score, 1),
        "matched_skills": matched_req + matched_pref,
        "missing_skills": missing_req + missing_pref,
        "required_missing": missing_req,
        "preferred_missing": missing_pref,
        "extra_skills": sorted(resume_skills - set(required) - set(preferred)),
        "suggestions": suggestions,
    }
