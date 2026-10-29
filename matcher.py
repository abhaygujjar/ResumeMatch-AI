from skill_extractor import extract_skills, extract_jd_skills


def match_skills(resume_text, job_description):
    resume_skills = set(extract_skills(resume_text))
    required, preferred = extract_jd_skills(job_description)
    jd_skills = set(required) | set(preferred)

    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)
    extra = sorted(resume_skills - jd_skills)

    percentage = round(len(matched) / len(jd_skills) * 100, 1) if jd_skills else 0.0

    return {
        "match_percentage": percentage,
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
    }
