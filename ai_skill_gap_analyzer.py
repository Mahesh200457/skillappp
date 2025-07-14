import streamlit as st
from PyPDF2 import PdfReader
import openai
from openai import OpenAI
import requests
import json
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from typing import List
from io import BytesIO
import os

# Secure API key management
def get_api_keys():
    """Get API keys from environment variables or Streamlit secrets"""
    try:
        # Try to get from Streamlit secrets first
        openai_key = st.secrets.get("OPENAI_API_KEY")
        jsearch_key = st.secrets.get("JSEARCH_API_KEY")
    except:
        # Fall back to environment variables
        openai_key = os.getenv("OPENAI_API_KEY")
        jsearch_key = os.getenv("JSEARCH_API_KEY")
    
    return openai_key, jsearch_key

# Get API keys
OPENAI_API_KEY, JSEARCH_API_KEY = get_api_keys()
JSEARCH_HOST = "jsearch.p.rapidapi.com"

# Initialize OpenAI client only if API key is available
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")

st.set_page_config(page_title="AI Skill Gap Analyzer", layout="wide")
st.title("🧠 AI-Based Skill Gap Analyzer Platform")
st.markdown("Upload your resume to find skill gaps, personalized learning resources, and real-time job matches in India.")

# Check if API keys are configured
if not OPENAI_API_KEY:
    st.error("⚠️ OpenAI API key is not configured. Please set up your API key in Streamlit secrets or environment variables.")
    st.markdown("""
    ### How to set up API keys:
    
    **Option 1: Streamlit Secrets (Recommended for deployment)**
    1. Create a `.streamlit/secrets.toml` file in your project directory
    2. Add your keys:
    ```toml
    OPENAI_API_KEY = "your-openai-api-key-here"
    JSEARCH_API_KEY = "your-jsearch-api-key-here"
    ```
    
    **Option 2: Environment Variables**
    1. Set environment variables:
    ```bash
    export OPENAI_API_KEY="your-openai-api-key-here"
    export JSEARCH_API_KEY="your-jsearch-api-key-here"
    ```
    
    **Get your API keys:**
    - OpenAI: https://platform.openai.com/api-keys
    - JSearch: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
    """)
    st.stop()

if not JSEARCH_API_KEY:
    st.warning("⚠️ JSearch API key is not configured. Job search functionality will be limited.")

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

def analyze_resume_gpt(text: str) -> str:
    """Analyze resume using OpenAI GPT"""
    if not client:
        return "OpenAI client not initialized. Please check your API key."
    
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
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except openai.AuthenticationError:
        return "❌ Authentication Error: Invalid OpenAI API key. Please check your API key configuration."
    except openai.RateLimitError:
        return "❌ Rate limit exceeded. Please try again later."
    except Exception as e:
        return f"❌ Error analyzing resume: {str(e)}"

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
    """Extract required skills from job descriptions using GPT"""
    if not client or not jobs:
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
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        extracted = response.choices[0].message.content.strip()
        
        # Try to safely evaluate the response
        try:
            # Remove any markdown formatting
            if "```" in extracted:
                extracted = extracted.split("```")[1].strip()
            if extracted.startswith("python"):
                extracted = extracted[6:].strip()
            
            skills = eval(extracted)
            return skills if isinstance(skills, list) else []
        except:
            # If eval fails, try to parse manually
            import re
            skills = re.findall(r'"([^"]+)"', extracted)
            return skills[:20]  # Limit to 20 skills
            
    except Exception as e:
        st.warning(f"Error extracting skills from jobs: {str(e)}")
        return []

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
    if not client or not missing_skills:
        return "No specific recommendations available."
    
    prompt = f"""
    Recommend specific online learning resources for the following skills. 
    For each skill, provide:
    1. 2-3 specific course recommendations (with platform names like Coursera, Udemy, edX)
    2. 1-2 free resources (YouTube channels, documentation, tutorials)
    3. Practice platforms if applicable
    
    Skills to learn: {', '.join(missing_skills[:10])}  # Limit to 10 skills
    
    Format your response in a clear, organized manner.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

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

# Main application logic
if uploaded_file:
    with st.spinner("Analyzing resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        
        if resume_text:
            analysis_result = analyze_resume_gpt(resume_text)
            
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
