
from pypdf import PdfReader
import mysql.connector

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# STEP 1: Get candidate details
candidate_name = input("Enter candidate name: ")

pdf_path = "resumes/Sumithra_Diddey_Resume_Python_Full_Stack_AI_Resume.pdf"

reader = PdfReader(pdf_path)

resume_text = ""

for page in reader.pages:
    resume_text += page.extract_text() or ""

print("\nResume extracted successfully!")
print("Total characters:", len(resume_text))


# STEP 2: Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dreams@917",
    database="ai_resume_matcher"
)

cursor = connection.cursor()


# STEP 3: Retrieve job details from MySQL
cursor.execute(
    """
    SELECT job_id, job_title, description, required_skills
    FROM job_descriptions
    WHERE job_id = 1
    """
)

job = cursor.fetchone()


if job is not None:

    job_id = job[0]
    job_title = job[1]
    job_description = job[2]
    required_skills_text = job[3]

    print("\nJob Title:", job_title)


    # STEP 4: Find matched and missing skills
    required_skills = required_skills_text.split(",")

    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        skill = skill.strip()

        if skill.lower() in resume_text.lower():
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    print("\n--- Skill Comparison ---")
    print("Required skills:", required_skills)
    print("Matched skills:", matched_skills)
    print("Missing skills:", missing_skills)


    # STEP 5: Calculate skill match percentage
    total_skills = len(required_skills)
    matched_count = len(matched_skills)

    if total_skills > 0:
        match_score = (matched_count / total_skills) * 100
    else:
        match_score = 0

    print("Skill Match Score:", round(match_score, 2), "%")


    # STEP 6: Calculate text similarity using ML
    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    similarity_score = similarity[0][0] * 100

    print("Text Similarity Score:", round(similarity_score, 2), "%")


    # STEP 7: Save analysis results in MySQL
    insert_query = """
    INSERT INTO resume_analyses
    (candidate_name, job_id, resume_filename,
     match_score, similarity_score, matched_skills, missing_skills)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        candidate_name,
        job_id,
        pdf_path.split("/")[-1],
        round(match_score, 2),
        round(similarity_score, 2),
        ", ".join(matched_skills),
        ", ".join(missing_skills)
    )

    cursor.execute(insert_query, values)

    connection.commit()

    print("\nAnalysis results saved successfully in MySQL!")

else:
    print("Job not found!")


# STEP 8: Close database connection
cursor.close()
connection.close()

print("\nProgram completed successfully!")
