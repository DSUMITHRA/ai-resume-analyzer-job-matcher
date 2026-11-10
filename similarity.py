

from pypdf import PdfReader
import mysql.connector

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# STEP 1: Read resume PDF
pdf_path = "resumes/Sumithra_Diddey_Resume_Python_Full_Stack_AI_Resume.pdf"

reader = PdfReader(pdf_path)

resume_text = ""

for page in reader.pages:
    resume_text += page.extract_text() or ""

print("Resume extracted successfully!")


# STEP 2: Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dreams@917",
    database="ai_resume_matcher"
)

cursor = connection.cursor()


# STEP 3: Get job description from MySQL
cursor.execute(
    "SELECT description FROM job_descriptions WHERE job_id = 1"
)

job = cursor.fetchone()


# STEP 4: Compare resume and job description
if job is not None and job[0]:

    job_description = job[0]

    documents = [resume_text, job_description]

    # Convert text into numerical values
    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    print("TF-IDF conversion completed!")

    # Calculate cosine similarity
    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    # Convert similarity into percentage
    similarity_score = similarity[0][0] * 100

    print("\n--- AI Resume Similarity Result ---")
    print("Job Title: Python Developer")
    print("Similarity Score:", round(similarity_score, 2), "%")

else:
    print("Job description not found!")


# STEP 5: Close database connection
cursor.close()
connection.close()

print("\nProgram completed successfully!")
