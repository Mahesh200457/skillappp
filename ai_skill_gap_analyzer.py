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

# ✅ Gemini API credentials - Replace with your actual API key
GEMINI_API_KEY = "AIzaSyBSG3_c6wAW4q4XkF9PjYKmpd33NxV7GZ4"  # Replace this with a fresh API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e"
JSEARCH_HOST = "jsearch.p.rapidapi.com"

# Set Streamlit page config
st.set_page_config(page_title="AI Skill Gap Analyzer", layout="wide")
st.title("🧠 AI-Based Skill Gap Analyzer Platform")
st.markdown("Upload your resume to find skill gaps, personalized learning resources, and real-time job matches in India.")

# ----------------------- Improved API Call Function ----------------------------
def call_gemini_api(prompt: str, max_tokens: int = 1000) -> str:
    """
    Improved Gemini API call with better error handling
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        return "❌ Please set a valid Gemini API key in the code."
    
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
            "temperature": 0.7,
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
        
        # Debug information
        st.write(f"API Response Status: {response.status_code}")
        
        if response.status_code == 400:
            error_detail = response.json()
            st.error(f"API Error 400: {error_detail}")
            return f"❌ Bad Request: {error_detail.get('error', {}).get('message', 'Unknown error')}"
        elif response.status_code == 403:
            st.error("API Error 403: API key might be invalid or quota exceeded")
            return "❌ API key invalid or quota exceeded. Please check your Gemini API key."
        elif response.status_code == 429:
            st.error("API Error 429: Rate limit exceeded")
            return "❌ Rate limit exceeded. Please try again later."
        
        response.raise_for_status()
        result = response.json()
        
        # Check if response has the expected structure
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0]:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                st.error(f"Unexpected API response structure: {result}")
                return "❌ Unexpected API response structure"
        else:
            st.error(f"No candidates in response: {result}")
            return "❌ No response generated"
            
    except requests.exceptions.Timeout:
        return "❌ Request timeout. Please try again."
    except requests.exceptions.ConnectionError:
        return "❌ Connection error. Please check your internet connection."
    except Exception as e:
        st.error(f"Detailed error: {str(e)}")
        return f"❌ Gemini API error: {str(e)}"

# ----------------------- Simple API Test ----------------------------
def test_gemini_connection():
    """Test if Gemini API is working with a simple prompt"""
    result = call_gemini_api("Hello! Please respond with exactly: 'API is working correctly'", max_tokens=50)
    st.write(f"Test Response: {result}")
    return "API is working correctly" in result or "working" in result.lower()

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
    Please analyze this resume and extract the following information in a clear format:
    
    1. Name: [Extract the person's name]
    2. Contact: [Extract email and phone number]
    3. Skills: [List all technical and professional skills mentioned]
    4. Education: [List educational qualifications]
    5. Work Experience: [Summarize work experience]
    6. Achievements: [List key achievements or certifications]
    
    Resume Text:
    {text[:3000]}  # Limit text to avoid token limits
    
    Please format your response clearly with each section labeled.
    """
    return call_gemini_api(prompt, max_tokens=1500)

# ----------------------- Fetch Jobs from JSearch ----------------------------
def fetch_jobs_from_jsearch(job_role: str, location="India") -> List[dict]:
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
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("data", [])
        else:
            st.warning(f"Job API returned status {res.status_code}")
            return []
    except Exception as e:
        st.warning(f"Job fetch error: {e}")
        return []

# ----------------------- Extract Job Skills using Gemini ----------------------------
def extract_required_skills_from_jobs(jobs: List[dict]) -> List[str]:
    if not jobs:
        return []

    # Combine job descriptions
    job_descriptions = []
    for job in jobs[:5]:  # Limit to first 5 jobs
        desc = job.get("job_description", "")
        if desc:
            job_descriptions.append(desc[:500])  # Limit each description
    
    if not job_descriptions:
        return []
    
    combined_descriptions = "\n\n".join(job_descriptions)
    
    prompt = f"""
    Analyze these job descriptions and extract the top 10 most commonly required technical skills.
    Return ONLY a Python list format like: ["Python", "SQL", "Machine Learning", ...]
    
    Job Descriptions:
    {combined_descriptions[:2000]}  # Limit total text
    
    Return only the list, no other text.
    """
    
    result = call_gemini_api(prompt, max_tokens=300)
    
    try:
        # Try to extract list from response
        if "[" in result and "]" in result:
            list_part = result[result.find("["):result.find("]")+1]
            skills = eval(list_part)
            return skills if isinstance(skills, list) else []
        else:
            # Fallback: extract skills manually
            lines = result.split('\n')
            skills = []
            for line in lines:
                if line.strip() and not line.startswith('❌'):
                    # Remove quotes and clean up
                    skill = line.strip().strip('"').strip("'").strip('-').strip()
                    if skill and len(skill) < 50:  # Reasonable skill name length
                        skills.append(skill)
            return skills[:10]  # Limit to 10 skills
    except:
        return ["Python", "SQL", "Communication", "Problem Solving", "Teamwork"]  # Fallback skills

