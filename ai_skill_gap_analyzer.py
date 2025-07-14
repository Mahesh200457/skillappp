import streamlit as st
from PyPDF2 import PdfReader
import openai
import requests
import json
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from typing import List
from io import BytesIO

# ❗️ Manually setting your API keys (temporary)
openai.api_key = "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"
JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e"
JSEARCH_HOST = "jsearch.p.rapidapi.com"

st.set_page_config(page_title="AI Skill Gap Analyzer", layout="wide")
st.title("🧠 AI-Based Skill Gap Analyzer Platform")
st.markdown("Upload your resume to find skill gaps, personalized learning resources, and real-time job matches in India.")

uploaded_file = st.file_uploader("Upload your PDF Resume", type=["pdf"])

def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def analyze_resume_gpt(text: str) -> str:
    prompt = f"""
    Analyze this resume and extract:
    1. Skills (comma-separated)
    2. Education details
    3. Work experience
    Resume Text:
    {text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def fetch_jobs_from_jsearch(job_role: str, location: str = "India") -> List[dict]:
    url = f"https://{JSEARCH_HOST}/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST
    }
    params = {"query": job_role, "page": "1", "num_pages": "1", "country": "IN"}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("data", [])

def extract_required_skills_from_jobs(jobs: List[dict]) -> List[str]:
    job_descriptions = "\n\n".join(job.get("job_description", "") for job in jobs)
    prompt = f"""
    From the following job descriptions, extract a unique list of most common required skills for this role.
    Return them as a Python list (no explanation needed).

    Job Descriptions:
    {job_descriptions[:3000]}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    extracted = response.choices[0].message.content.strip()
    try:
        return eval(extracted)
    except:
        return []

def detect_skill_gaps(user_skills: List[str], required_skills: List[str]) -> dict:
    user_skills = [skill.strip().lower() for skill in user_skills]
    required_skills = [skill.strip().lower() for skill in required_skills]
    matched = list(set(user_skills).intersection(required_skills))
    missing = list(set(required_skills) - set(user_skills))
    return {"matched": matched, "missing": missing}

def recommend_learning_resources(missing_skills: List[str]) -> str:
    prompt = f"""
    Recommend top online learning resources for the following missing skills. 
    Include a mix of free/paid courses, books, and practice platforms with platform names.

    Skills: {', '.join(missing_skills)}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_pdf_report(name: str, role: str, matched: List[str], missing: List[str], recommendations: str) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title("Skill Gap Analysis Report")

    pdf.cell(200, 10, txt=f"Skill Gap Report for {name}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Target Role: {role}", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", size=12)
    pdf.cell(200, 10, "Matched Skills:", ln=True)
    pdf.set_font("Arial", size=11)
    for skill in matched:
        pdf.cell(200, 8, f"- {skill}", ln=True)

    pdf.set_font("Arial", "B", size=12)
    pdf.cell(200, 10, "Missing Skills:", ln=True)
    pdf.set_font("Arial", size=11)
    for skill in missing:
        pdf.cell(200, 8, f"- {skill}", ln=True)

    pdf.set_font("Arial", "B", size=12)
    pdf.cell(200, 10, "Recommendations:", ln=True)
    pdf.set_font("Arial", size=11)
    for line in recommendations.split("\n"):
        pdf.multi_cell(0, 8, line)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

if uploaded_file:
    with st.spinner("Analyzing resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        analysis_result = analyze_resume_gpt(resume_text)
        st.success("Resume analyzed successfully!")

    st.markdown("### Resume Summary")
    st.markdown(f"```\n{analysis_result}\n```")

    job_roles = [
        "Data Analyst", "Software Developer", "AI Engineer", "Web Developer", 
        "Cloud Engineer", "Cybersecurity Analyst", "Full Stack Developer", 
        "DevOps Engineer", "ML Engineer", "Business Analyst"
    ]
    job_role = st.selectbox("Select your target job role", job_roles)

    if job_role:
        jobs = fetch_jobs_from_jsearch(job_role)
        user_skills = []
        for line in analysis_result.splitlines():
            if "Skills" in line:
                user_skills = [s.strip() for s in line.split(":")[-1].split(",")]
                break

        if user_skills:
            required_skills = extract_required_skills_from_jobs(jobs)
            skill_gap = detect_skill_gaps(user_skills, required_skills)
            recommendations = recommend_learning_resources(skill_gap["missing"])

            skill_df = pd.DataFrame({
                "Skill Type": ["Matched Skills", "Missing Skills"],
                "Count": [len(skill_gap["matched"]), len(skill_gap["missing"])]
            })
            fig1 = px.pie(skill_df, names='Skill Type', values='Count', title="Skill Match Overview")

            missing_df = pd.DataFrame({"Missing Skills": skill_gap["missing"]})
            fig2 = px.bar(missing_df, x="Missing Skills", title="Missing Skills for Selected Role")

            tabs = st.tabs(["📄 Resume Analysis", "📊 Skill Gap Insights", "📚 Recommendations", "📥 Download Report"])
            with tabs[0]:
                st.subheader("Resume Details Extracted")
                st.markdown(f"```\n{analysis_result}\n```")

            with tabs[1]:
                st.subheader("Skill Match Overview")
                st.plotly_chart(fig1)
                st.subheader("Missing Skills Bar Chart")
                st.plotly_chart(fig2)

            with tabs[2]:
                st.subheader("AI-Powered Personalized Recommendations")
                st.markdown(recommendations)

            with tabs[3]:
                name_guess = analysis_result.split("\n")[0].split(":")[-1].strip() if ":" in analysis_result.split("\n")[0] else "Candidate"
                report = generate_pdf_report(name=name_guess, role=job_role, matched=skill_gap["matched"], missing=skill_gap["missing"], recommendations=recommendations)
                st.download_button("📄 Download PDF Report", data=report, file_name="Skill_Gap_Report.pdf")
        else:
            st.warning("Could not extract skills from resume. Please try a clearer format.")
