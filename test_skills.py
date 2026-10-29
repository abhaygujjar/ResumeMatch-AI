from skill_extractor import extract_skills

sample_text = """
I have experience with Python, SQL, Machine Learning,
Pandas, NumPy, TensorFlow, GitHub and FastAPI.
"""

skills = extract_skills(sample_text)

print("\nExtracted Skills:")
print("-----------------")

for skill in skills:
    print(f"- {skill}")
