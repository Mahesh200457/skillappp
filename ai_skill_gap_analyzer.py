import streamlit as st
from PyPDF2 import PdfReader
import requests
import json
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from typing import List
from io import BytesIO
import os

# ✅ Gemini and JSearch API credentials
GEMINI_API_KEY = "AIzaSyBSG3_c6wAW4q4XkF9PjYKmpd33NxV7GZ4"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"


JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e"
JSEARCH_HOST = "jsearch.p.rapidapi.com"

# Set Streamlit page config
st.set_page_config(page_title="AI Skill Gap Analyzer", layout="wide")
st.title("🧠 AI-Based Skill Gap Analyzer Platform")
st.markdown("Upload your resume to find skill gaps, personalized learning resources, and real-time job matches in India.")

# ----------------------- API Call Function ----------------------------
def call_gemini_api(prompt: str, max_tokens: int = 1000) -> str:
    if not GEMINI_API_KEY:
        return "❌ Gemini API key not configured."
    
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": max_tokens
        }
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ Gemini API error: {str(e)}"

# ----------------------- API Test on Load ----------------------------
def test_gemini_connection():
    result = call_gemini_api("Say: API is working!", max_tokens=20)
    return "API is working" in result

# ----------------------- Resume Text Extractor ----------------------------
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        return text
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return ""

# ----------------------- Resume Analyzer ----------------------------
def analyze_resume_gemini(text: str) -> str:
    prompt = f"""
    Extract this resume data:
    - Name
    - Contact (Email, Phone)
    - Skills
    - Education
    - Work Experience
    - Achievements
    Resume Text:
    {text}
    """
    return call_gemini_api(prompt)

# ----------------------- Fetch Jobs from JSearch ----------------------------
def fetch_jobs_from_jsearch(job_role: str, location="India") -> List[dict]:
    url = f"https://{JSEARCH_HOST}/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST
    }
    params = {"query": f"{job_role} {location}", "page": "1", "num_pages": "1", "country": "IN"}

    try:
        res = requests.get(url, headers=headers, params=params)
        return res.json().get("data", [])
    except Exception as e:
        st.warning(f"Job fetch error: {e}")
        return []

# ----------------------- Extract Job Skills using Gemini ----------------------------
def extract_required_skills_from_jobs(jobs: List[dict]) -> List[str]:
    if not jobs:
        return []

    sample_jobs = "\n".join(job.get("job_description", "")[:500] for job in jobs[:5])
    prompt = f"""
    Extract top 10 skills from these job descriptions (Python list format only):\n{sample_jobs}
    """
    result = call_gemini_api(prompt)

    try:
        skills = eval(result.strip().split("```")[-1])  # Fallback if markdown
        return skills if isinstance(skills, list) else []
    except:
        return []

# ----------------------- Skill Gap Logic ----------------------------
def detect_skill_gaps(user_skills: List[str], required_skills: List[str]) -> dict:
    matched = [skill for skill in required_skills if skill.lower() in map(str.lower, user_skills)]
    missing = [skill for skill in required_skills if skill.lower() not in map(str.lower, user_skills)]
    return {"matched": matched, "missing": missing}

# ----------------------- Learning Recommendations ----------------------------
def recommend_learning_resources(missing_skills: List[str]) -> str:
    if not missing_skills:
        return "No recommendations needed."
    
    prompt = f"""
    Suggest online resources for learning these skills:
    {', '.join(missing_skills)}
    For each, include: 1-2 paid courses, free resources, and practice platforms.
    """
    return call_gemini_api(prompt, max_tokens=1500)

# ----------------------- PDF Report Generator ----------------------------
def generate_pdf_report(name, role, matched, missing, recommendations) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Skill Gap Analysis Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Role: {role}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Matched Skills ({len(matched)}):", ln=True)
    pdf.set_font("Arial", "", 11)
    for skill in matched:
        pdf.cell(0, 8, f"- {skill}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Skills to Learn ({len(missing)}):", ln=True)
    pdf.set_font("Arial", "", 11)
    for skill in missing:
        pdf.cell(0, 8, f"- {skill}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Recommendations:", ln=True)
    pdf.set_font("Arial", "", 10)
    for line in recommendations.split("\n")[:30]:
        pdf.multi_cell(0, 6, line)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ----------------------- Interface Logic ----------------------------

# Test Gemini on load
if GEMINI_API_KEY:
    with st.spinner("Testing Gemini API..."):
        if test_gemini_connection():
            st.success("✅ Gemini API is connected!")
        else:
            st.error("❌ Invalid Gemini API key or error in connection.")

uploaded_file = st.file_uploader("📤 Upload your PDF Resume", type=["pdf"])

if uploaded_file:
    with st.spinner("⏳ Reading resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        analysis = analyze_resume_gemini(resume_text)
        st.success("✅ Resume analysis complete!")

    st.subheader("📄 Resume Insights")
    st.code(analysis, language="markdown")

    job_roles = [
        "Data Analyst", "Software Developer", "AI Engineer", "Full Stack Developer",
        "Cloud Engineer", "Cybersecurity Analyst", "ML Engineer", "UI/UX Designer"
    ]
    selected_role = st.selectbox("🎯 Choose target job role", job_roles)

    if selected_role:
        with st.spinner("🔍 Fetching jobs & analyzing gaps..."):
            jobs = fetch_jobs_from_jsearch(selected_role)

            # Extract user skills from Gemini response
            user_skills = []
            for line in analysis.splitlines():
                if "Skills:" in line:
                    user_skills = [x.strip() for x in line.split(":", 1)[-1].split(",")]
                    break

            required_skills = extract_required_skills_from_jobs(jobs)
            gap = detect_skill_gaps(user_skills, required_skills)
            recommendations = recommend_learning_resources(gap["missing"])

        # Visuals
        st.subheader("📊 Skill Gap Overview")
        st.metric("✅ Matched", len(gap["matched"]))
        st.metric("🚧 Missing", len(gap["missing"]))

        chart_data = pd.DataFrame({
            "Type": ["Matched", "Missing"],
            "Count": [len(gap["matched"]), len(gap["missing"])]
        })
        st.plotly_chart(px.pie(chart_data, names="Type", values="Count", title="Skill Distribution"), use_container_width=True)

        st.subheader("📚 Learning Resources")
        st.markdown(recommendations)

        st.subheader("💼 Job Market Snapshot")
        if jobs:
            for job in jobs[:3]:
                with st.expander(f"{job.get('job_title')} @ {job.get('employer_name')}"):
                    st.write(job.get("job_description", "")[:300])
                    if job.get("job_apply_link"):
                        st.link_button("Apply Now", job["job_apply_link"])
        else:
            st.warning("No jobs found for this role.")

        st.subheader("📥 Download Report")
        candidate_name = "Professional"
        for line in analysis.splitlines():
            if "Name:" in line:
                candidate_name = line.split(":")[-1].strip()
                break

        if st.button("📄 Generate PDF Report"):
            report = generate_pdf_report(candidate_name, selected_role, gap["matched"], gap["missing"], recommendations)
            st.download_button("⬇ Download Report", data=report, file_name="Skill_Gap_Report.pdf", mime="application/pdf")

# Footer
st.markdown("---")
st.markdown("🔒 Your data is never stored. | 🤖 Powered by Google Gemini + JSearch APIs")