# ----------------------- Skill Gap Logic ----------------------------
def detect_skill_gaps(user_skills: List[str], required_skills: List[str]) -> dict:
    user_skills_lower = [skill.lower().strip() for skill in user_skills if skill.strip()]
    required_skills_lower = [skill.lower().strip() for skill in required_skills if skill.strip()]
    
    matched = []
    missing = []
    
    for req_skill in required_skills:
        req_skill_lower = req_skill.lower().strip()
        is_matched = False
        
        for user_skill in user_skills_lower:
            if req_skill_lower in user_skill or user_skill in req_skill_lower:
                matched.append(req_skill)
                is_matched = True
                break
        
        if not is_matched:
            missing.append(req_skill)
    
    return {"matched": matched, "missing": missing}

# ----------------------- Learning Recommendations ----------------------------
def recommend_learning_resources(missing_skills: List[str]) -> str:
    if not missing_skills:
        return "🎉 Great! You have all the required skills for this role."
    
    skills_text = ", ".join(missing_skills[:5])  # Limit to 5 skills
    
    prompt = f"""
    Provide learning recommendations for these skills: {skills_text}
    
    For each skill, suggest:
    1. One popular paid course (Coursera, Udemy, etc.)
    2. One free resource (YouTube, documentation, etc.)
    3. One practice platform or project idea
    
    Format your response clearly with skill names as headers.
    Keep recommendations practical and specific.
    """
    return call_gemini_api(prompt, max_tokens=2000)

# ----------------------- PDF Report Generator ----------------------------
def generate_pdf_report(name, role, matched, missing, recommendations) -> BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Skill Gap Analysis Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Target Role: {role}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Matched Skills ({len(matched)}):", ln=True)
    pdf.set_font("Arial", "", 11)
    for skill in matched[:10]:  # Limit to prevent overflow
        pdf.cell(0, 8, f"✓ {skill}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Skills to Develop ({len(missing)}):", ln=True)
    pdf.set_font("Arial", "", 11)
    for skill in missing[:10]:  # Limit to prevent overflow
        pdf.cell(0, 8, f"• {skill}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Learning Recommendations:", ln=True)
    pdf.set_font("Arial", "", 10)
    
    # Split recommendations into lines and add to PDF
    rec_lines = recommendations.split("\n")
    for line in rec_lines[:40]:  # Limit lines to prevent overflow
        if line.strip():
            try:
                pdf.multi_cell(0, 6, line.encode('latin-1', 'replace').decode('latin-1'))
            except:
                pdf.multi_cell(0, 6, "Content encoding issue")

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ----------------------- Main Interface ----------------------------

# API Key Configuration Section
st.sidebar.header("🔧 Configuration")
st.sidebar.info("If you're getting API errors, replace the API key in the code with a fresh one from Google AI Studio.")

# Test Gemini API connection
st.subheader("🔍 API Status Check")
if st.button("Test Gemini API Connection"):
    with st.spinner("Testing Gemini API..."):
        if test_gemini_connection():
            st.success("✅ Gemini API is working correctly!")
        else:
            st.error("❌ Gemini API connection failed. Please check your API key.")
            st.info("To fix this:\n1. Go to https://makersuite.google.com/app/apikey\n2. Create a new API key\n3. Replace the GEMINI_API_KEY in the code")

st.markdown("---")

# File upload section
uploaded_file = st.file_uploader("📤 Upload your PDF Resume", type=["pdf"])

