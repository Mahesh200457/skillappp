import streamlit as st
from PyPDF2 import PdfReader
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from typing import List
from io import BytesIO
import os
import time

# ✅ Updated Gemini API credentials
GEMINI_API_KEY = "AIzaSyB-aZF6eOVKgE8TLD_ZCYm_lS6AIzw_1Yw"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"

JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e"
JSEARCH_HOST = "jsearch.p.rapidapi.com"

# 🎨 Enhanced Streamlit page configuration
st.set_page_config(
    page_title="AI Skill Gap Analyzer", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Custom CSS for better design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .skill-badge {
        display: inline-block;
        background: #e8f4fd;
        color: #1f77b4;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
        border: 1px solid #1f77b4;
    }
    
    .missing-skill-badge {
        display: inline-block;
        background: #fff2f2;
        color: #d63384;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
        border: 1px solid #d63384;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .job-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 🎨 Main header with gradient background
st.markdown("""
<div class="main-header">
    <h1>🧠 AI-Powered Skill Gap Analyzer</h1>
    <p>Transform your career with AI-driven insights • Find skill gaps • Get personalized learning paths • Discover job opportunities</p>
</div>
""", unsafe_allow_html=True)

# ----------------------- Enhanced API Call Function ----------------------------
def call_gemini_api(prompt: str, max_tokens: int = 1000) -> str:
    """Enhanced Gemini API call with better error handling and user feedback"""
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        return "❌ Please configure a valid Gemini API key."
    
    headers = {'Content-Type': 'application/json'}
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": max_tokens,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
    }

    try:
        with st.spinner("🤖 AI is processing your request..."):
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers=headers,
                json=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0]:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    st.error("🚨 API response format error. Content not found in response.")
                    return "❌ API response format error"
            else:
                st.error("🚨 No candidates in API response. The request may have been blocked.")
                return "❌ No valid response from AI"
        
        # Handle different error codes with user-friendly messages
        error_messages = {
            400: "Invalid request format. Please try again.",
            401: "API key authentication failed. Please check your API key.",
            403: "API access forbidden. Your API key might be invalid or quota exceeded.",
            404: "API endpoint not found. The service might be temporarily unavailable.",
            429: "Rate limit exceeded. Please wait a moment and try again.",
            500: "Google AI service temporarily unavailable. Please try again later."
        }
        
        error_msg = error_messages.get(response.status_code, f"API error (Status: {response.status_code})")
        st.error(f"🚨 {error_msg}")
        st.error(f"Response: {response.text[:500]}")  # Show first 500 chars of error response
        return f"❌ {error_msg}"
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timeout. Please try again.")
        return "❌ Request timeout. Please try again."
    except requests.exceptions.ConnectionError:
        st.error("🌐 Connection error. Please check your internet connection.")
        return "❌ Connection error. Please check your internet connection."
    except Exception as e:
        st.error(f"🔧 Unexpected error: {str(e)}")
        return f"❌ Unexpected error: {str(e)}"

# ----------------------- API Connection Test ----------------------------
def test_gemini_connection():
    """Test Gemini API with a simple prompt"""
    test_prompt = "Respond with exactly: 'API connection successful'"
    result = call_gemini_api(test_prompt, max_tokens=50)
    return "successful" in result.lower() and not result.startswith("❌")

