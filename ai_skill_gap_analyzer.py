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

# ✅ Manually set your API keys directly
GEMINI_API_KEY = "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"
JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e"
JSEARCH_HOST = "jsearch.p.rapidapi.com"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"



def call_gemini_api(prompt: str, max_tokens: int = 1000) -> str:
    """Call Gemini API with the given prompt"""
    if not GEMINI_API_KEY:
        return "❌ Gemini API key not configured."
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": max_tokens,
            "stopSequences": []
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
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
        
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0]:
                return result['candidates'][0]['content']['parts'][0]['text']
        
        return "❌ No response generated from Gemini API."
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error calling Gemini API: {str(e)}"
    except KeyError as e:
        return f"❌ Unexpected response format from Gemini API: {str(e)}"
    except Exception as e:
        return f"❌ Error processing Gemini response: {str(e)}"

st.set_page_config(page_title="AI Skill Gap Analyzer", layout="wide")
st.title("🧠 AI-Based Skill Gap Analyzer Platform")
st.markdown("Upload your resume to find skill gaps, personalized learning resources, and real-time job matches in India.")

# Check if API keys are configured


uploaded_file = st.file_uploader("Upload your PDF Resume", type=["pdf"])

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf = PdfReader(uploaded_file)
        text = ""
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def analyze_resume_gemini(text: str) -> str:
    """Analyze resume using Gemini API"""
    prompt = f"""
    Analyze this resume and extract the following information in a structured format:
    
    1. Name: [Extract full name]
    2. Contact Information: [Email, phone, location if available]
    3. Skills: [List all technical and soft skills found, comma-separated]
    4. Education: [Degree, institution, year if available]
    5. Work Experience: [Job titles, companies, duration]
    6. Key Achievements: [Notable accomplishments]
    
    Resume Text:
    {text}
    
    Please format your response clearly with each section on a new line.
    """
    
    return call_gemini_api(prompt, max_tokens=1000)

