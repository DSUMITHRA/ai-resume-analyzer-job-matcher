
import mysql.connector

# STEP 1: Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dreams@917",
    database="ai_resume_matcher"
)

cursor = connection.cursor()

# STEP 2: Retrieve saved analysis records
cursor.execute("""
    SELECT
        analysis_id,
        candidate_name,
        job_id,
        match_score,
        similarity_score,
        matched_skills,
        missing_skills
    FROM resume_analyses
""")

# STEP 3: Get all records
records = cursor.fetchall()

# STEP 4: Display analysis history
print("\n--- Resume Analysis History ---")

for record in records:
    print("\nAnalysis ID:", record[0])
    print("Candidate Name:", record[1])
    print("Job ID:", record[2])
    print("Skill Match Score:", record[3], "%")
    print("Text Similarity Score:", record[4], "%")
    print("Matched Skills:", record[5])
    print("Missing Skills:", record[6])

# STEP 5: Close connection
cursor.close()
connection.close()

print("\nAnalysis history retrieved successfully!")