# ----------------------- Enhanced Resume Processing ----------------------------
def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF with better error handling"""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        if not text.strip():
            st.error("📄 No readable text found in the PDF. Please ensure it's not a scanned image.")
            return ""
        
        return text
    except Exception as e:
        st.error(f"📄 PDF processing error: {str(e)}")
        return ""

def analyze_resume_with_ai(text: str) -> dict:
    """Enhanced resume analysis with structured output"""
    prompt = f"""
    Analyze this resume and extract information in the following JSON-like format:
    
    Name: [Full name of the person]
    Email: [Email address]
    Phone: [Phone number]
    Skills: [List all technical skills, separated by commas]
    Education: [Educational qualifications]
    Experience: [Work experience summary]
    Certifications: [Any certifications mentioned]
    
    Resume Text:
    {text[:4000]}
    
    Please provide clear, structured information for each field. If any field is not found, write "Not specified".
    """
    
    result = call_gemini_api(prompt, max_tokens=1500)
    
    # Parse the result into a structured format
    analysis = {}
    lines = result.split('\n')
    
    for line in lines:
        if ':' in line and not line.startswith('❌'):
            key, value = line.split(':', 1)
            analysis[key.strip()] = value.strip()
    
    return analysis

# ----------------------- Job Market Analysis ----------------------------
def fetch_jobs_from_jsearch(job_role: str, location="India") -> List[dict]:
    """Fetch jobs with better error handling and filtering"""
    url = f"https://{JSEARCH_HOST}/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": JSEARCH_HOST
    }
    params = {
        "query": f"{job_role} {location}",
        "page": "1",
        "num_pages": "1",
        "country": "IN",
        "employment_types": "FULLTIME,PARTTIME,CONTRACTOR"
    }

    try:
        with st.spinner(f"🔍 Searching for {job_role} jobs in {location}..."):
            response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                jobs = data.get("data", [])
                
                # Filter and clean job data
                filtered_jobs = []
                for job in jobs[:10]:  # Limit to top 10 jobs
                    if job.get("job_title") and job.get("employer_name"):
                        filtered_jobs.append(job)
                
                return filtered_jobs
            else:
                st.warning(f"⚠️ Job search API returned status {response.status_code}")
                return []
                
    except Exception as e:
        st.warning(f"⚠️ Job search error: {str(e)}")
        return []

def extract_skills_from_jobs(jobs: List[dict]) -> List[str]:
    """Extract required skills from job descriptions using AI"""
    if not jobs:
        return ["Python", "Communication", "Problem Solving", "Teamwork", "SQL"]  # Default skills
    
    # Combine job descriptions
    job_descriptions = []
    for job in jobs[:5]:
        desc = job.get("job_description", "")
        if desc:
            job_descriptions.append(desc[:800])  # Limit each description
    
    if not job_descriptions:
        return ["Python", "Communication", "Problem Solving", "Teamwork", "SQL"]
    
    combined_text = "\n\n".join(job_descriptions)
    
    prompt = f"""
    Analyze these job descriptions and extract the top 15 most important skills required.
    Focus on both technical skills and soft skills.
    Return only a comma-separated list of skills, nothing else.
    
    Job Descriptions:
    {combined_text[:3000]}
    
    Example format: Python, SQL, Machine Learning, Communication, Leadership
    """
    
    result = call_gemini_api(prompt, max_tokens=300)
    
    if result.startswith("❌"):
        return ["Python", "Communication", "Problem Solving", "Teamwork", "SQL"]
    
    # Parse skills from result
    skills = []
    for skill in result.split(','):
        clean_skill = skill.strip().strip('"').strip("'")
        if clean_skill and len(clean_skill) < 50:
            skills.append(clean_skill)
    
    return skills[:15] if skills else ["Python", "Communication", "Problem Solving", "Teamwork", "SQL"]

# ----------------------- Skill Gap Analysis ----------------------------
def analyze_skill_gaps(user_skills: List[str], required_skills: List[str]) -> dict:
    """Enhanced skill gap analysis with fuzzy matching"""
    if not user_skills:
        return {"matched": [], "missing": required_skills, "match_percentage": 0}
    
    user_skills_lower = [skill.lower().strip() for skill in user_skills if skill.strip()]
    required_skills_clean = [skill.strip() for skill in required_skills if skill.strip()]
    
    matched = []
    missing = []
    
    for req_skill in required_skills_clean:
        req_skill_lower = req_skill.lower()
        is_matched = False
        
        for user_skill in user_skills_lower:
            # Fuzzy matching - check if skills are similar
            if (req_skill_lower in user_skill or 
                user_skill in req_skill_lower or
                any(word in user_skill for word in req_skill_lower.split() if len(word) > 3)):
                matched.append(req_skill)
                is_matched = True
                break
        
        if not is_matched:
            missing.append(req_skill)
    
    match_percentage = (len(matched) / len(required_skills_clean)) * 100 if required_skills_clean else 0
    
    return {
        "matched": matched,
        "missing": missing,
        "match_percentage": round(match_percentage, 1)
    }

# ----------------------- Learning Recommendations ----------------------------
def generate_learning_path(missing_skills: List[str]) -> str:
    """Generate personalized learning recommendations"""
    if not missing_skills:
        return "🎉 Excellent! You have all the required skills for this role. Consider exploring advanced topics to stay ahead!"
    
    skills_text = ", ".join(missing_skills[:8])  # Limit to 8 skills
    
    prompt = f"""
    Create a personalized learning path for these skills: {skills_text}
    
    For each skill, provide:
    1. 📚 One recommended online course (Coursera, Udemy, edX, etc.)
    2. 🆓 One free learning resource (YouTube channel, documentation, tutorial)
    3. 🛠️ One hands-on project idea to practice the skill
    4. ⏱️ Estimated learning time
    
    Format your response with clear headings and emojis for better readability.
    Keep recommendations practical and actionable.
    """
    
    return call_gemini_api(prompt, max_tokens=2500)

# ----------------------- Enhanced PDF Report Generator ----------------------------
def clean_text_for_pdf(text: str) -> str:
    """Clean text to remove problematic characters for PDF generation"""
    # Replace common Unicode characters that cause encoding issues
    replacements = {
        '\u2022': '•',  # Bullet point
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2026': '...',# Ellipsis
        '\u00a0': ' ',  # Non-breaking space
    }
    
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    
    # Remove any remaining non-ASCII characters
    text = ''.join(char if ord(char) < 128 else '?' for char in text)
    
    return text

def create_detailed_report(analysis: dict, role: str, gap_analysis: dict, recommendations: str, jobs: List[dict]) -> BytesIO:
    """Generate a comprehensive PDF report"""
    pdf = FPDF(format='A4')
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(102, 126, 234)  # Blue color
    pdf.cell(0, 15, "AI Skill Gap Analysis Report", ln=True, align='C')
    pdf.ln(10)
    
    # Personal Information
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Personal Information", ln=True)
    pdf.set_font("Arial", "", 11)
    
    name = analysis.get("Name", "Professional")
    email = analysis.get("Email", "Not specified")
    phone = analysis.get("Phone", "Not specified")
    
    # Clean text before adding to PDF
    pdf.cell(0, 8, clean_text_for_pdf(f"Name: {name}"), ln=True)
    pdf.cell(0, 8, clean_text_for_pdf(f"Email: {email}"), ln=True)
    pdf.cell(0, 8, clean_text_for_pdf(f"Phone: {phone}"), ln=True)
    pdf.cell(0, 8, clean_text_for_pdf(f"Target Role: {role}"), ln=True)
    pdf.ln(5)
    
    # Skills Analysis
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Skills Analysis", ln=True)
    pdf.set_font("Arial", "", 11)
    
    pdf.cell(0, 8, f"Skills Match: {gap_analysis['match_percentage']}%", ln=True)
    pdf.cell(0, 8, f"Skills You Have: {len(gap_analysis['matched'])}", ln=True)
    pdf.cell(0, 8, f"Skills to Develop: {len(gap_analysis['missing'])}", ln=True)
    pdf.ln(5)
    
    # Matched Skills
    if gap_analysis['matched']:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Your Matching Skills:", ln=True)
        pdf.set_font("Arial", "", 10)
        for skill in gap_analysis['matched'][:15]:
            pdf.cell(0, 6, clean_text_for_pdf(f"* {skill}"), ln=True)
        pdf.ln(5)
    
    # Skills to Develop
    if gap_analysis['missing']:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Skills to Develop:", ln=True)
        pdf.set_font("Arial", "", 10)
        for skill in gap_analysis['missing'][:15]:
            pdf.cell(0, 6, clean_text_for_pdf(f"- {skill}"), ln=True)
        pdf.ln(5)
    
    # Learning Recommendations
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Learning Recommendations", ln=True)
    pdf.set_font("Arial", "", 9)
    
    # Split recommendations into lines
    clean_recommendations = clean_text_for_pdf(recommendations)
    rec_lines = clean_recommendations.split("\n")
    for line in rec_lines[:50]:  # Limit to prevent overflow
        if line.strip():
            try:
                pdf.multi_cell(0, 5, line.strip())
            except:
                pdf.multi_cell(0, 5, "[Content formatting issue]")
    
    # Job Opportunities
    if jobs:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Current Job Opportunities", ln=True)
        pdf.set_font("Arial", "", 10)
        
        for i, job in enumerate(jobs[:5]):
            pdf.set_font("Arial", "B", 11)
            title = job.get('job_title', 'Job Title')[:50]
            company = job.get('employer_name', 'Company')[:30]
            pdf.cell(0, 8, clean_text_for_pdf(f"{i+1}. {title} at {company}"), ln=True)
            
            pdf.set_font("Arial", "", 9)
            location = f"{job.get('job_city', 'N/A')}, {job.get('job_state', 'N/A')}"
            pdf.cell(0, 6, clean_text_for_pdf(f"Location: {location}"), ln=True)
            pdf.cell(0, 6, clean_text_for_pdf(f"Type: {job.get('job_employment_type', 'N/A')}"), ln=True)
            pdf.ln(3)
    
    # Generate PDF
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# ----------------------- Enhanced Sidebar ----------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-info">
        <h3>🚀 How It Works</h3>
        <ol>
            <li>Upload your PDF resume</li>
            <li>AI analyzes your skills</li>
            <li>Select target job role</li>
            <li>Get skill gap analysis</li>
            <li>Receive learning recommendations</li>
            <li>Explore job opportunities</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Status Check
    st.subheader("🔧 System Status")
    if st.button("🧪 Test AI Connection", use_container_width=True):
        with st.spinner("Testing AI connection..."):
            if test_gemini_connection():
                st.success("✅ AI system is ready!")
            else:
                st.error("❌ AI connection failed")
                st.info("Please check your internet connection and try again.")
    
    st.markdown("---")
    
    # Tips
    st.markdown("""
    <div class="sidebar-info">
        <h4>💡 Tips for Best Results</h4>
        <ul>
            <li>Use a well-formatted PDF resume</li>
            <li>Include all your technical skills</li>
            <li>Mention certifications and projects</li>
            <li>Keep your resume updated</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ----------------------- Main Application Interface ----------------------------

