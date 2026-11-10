import mysql.connector
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Dreams@917",
    database="ai_resume_matcher"
)
cursor = connection.cursor()

# Get the job description and required skills
cursor.execute(
    "SELECT job_id, job_title, required_skills FROM job_descriptions"
)

jobs = cursor.fetchall()

for job in jobs:
    print("Job ID:", job[0])
    print("Job Title:", job[1])
    print("Required Skills:", job[2])

cursor.close()
connection.close()
