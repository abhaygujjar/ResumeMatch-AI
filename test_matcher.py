from matcher import match_skills


resume = """
I have experience in Python, SQL, Pandas,
Machine Learning and Git.
"""

job_description = """
We need a candidate skilled in Python, SQL,
Machine Learning, TensorFlow and Docker.
"""


results = match_skills(resume, job_description)

print("\n===== RESUMEMATCH AI =====")

print(f"\nSkill Match: {results['match_percentage']}%")

print("\nMatched Skills:")
for skill in results["matched_skills"]:
    print(f"  + {skill}")

print("\nMissing Skills:")
for skill in results["missing_skills"]:
    print(f"  - {skill}")

print("\nAdditional Resume Skills:")
for skill in results["extra_skills"]:
    print(f"  + {skill}")