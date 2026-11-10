
from django.shortcuts import render
from pypdf import PdfReader
from io import BytesIO
import mysql.connector
import os
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    password = os.environ.get("MYSQL_PASSWORD")

    if not password:
        raise ValueError("MySQL password is not configured.")

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
        database="ai_resume_matcher"
    )

    return connection


# ==========================================
# HOME PAGE AND RESUME ANALYSIS
# ==========================================

def home(request):

    connection = None
    cursor = None
    jobs = []

    try:

        # STEP 1: Connect to MySQL

        connection = get_db_connection()
        cursor = connection.cursor()

        # STEP 2: Fetch available jobs

        cursor.execute("""
            SELECT job_id, job_title, company_name
            FROM job_descriptions
            ORDER BY job_id
        """)

        jobs = cursor.fetchall()

        # STEP 3: Handle resume upload

        if request.method == "POST":

            candidate_name = (
                request.POST.get("candidate_name") or ""
            ).strip()

            uploaded_resume = request.FILES.get("resume")
            selected_job_id = request.POST.get("job_id")

            # STEP 4: Validate candidate name

            if not candidate_name:

                return render(request, "resume_analyzer/home.html", {
                    "error": "Please enter candidate name.",
                    "jobs": jobs
                })

            # Allow only English letters and spaces

            if not re.fullmatch(r"[A-Za-z ]+", candidate_name):

                return render(request, "resume_analyzer/home.html", {
                    "error": "Name should contain only letters and spaces.",
                    "jobs": jobs
                })

            # STEP 5: Validate selected job

            if not selected_job_id:

                return render(request, "resume_analyzer/home.html", {
                    "error": "Please select a job.",
                    "jobs": jobs
                })

            # STEP 6: Validate uploaded file

            if not uploaded_resume:

                return render(request, "resume_analyzer/home.html", {
                    "error": "Please upload a PDF resume.",
                    "jobs": jobs
                })

            if not uploaded_resume.name.lower().endswith(".pdf"):

                return render(request, "resume_analyzer/home.html", {
                    "error": "Only PDF files are allowed.",
                    "jobs": jobs
                })

            if uploaded_resume.size == 0:

                return render(request, "resume_analyzer/home.html", {
                    "error": "The uploaded file is empty.",
                    "jobs": jobs
                })

            if uploaded_resume.size > 5 * 1024 * 1024:

                return render(request, "resume_analyzer/home.html", {
                    "error": "File size must be less than 5 MB.",
                    "jobs": jobs
                })

            # STEP 7: Extract PDF text

            try:

                pdf = PdfReader(BytesIO(uploaded_resume.read()))

                if pdf.is_encrypted:
                    raise ValueError(
                        "Password-protected PDFs are not supported."
                    )

                resume_text = ""

                for page in pdf.pages:
                    resume_text += page.extract_text() or ""

            except ValueError:
                raise

            except Exception:
                raise ValueError(
                    "Unable to read this PDF. Please upload a valid PDF."
                )

            print("Resume extracted:", len(resume_text), "characters")

            if not resume_text.strip():

                raise ValueError(
                    "No readable text found in the PDF. "
                    "Please upload a text-based PDF."
                )

            # STEP 8: Fetch selected job details

            cursor.execute("""
                SELECT
                    job_id,
                    job_title,
                    required_skills,
                    description
                FROM job_descriptions
                WHERE job_id = %s
            """, (selected_job_id,))

            job = cursor.fetchone()

            if job is None:
                raise ValueError("Selected job not found.")

            job_id, job_title, required_skills, job_description = job

            # STEP 9: Compare required skills

            required_skills_list = [
                skill.strip()
                for skill in (required_skills or "").split(",")
                if skill.strip()
            ]

            matched_skills = []
            missing_skills = []

            resume_lower = resume_text.lower()

            for skill in required_skills_list:

                skill_pattern = (
                    r"(?<!\w)"
                    + re.escape(skill.lower())
                    + r"(?!\w)"
                )

                if re.search(skill_pattern, resume_lower):
                    matched_skills.append(skill)
                else:
                    missing_skills.append(skill)

            # Calculate skill match score

            if required_skills_list:

                match_score = (
                    len(matched_skills) / len(required_skills_list)
                ) * 100

            else:

                match_score = 0

            # STEP 10: Calculate TF-IDF similarity

            job_description = job_description or ""
            similarity_score = 0

            if job_description.strip():

                try:

                    documents = [
                        resume_text,
                        job_description
                    ]

                    vectorizer = TfidfVectorizer()

                    tfidf_matrix = vectorizer.fit_transform(documents)

                    similarity = cosine_similarity(
                        tfidf_matrix[0:1],
                        tfidf_matrix[1:2]
                    )

                    similarity_score = similarity[0][0] * 100

                except ValueError:

                    similarity_score = 0

            # STEP 11: Save results in MySQL

            cursor.execute("""
                INSERT INTO resume_analyses
                (
                    candidate_name,
                    job_id,
                    resume_filename,
                    match_score,
                    matched_skills,
                    missing_skills,
                    similarity_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                candidate_name,
                job_id,
                uploaded_resume.name,
                round(match_score, 2),
                ", ".join(matched_skills),
                ", ".join(missing_skills),
                round(similarity_score, 2)
            ))

            connection.commit()

            # STEP 12: Display results

            return render(
                request,
                "resume_analyzer/home.html",
                {
                    "message": "Resume analysis completed successfully!",
                    "candidate_name": candidate_name,
                    "job_title": job_title,
                    "match_score": round(match_score, 2),
                    "similarity_score": round(similarity_score, 2),
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                    "jobs": jobs
                }
            )

        # Display homepage

        return render(
            request,
            "resume_analyzer/home.html",
            {"jobs": jobs}
        )

    except ValueError as e:

        if connection and connection.is_connected():
            connection.rollback()

        return render(
            request,
            "resume_analyzer/home.html",
            {
                "error": str(e),
                "jobs": jobs
            }
        )

    except Exception as e:

        if connection and connection.is_connected():
            connection.rollback()

        print("HOME ERROR:", str(e))

        return render(
            request,
            "resume_analyzer/home.html",
            {
                "error": "Something went wrong. Please try again.",
                "jobs": jobs
            }
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================
# ANALYSIS HISTORY
# ==========================================

def history(request):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                ra.analysis_id,
                ra.candidate_name,
                jd.job_title,
                ra.resume_filename,
                ra.match_score,
                ra.similarity_score,
                ra.matched_skills,
                ra.missing_skills,
                ra.created_at
            FROM resume_analyses ra
            LEFT JOIN job_descriptions jd
            ON ra.job_id = jd.job_id
            ORDER BY ra.created_at DESC
        """)

        records = cursor.fetchall()

        return render(
            request,
            "resume_analyzer/history.html",
            {"records": records}
        )

    except Exception as e:

        print("HISTORY ERROR:", str(e))

        return render(
            request,
            "resume_analyzer/history.html",
            {
                "error": "Unable to load analysis history."
            }
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================
# DASHBOARD
# ==========================================

def dashboard(request):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # Total resumes analyzed

        cursor.execute("""
            SELECT COUNT(*)
            FROM resume_analyses
        """)

        total_resumes = cursor.fetchone()[0]

        # Total available jobs

        cursor.execute("""
            SELECT COUNT(*)
            FROM job_descriptions
        """)

        total_jobs = cursor.fetchone()[0]

        # Average match score

        cursor.execute("""
            SELECT AVG(match_score)
            FROM resume_analyses
        """)

        average_score = cursor.fetchone()[0] or 0

        # Highest match score

        cursor.execute("""
            SELECT MAX(match_score)
            FROM resume_analyses
        """)

        highest_score = cursor.fetchone()[0] or 0

        # Recent analyses

        cursor.execute("""
            SELECT
                ra.candidate_name,
                jd.job_title,
                ra.match_score,
                ra.similarity_score,
                ra.created_at
            FROM resume_analyses ra
            LEFT JOIN job_descriptions jd
            ON ra.job_id = jd.job_id
            ORDER BY ra.created_at DESC
            LIMIT 5
        """)

        recent_records = cursor.fetchall()

        return render(
            request,
            "resume_analyzer/dashboard.html",
            {
                "total_resumes": total_resumes,
                "total_jobs": total_jobs,
                "average_score": round(float(average_score), 2),
                "highest_score": round(float(highest_score), 2),
                "recent_records": recent_records
            }
        )

    except Exception as e:

        print("DASHBOARD ERROR:", str(e))

        return render(
            request,
            "resume_analyzer/dashboard.html",
            {
                "error": "Unable to load dashboard data."
            }
        )

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
