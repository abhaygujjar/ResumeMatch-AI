from scorer import calculate_score


resume = """
Computer Science student with experience in Python,
SQL, Pandas, Machine Learning and Git.
Built projects using data analysis and Python.
"""

job_description = """
We are looking for an AI/ML intern with Python,
SQL, Machine Learning, TensorFlow and Docker skills.
Experience with data analysis is preferred.
"""


results = calculate_score(resume, job_description)

print("\n===== RESUMEMATCH AI SCORE =====")

print(f"\nOverall Match: {results['overall_score']}%")
print(f"Skill Match: {results['skill_score']}%")
print(f"Text Similarity: {results['text_similarity']}%")

print("\nMatched Skills:")
for skill in results["matched_skills"]:
    print(f"  + {skill}")

print("\nMissing Skills:")
for skill in results["missing_skills"]:
    print(f"  - {skill}")
    