def fetch_jobs_from_jsearch(job_role: str, location: str = "India") -> List[dict]:
    """Fetch jobs from JSearch API"""
    if not JSEARCH_API_KEY:
        return []
    
    url = f"https://{JSEARCH_HOST}/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST
    }
    params = {
        "query": f"{job_role} {location}",
        "page": "1",
        "num_pages": "1",
        "country": "IN"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        st.warning(f"Error fetching jobs: {str(e)}")
        return []

def extract_required_skills_from_jobs(jobs: List[dict]) -> List[str]:
    """Extract required skills from job descriptions using Gemini"""
    if not jobs:
        return []
    
    job_descriptions = "\n\n".join([
        job.get("job_description", "")[:500] for job in jobs[:5]  # Limit to first 5 jobs and 500 chars each
    ])
    
    prompt = f"""
    From the following job descriptions, extract a list of the most common required technical skills and qualifications.
    Return only a Python list format like: ["skill1", "skill2", "skill3"]
    Focus on technical skills, programming languages, tools, and certifications.
    
    Job Descriptions:
    {job_descriptions}
    """
    
    response = call_gemini_api(prompt, max_tokens=500)
    
    if "❌" in response:
        st.warning(f"Error extracting skills from jobs: {response}")
        return []
    
    try:
        # Remove any markdown formatting
        extracted = response.strip()
        if "```" in extracted:
            extracted = extracted.split("```")[1].strip()
        if extracted.startswith("python"):
            extracted = extracted[6:].strip()
        
        skills = eval(extracted)
        return skills if isinstance(skills, list) else []
    except:
        # If eval fails, try to parse manually
        import re
        skills = re.findall(r'"([^"]+)"', response)
        return skills[:20]  # Limit to 20 skills

def detect_skill_gaps(user_skills: List[str], required_skills: List[str]) -> dict:
    """Detect skill gaps between user skills and required skills"""
    if not user_skills or not required_skills:
        return {"matched": [], "missing": required_skills or []}
    
    # Normalize skills for comparison
    user_skills_norm = [skill.strip().lower() for skill in user_skills if skill.strip()]
    required_skills_norm = [skill.strip().lower() for skill in required_skills if skill.strip()]
    
    # Find exact matches
    matched = []
    missing = []
    
    for req_skill in required_skills_norm:
        found = False
        for user_skill in user_skills_norm:
            if req_skill in user_skill or user_skill in req_skill:
                matched.append(req_skill)
                found = True
                break
        if not found:
            missing.append(req_skill)
    
    return {
        "matched": list(set(matched)),
        "missing": list(set(missing))
    }

def recommend_learning_resources(missing_skills: List[str]) -> str:
    """Recommend learning resources for missing skills"""
    if not missing_skills:
        return "No specific recommendations available."
    
    prompt = f"""
    Recommend specific online learning resources for the following skills. 
    For each skill, provide:
    1. 2-3 specific course recommendations (with platform names like Coursera, Udemy, edX)
    2. 1-2 free resources (YouTube channels, documentation, tutorials)
    3. Practice platforms if applicable
    
    Skills to learn: {', '.join(missing_skills[:10])}
    
    Format your response in a clear, organized manner with proper headings and bullet points.
    """
    
    response = call_gemini_api(prompt, max_tokens=1500)
    return response if "❌" not in response else "Error generating recommendations."

def generate_pdf_report(name: str, role: str, matched: List[str], missing: List[str], recommendations: str) -> BytesIO:
    """Generate PDF report of skill gap analysis"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(0, 10, f"Skill Gap Analysis Report", ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Candidate: {name}", ln=True)
        pdf.cell(0, 10, f"Target Role: {role}", ln=True)
        pdf.ln(10)
        
        # Matched Skills
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 10, f"Matched Skills ({len(matched)}):", ln=True)
        pdf.set_font("Arial", size=10)
        for skill in matched[:15]:  # Limit to prevent overflow
            pdf.cell(0, 6, f"• {skill.title()}", ln=True)
        pdf.ln(5)
        
        # Missing Skills
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 10, f"Skills to Develop ({len(missing)}):", ln=True)
        pdf.set_font("Arial", size=10)
        for skill in missing[:15]:  # Limit to prevent overflow
            pdf.cell(0, 6, f"• {skill.title()}", ln=True)
        pdf.ln(5)
        
        # Recommendations
        pdf.set_font("Arial", "B", size=12)
        pdf.cell(0, 10, "Learning Recommendations:", ln=True)
        pdf.set_font("Arial", size=9)
        
        # Split recommendations into lines and add them
        lines = recommendations.split('\n')
        for line in lines[:30]:  # Limit lines to prevent overflow
            if line.strip():
                pdf.multi_cell(0, 5, line.strip())
        
        # Save to BytesIO
        pdf_output = BytesIO()
        pdf_string = pdf.output(dest='S').encode('latin-1')
        pdf_output.write(pdf_string)
        pdf_output.seek(0)
        return pdf_output
        
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")
        return BytesIO()

# Test Gemini API connection
def test_gemini_connection():
    """Test if Gemini API is working"""
    test_response = call_gemini_api("Hello, please respond with 'API is working correctly!'", max_tokens=50)
    return "API is working correctly!" in test_response

# Show API status
if GEMINI_API_KEY:
    with st.spinner("Testing Gemini API connection..."):
        if test_gemini_connection():
            st.success("✅ Gemini API is connected and working!")
        else:
            st.error("❌ Gemini API connection failed. Please check your API key.")

# Main application logic
if uploaded_file:
    with st.spinner("Analyzing resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        
        if resume_text:
            analysis_result = analyze_resume_gemini(resume_text)
            
            if "❌" in analysis_result:
                st.error(analysis_result)
                st.stop()
            else:
                st.success("Resume analyzed successfully!")
        else:
            st.error("Failed to extract text from PDF. Please try a different file.")
            st.stop()

    # Display resume analysis
    st.markdown("### 📄 Resume Analysis")
    st.markdown(f"```\n{analysis_result}\n```")

    # Job role selection
    job_roles = [
        "Data Analyst", "Software Developer", "AI Engineer", "Web Developer", 
        "Cloud Engineer", "Cybersecurity Analyst", "Full Stack Developer", 
        "DevOps Engineer", "Machine Learning Engineer", "Business Analyst",
        "Product Manager", "UI/UX Designer", "Database Administrator"
    ]
    
    job_role = st.selectbox("🎯 Select your target job role", job_roles)

    if job_role:
        with st.spinner("Fetching job requirements and analyzing skill gaps..."):
            # Fetch jobs
            jobs = fetch_jobs_from_jsearch(job_role)
            
            # Extract user skills from analysis
            user_skills = []
            for line in analysis_result.split('\n'):
                if 'Skills:' in line or 'skills:' in line:
                    skills_text = line.split(':', 1)[-1].strip()
                    user_skills = [s.strip() for s in skills_text.split(',') if s.strip()]
                    break
            
            if not user_skills:
                st.warning("Could not extract skills from resume analysis. Please ensure your resume clearly lists your skills.")
                st.stop()

            # Get required skills and analyze gaps
            required_skills = extract_required_skills_from_jobs(jobs)
            skill_gap = detect_skill_gaps(user_skills, required_skills)
            
            # Generate recommendations
            recommendations = recommend_learning_resources(skill_gap["missing"])

        # Create visualizations
        if skill_gap["matched"] or skill_gap["missing"]:
            skill_df = pd.DataFrame({
                "Skill Type": ["Matched Skills", "Missing Skills"],
                "Count": [len(skill_gap["matched"]), len(skill_gap["missing"])]
            })
            fig1 = px.pie(skill_df, names='Skill Type', values='Count', 
                         title="Skill Match Overview",
                         color_discrete_map={'Matched Skills': '#00CC88', 'Missing Skills': '#FF6B6B'})
            
            if skill_gap["missing"]:
                missing_df = pd.DataFrame({"Skills": skill_gap["missing"][:10]})  # Top 10 missing skills
                fig2 = px.bar(missing_df, x="Skills", 
                             title="Top Missing Skills for Selected Role",
                             color_discrete_sequence=['#FF6B6B'])
                fig2.update_xaxis(tickangle=45)

        # Display results in tabs
        tabs = st.tabs(["📊 Skill Gap Analysis", "📚 Learning Recommendations", "💼 Job Insights", "📥 Download Report"])
        
        with tabs[0]:
            st.subheader("📊 Skill Match Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Matched Skills", len(skill_gap["matched"]))
                if skill_gap["matched"]:
                    st.success("**Your Strengths:**")
                    for skill in skill_gap["matched"][:10]:
                        st.write(f"✅ {skill.title()}")
            
            with col2:
                st.metric("Skills to Develop", len(skill_gap["missing"]))
                if skill_gap["missing"]:
                    st.warning("**Areas for Improvement:**")
                    for skill in skill_gap["missing"][:10]:
                        st.write(f"📈 {skill.title()}")
            
            if skill_gap["matched"] or skill_gap["missing"]:
                st.plotly_chart(fig1, use_container_width=True)
                
                if skill_gap["missing"]:
                    st.plotly_chart(fig2, use_container_width=True)

        with tabs[1]:
            st.subheader("📚 Personalized Learning Recommendations")
            if recommendations and "Error" not in recommendations:
                st.markdown(recommendations)
            else:
                st.info("No specific recommendations available at the moment.")

        with tabs[2]:
            st.subheader("💼 Job Market Insights")
            if jobs:
                st.success(f"Found {len(jobs)} relevant job postings for {job_role}")
                
                # Display sample jobs
                for i, job in enumerate(jobs[:3]):
                    with st.expander(f"📋 {job.get('job_title', 'Job Title')} - {job.get('employer_name', 'Company')}"):
                        st.write(f"**Location:** {job.get('job_city', 'N/A')}, {job.get('job_state', 'N/A')}")
                        st.write(f"**Employment Type:** {job.get('job_employment_type', 'N/A')}")
                        if job.get('job_description'):
                            st.write(f"**Description:** {job.get('job_description', '')[:300]}...")
                        if job.get('job_apply_link'):
                            st.link_button("Apply Now", job.get('job_apply_link'))
            else:
                st.info("No job postings found. This might be due to API limitations or network issues.")

        with tabs[3]:
            st.subheader("📥 Download Your Report")
            
            # Extract name from analysis
            name = "Professional"
            for line in analysis_result.split('\n'):
                if 'Name:' in line:
                    name = line.split(':', 1)[-1].strip()
                    break
            
            if st.button("🔄 Generate PDF Report"):
                with st.spinner("Generating PDF report..."):
                    pdf_report = generate_pdf_report(
                        name=name,
                        role=job_role,
                        matched=skill_gap["matched"],
                        missing=skill_gap["missing"],
                        recommendations=recommendations
                    )
                    
                    if pdf_report.getvalue():
                        st.download_button(
                            label="📄 Download Skill Gap Report",
                            data=pdf_report,
                            file_name=f"Skill_Gap_Report_{job_role.replace(' ', '_')}.pdf",
                            mime="application/pdf"
                        )
                        st.success("✅ PDF report generated successfully!")
                    else:
                        st.error("Failed to generate PDF report.")
else:
    st.info("👆 Please upload your resume (PDF format) to get started!")
    
# Footer
st.markdown("---")
st.markdown("🔒 **Privacy Note:** Your resume is processed securely and is not stored on our servers.")
st.markdown("🤖 **Powered by:** Google Gemini AI")