if uploaded_file:
    with st.spinner("⏳ Processing resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        
        if resume_text:
            st.success("✅ Resume uploaded successfully!")
            
            # Show extracted text preview
            with st.expander("📄 Extracted Resume Text (Preview)"):
                st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
            
            # Analyze resume
            with st.spinner("🤖 Analyzing resume with AI..."):
                analysis = analyze_resume_gemini(resume_text)
            
            st.subheader("📊 Resume Analysis")
            st.markdown(analysis)
            
            # Job role selection
            job_roles = [
                "Data Analyst", "Software Developer", "AI Engineer", "Full Stack Developer",
                "Cloud Engineer", "Cybersecurity Analyst", "ML Engineer", "UI/UX Designer",
                "DevOps Engineer", "Product Manager", "Business Analyst", "QA Engineer"
            ]
            selected_role = st.selectbox("🎯 Select your target job role:", job_roles)
            
            if selected_role:
                with st.spinner("🔍 Analyzing job market and skill gaps..."):
                    # Fetch jobs
                    jobs = fetch_jobs_from_jsearch(selected_role)
                    
                    # Extract user skills from analysis
                    user_skills = []
                    analysis_lines = analysis.split('\n')
                    for line in analysis_lines:
                        if "Skills:" in line or "skills:" in line:
                            skills_text = line.split(":", 1)[-1]
                            user_skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]
                            break
                    
                    # If no skills found in analysis, try alternative extraction
                    if not user_skills:
                        skill_prompt = f"Extract only the technical skills from this resume analysis as a comma-separated list:\n{analysis}"
                        skills_response = call_gemini_api(skill_prompt, max_tokens=200)
                        user_skills = [skill.strip() for skill in skills_response.split(",") if skill.strip() and not skill.startswith("❌")]
                    
                    # Get required skills from jobs
                    required_skills = extract_required_skills_from_jobs(jobs)
                    
                    # Analyze skill gaps
                    gap = detect_skill_gaps(user_skills, required_skills)
                    
                    # Get learning recommendations
                    recommendations = recommend_learning_resources(gap["missing"])
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("✅ Skills You Have", len(gap["matched"]))
                    if gap["matched"]:
                        st.write("**Your Matching Skills:**")
                        for skill in gap["matched"]:
                            st.write(f"✓ {skill}")
                
                with col2:
                    st.metric("📚 Skills to Learn", len(gap["missing"]))
                    if gap["missing"]:
                        st.write("**Skills to Develop:**")
                        for skill in gap["missing"]:
                            st.write(f"• {skill}")
                
                # Skill distribution chart
                if gap["matched"] or gap["missing"]:
                    chart_data = pd.DataFrame({
                        "Category": ["Skills You Have", "Skills to Learn"],
                        "Count": [len(gap["matched"]), len(gap["missing"])]
                    })
                    fig = px.pie(chart_data, names="Category", values="Count", 
                               title="Your Skill Gap Analysis",
                               color_discrete_map={"Skills You Have": "#00CC96", "Skills to Learn": "#FF6B6B"})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Learning recommendations
                st.subheader("📚 Personalized Learning Path")
                st.markdown(recommendations)
                
                # Job opportunities
                st.subheader("💼 Current Job Opportunities")
                if jobs:
                    for i, job in enumerate(jobs[:5]):  # Show top 5 jobs
                        with st.expander(f"🏢 {job.get('job_title', 'Job Title')} at {job.get('employer_name', 'Company')}"):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**Location:** {job.get('job_city', 'N/A')}, {job.get('job_state', 'N/A')}")
                                st.write(f"**Employment Type:** {job.get('job_employment_type', 'N/A')}")
                                description = job.get("job_description", "No description available")
                                st.write(f"**Description:** {description[:400]}...")
                            with col2:
                                if job.get("job_apply_link"):
                                    st.link_button("🔗 Apply Now", job["job_apply_link"])
                                st.write(f"**Posted:** {job.get('job_posted_at_datetime_utc', 'N/A')[:10]}")
                else:
                    st.info("No current job openings found. Try a different role or check back later.")
                
                # Generate report
                st.subheader("📥 Download Your Report")
                
                # Extract name from analysis
                candidate_name = "Professional"
                for line in analysis.split('\n'):
                    if "Name:" in line:
                        name_part = line.split(":", 1)[-1].strip()
                        if name_part and not name_part.startswith("❌"):
                            candidate_name = name_part
                        break
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📄 Generate PDF Report"):
                        with st.spinner("Generating report..."):
                            try:
                                report = generate_pdf_report(
                                    candidate_name, 
                                    selected_role, 
                                    gap["matched"], 
                                    gap["missing"], 
                                    recommendations
                                )
                                st.success("✅ Report generated successfully!")
                                st.download_button(
                                    "⬇️ Download PDF Report", 
                                    data=report, 
                                    file_name=f"Skill_Gap_Report_{selected_role.replace(' ', '_')}.pdf", 
                                    mime="application/pdf"
                                )
                            except Exception as e:
                                st.error(f"Error generating report: {e}")
        else:
            st.error("❌ Could not extract text from the PDF. Please ensure it's a valid PDF file.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🔒 Your data is processed securely and never stored permanently<br>
    🤖 Powered by Google Gemini AI & JSearch API<br>
    💡 For support, check your API keys and internet connection
</div>
""", unsafe_allow_html=True)