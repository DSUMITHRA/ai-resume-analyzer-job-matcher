# AI Resume Analyzer and Job Matcher

A Django-based web application that analyzes a candidate's PDF resume
against a selected job description. It compares required skills,
calculates a text-similarity score, and stores analysis results in
MySQL.

## Project Overview

Recruiters and job seekers often need to compare a resume with a job
description. This project provides a simple way to: - Upload a resume in
PDF format. - Select a job from the available job descriptions. -
Extract text from the uploaded PDF. - Compare resume skills with the
job's required skills. - Calculate text similarity using TF-IDF and
cosine similarity. - Save and review analysis results. - View summary
metrics on a dashboard.

## Technologies Used

-   **Python** -- application logic
-   **Django** -- web framework
-   **HTML and CSS** -- user interface
-   **MySQL** -- job descriptions and analysis records
-   **mysql-connector-python** -- Python connection to MySQL
-   **pypdf** -- PDF text extraction
-   **scikit-learn** -- TF-IDF and cosine similarity

> Django's own internal tables may use SQLite in this setup. The
> project-specific `job_descriptions` and `resume_analyses` tables are
> accessed directly through MySQL Connector.

## Main Features

1.  **Resume upload:** Upload a candidate's PDF resume.
2.  **Job selection:** Choose a job description from the jobs stored in
    the database.
3.  **Skill matching:** Compare the job's required skills with the
    extracted resume text.
4.  **Text similarity:** Use TF-IDF vectorization and cosine similarity
    to estimate how similar the resume and job description text are.
5.  **Analysis history:** View previous resume analyses.
6.  **Dashboard:** View the number of resumes analyzed, available jobs,
    average match score, highest match score, and recent analyses.

## How the Analysis Works

### 1. PDF text extraction

The application reads the uploaded PDF using `pypdf` and extracts its
text.

### 2. Required-skill comparison

The required skills are read from the selected job record and compared
with the extracted resume text. The application displays matched and
missing skills.

The skill match score is calculated as:

`Skill Match Score = (Number of Matched Skills / Total Required Skills) × 100`

### 3. Text similarity

The application combines the resume text and job description, converts
them into TF-IDF vectors using `TfidfVectorizer`, and calculates cosine
similarity.

The similarity score is displayed as a percentage.

> These scores are simple matching indicators, not a hiring decision.
> The current skill comparison uses text matching and may not understand
> context, synonyms, or whether a skill is used at a beginner or
> advanced level.

## Database

Database name: `ai_resume_matcher`

### `job_descriptions`

Stores job details, including: - `job_id` - `job_title` -
`company_name` - `description` - `required_skills`

### `resume_analyses`

Stores analysis results, including: - `analysis_id` - `candidate_name` -
`job_id` - `resume_filename` - `match_score` - `matched_skills` -
`missing_skills` - `created_at` - `similarity_score`

The analysis history joins these tables using `job_id` to display the
relevant job title.

## Project Structure

``` text
ai_resume_matcher/
├── manage.py
├── config/
│   └── urls.py
└── resume_analyzer/
    ├── views.py
    └── templates/
        └── resume_analyzer/
            ├── home.html
            ├── history.html
            └── dashboard.html
```

Other project files and folders may be present depending on your local
setup.

## Setup and Run

### 1. Open the project folder

In PowerShell:

``` powershell
cd C:\Users\dsuma\OneDrive\Desktop\ai_resume_matcher
```

### 2. Install dependencies

``` powershell
python -m pip install django mysql-connector-python pypdf scikit-learn
```

### 3. Configure the MySQL password

Set the password in the terminal without placing it directly in the
source code:

``` powershell
$env:MYSQL_PASSWORD="YOUR_MYSQL_PASSWORD"
```

Replace the placeholder with your MySQL password. Set this variable
again when opening a new terminal.

### 4. Prepare the MySQL database

Create the `ai_resume_matcher` database and the `job_descriptions` and
`resume_analyses` tables using the schema used by the project. Add job
descriptions to `job_descriptions` before testing resume analysis.

### 5. Check the Django project

``` powershell
python manage.py check
```

### 6. Start the development server

``` powershell
python manage.py runserver
```

Open these pages in your browser:

-   Home: http://127.0.0.1:8000/
-   Analysis history: http://127.0.0.1:8000/history/
-   Dashboard: http://127.0.0.1:8000/dashboard/

Stop the development server with `Ctrl + C`.

## Current Project Status

The current working version includes PDF upload and text extraction, job
selection, skill matching, TF-IDF similarity calculation, saving results
to MySQL, an analysis history page, and a dashboard.

## Future Enhancements

-   Improve skill matching with synonyms and context-aware methods.
-   Add stronger validation for uploaded files and empty or unreadable
    PDFs.
-   Add user authentication and role-based access.
-   Add charts and filters to the dashboard.
-   Support more resume formats.
-   Add automated tests and deployment configuration.

## Important Notes

-   Do not commit passwords, API keys, or other secrets to GitHub.
-   This is an educational project and its scores should not be used as
    the sole basis for recruitment decisions.
-   The Django development server is intended for local development, not
    production hosting.