# File Upload Section
st.subheader("📤 Upload Your Resume")
uploaded_file = st.file_uploader(
    "Choose your PDF resume file", 
    type=["pdf"],
    help="Upload a PDF version of your resume for AI analysis"
)

if uploaded_file:
    # Process the uploaded file
    with st.spinner("📄 Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    
    if resume_text:
        st.markdown('<div class="success-box">✅ Resume uploaded and processed successfully!</div>', unsafe_allow_html=True)
        
        # Show text preview
        with st.expander("📄 Resume Text Preview"):
            st.text_area("Extracted Text", resume_text[:2000] + "..." if len(resume_text) > 2000 else resume_text, height=200)
        
        # AI Analysis
        with st.spinner("🤖 AI is analyzing your resume..."):
            analysis = analyze_resume_with_ai(resume_text)
        
        # Display Analysis Results
        st.subheader("📊 Resume Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Personal Information**")
            st.write(f"**Name:** {analysis.get('Name', 'Not specified')}")
            st.write(f"**Email:** {analysis.get('Email', 'Not specified')}")
            st.write(f"**Phone:** {analysis.get('Phone', 'Not specified')}")
        
        with col2:
            st.markdown("**🎓 Education & Experience**")
            st.write(f"**Education:** {analysis.get('Education', 'Not specified')}")
            st.write(f"**Certifications:** {analysis.get('Certifications', 'Not specified')}")
        
        # Skills Display
        skills_text = analysis.get('Skills', '')
        if skills_text and skills_text != 'Not specified':
            user_skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            
            st.markdown("**🛠️ Your Skills**")
            skills_html = ""
            for skill in user_skills:
                skills_html += f'<span class="skill-badge">{skill}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            user_skills = []
            st.warning("⚠️ No skills detected in your resume. Please ensure your skills are clearly listed.")
        
        st.markdown("---")
        
        # Job Role Selection
        st.subheader("🎯 Select Your Target Role")
        
        job_categories = {
            "💻 Software Development": ["Software Developer", "Full Stack Developer", "Frontend Developer", "Backend Developer", "Mobile App Developer"],
            "📊 Data & Analytics": ["Data Analyst", "Data Scientist", "ML Engineer", "AI Engineer", "Business Analyst"],
            "☁️ Cloud & DevOps": ["Cloud Engineer", "DevOps Engineer", "Site Reliability Engineer", "Infrastructure Engineer"],
            "🔒 Cybersecurity": ["Cybersecurity Analyst", "Security Engineer", "Penetration Tester", "Security Consultant"],
            "🎨 Design & UX": ["UI/UX Designer", "Product Designer", "Graphic Designer", "Web Designer"],
            "📈 Management": ["Product Manager", "Project Manager", "Technical Lead", "Engineering Manager"],
            "🧪 Quality & Testing": ["QA Engineer", "Test Automation Engineer", "Quality Analyst", "Performance Tester"]
        }
        
        selected_category = st.selectbox("Choose a category:", list(job_categories.keys()))
        selected_role = st.selectbox("Select specific role:", job_categories[selected_category])
        
        if selected_role:
            # Job Market Analysis
            st.subheader("🔍 Job Market Analysis")
            
            with st.spinner(f"Analyzing job market for {selected_role}..."):
                jobs = fetch_jobs_from_jsearch(selected_role)
                required_skills = extract_skills_from_jobs(jobs)
                gap_analysis = analyze_skill_gaps(user_skills, required_skills)
            
            # Skills Gap Visualization
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "🎯 Skills Match", 
                    f"{gap_analysis['match_percentage']}%",
                    delta=f"{len(gap_analysis['matched'])} skills"
                )
            
            with col2:
                st.metric(
                    "✅ Skills You Have", 
                    len(gap_analysis['matched']),
                    delta="Ready to use"
                )
            
            with col3:
                st.metric(
                    "📚 Skills to Learn", 
                    len(gap_analysis['missing']),
                    delta="Growth opportunities"
                )
            
            # Skills Breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                if gap_analysis['matched']:
                    st.markdown("**✅ Your Matching Skills**")
                    matched_html = ""
                    for skill in gap_analysis['matched']:
                        matched_html += f'<span class="skill-badge">{skill}</span>'
                    st.markdown(matched_html, unsafe_allow_html=True)
                else:
                    st.info("No matching skills found. This is a great opportunity to start learning!")
            
            with col2:
                if gap_analysis['missing']:
                    st.markdown("**📚 Skills to Develop**")
                    missing_html = ""
                    for skill in gap_analysis['missing']:
                        missing_html += f'<span class="missing-skill-badge">{skill}</span>'
                    st.markdown(missing_html, unsafe_allow_html=True)
                else:
                    st.success("🎉 You have all the required skills!")
            
            # Skill Gap Visualization Chart
            if gap_analysis['matched'] or gap_analysis['missing']:
                fig = go.Figure(data=[
                    go.Bar(
                        name='Skills You Have',
                        x=['Skills Analysis'],
                        y=[len(gap_analysis['matched'])],
                        marker_color='#28a745'
                    ),
                    go.Bar(
                        name='Skills to Learn',
                        x=['Skills Analysis'],
                        y=[len(gap_analysis['missing'])],
                        marker_color='#dc3545'
                    )
                ])
                
                fig.update_layout(
                    title='Your Skill Gap Analysis',
                    barmode='stack',
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Learning Recommendations
            st.subheader("📚 Personalized Learning Path")
            
            if gap_analysis['missing']:
                with st.spinner("🎓 Generating personalized learning recommendations..."):
                    recommendations = generate_learning_path(gap_analysis['missing'])
                
                st.markdown(recommendations)
            else:
                st.success("🎉 Congratulations! You have all the required skills. Consider exploring advanced topics or leadership skills to advance your career further.")
                recommendations = "All required skills are present. Focus on advanced topics and leadership development."
            
            # Job Opportunities
            st.subheader("💼 Current Job Opportunities")
            
            if jobs:
                st.info(f"Found {len(jobs)} job opportunities for {selected_role}")
                
                for i, job in enumerate(jobs[:6]):  # Show top 6 jobs
                    with st.expander(f"🏢 {job.get('job_title', 'Job Title')} at {job.get('employer_name', 'Company')}"):
                        job_col1, job_col2 = st.columns([3, 1])
                        
                        with job_col1:
                            st.write(f"**📍 Location:** {job.get('job_city', 'N/A')}, {job.get('job_state', 'N/A')}")
                            st.write(f"**💼 Employment Type:** {job.get('job_employment_type', 'N/A')}")
                            st.write(f"**💰 Salary:** {job.get('job_salary', 'Not specified')}")
                            
                            description = job.get("job_description", "No description available")
                            st.write(f"**📝 Description:** {description[:500]}...")
                        
                        with job_col2:
                            if job.get("job_apply_link"):
                                st.link_button("🚀 Apply Now", job["job_apply_link"], use_container_width=True)
                            
                            posted_date = job.get('job_posted_at_datetime_utc', 'N/A')
                            if posted_date != 'N/A':
                                st.write(f"**📅 Posted:** {posted_date[:10]}")
            else:
                st.warning("⚠️ No job opportunities found at the moment. Try a different role or check back later.")
            
            # Report Generation
            st.subheader("📥 Download Your Comprehensive Report")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate Detailed PDF Report", use_container_width=True):
                    with st.spinner("📊 Creating your personalized report..."):
                        try:
                            report_buffer = create_detailed_report(
                                analysis, selected_role, gap_analysis, recommendations, jobs
                            )
                            
                            st.success("✅ Report generated successfully!")
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=report_buffer,
                                file_name=f"Skill_Gap_Analysis_{selected_role.replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"❌ Error generating report: {str(e)}")
            
            with col2:
                # Summary Statistics
                st.info(f"""
                **📊 Analysis Summary**
                - Skills Analyzed: {len(required_skills)}
                - Match Rate: {gap_analysis['match_percentage']}%
                - Jobs Found: {len(jobs)}
                - Learning Resources: Generated
                """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;'>
    <h4>🔒 Privacy & Security</h4>
    <p>Your resume data is processed securely and never stored permanently on our servers.</p>
    <p>🤖 Powered by Google Gemini AI & JSearch API | 💡 Built with Streamlit</p>
    <p><small>For support or feedback, please ensure your internet connection is stable and API keys are valid.</small></p>
</div>
""", unsafe_allow_html=True)