import streamlit as st
import openai
import PyPDF2
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import json
import io
import time
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="AI Skill Gap Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern, student-friendly design
st.markdown("""
<style>
    /* Global Styles */
    .main {
        padding: 0rem 1rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header Styles */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 1rem;
    }
    
    /* Card Styles */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-content {
        color: #666;
        line-height: 1.6;
    }
    
    /* Job Card Styles */
    .job-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .job-card:hover {
        transform: translateY(-3px);
    }
    
    .job-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .job-company {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .job-location {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-bottom: 1rem;
    }
    
    /* Learning Resource Card */
    .learning-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Skill Card */
    .skill-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        font-weight: 500;
        display: inline-block;
        min-width: 120px;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Chatbot Styles */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        height: 500px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        text-align: center;
        font-weight: 600;
    }
    
    .chatbot-messages {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
        max-height: 350px;
    }
    
    .chat-message {
        margin: 0.5rem 0;
        padding: 0.75rem;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background: #e3f2fd;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background: #f5f5f5;
        margin-right: auto;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        
        .chatbot-container {
            width: 300px;
            height: 400px;
            bottom: 10px;
            right: 10px;
        }
        
        .feature-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'user_skills' not in st.session_state:
    st.session_state.user_skills = []
if 'job_recommendations' not in st.session_state:
    st.session_state.job_recommendations = []

# API Configuration
def setup_apis():
    """Setup API keys and configurations"""
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
    
    if 'jsearch_api_key' not in st.session_state:
        st.session_state.jsearch_api_key = st.secrets.get("JSEARCH_API_KEY", "")

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def analyze_resume_with_ai(resume_text, api_key):
    """Use AI to extract skills, email, and education from resume"""
    try:
        openai.api_key = api_key
        
        prompt = f"""
        Analyze the following resume and extract:
        1. Email address
        2. Skills (technical and soft skills)
        3. Education details
        4. Experience level
        5. Career interests/domain
        
        Resume text:
        {resume_text}
        
        Please return the response in JSON format with keys: email, skills, education, experience_level, career_domain
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    
    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")
        return None

def get_skill_gap_analysis(user_skills, career_domain, api_key):
    """Get AI-powered skill gap analysis and recommendations"""
    try:
        openai.api_key = api_key
        
        prompt = f"""
        Based on the user's current skills: {user_skills}
        And their career domain: {career_domain}
        
        Provide:
        1. Skill gap analysis
        2. Top 5 skills they should learn
        3. Learning resources (courses, books, projects) for each skill
        4. Industry trends in their domain
        
        Return as JSON with keys: gap_analysis, recommended_skills, learning_resources, industry_trends
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    
    except Exception as e:
        st.error(f"Error getting skill gap analysis: {str(e)}")
        return None

def search_jobs_jsearch(skills, location="Remote", api_key=""):
    """Search for entry-level jobs using JSearch API"""
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        
        query = f"entry level {' '.join(skills[:3])} jobs"
        
        querystring = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "date_posted": "month"
        }
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        
        if response.status_code == 200:
            return response.json().get('data', [])
        else:
            return []
    
    except Exception as e:
        st.error(f"Error fetching jobs: {str(e)}")
        return []

def create_skill_visualization(user_skills, recommended_skills):
    """Create interactive skill visualization"""
    # Skill distribution pie chart
    skill_categories = {
        'Technical': 0,
        'Soft Skills': 0,
        'Domain Specific': 0,
        'Tools & Frameworks': 0
    }
    
    # Simple categorization (in real app, use AI for better categorization)
    technical_keywords = ['python', 'javascript', 'java', 'sql', 'html', 'css', 'react', 'node']
    soft_keywords = ['communication', 'leadership', 'teamwork', 'problem solving', 'creativity']
    
    for skill in user_skills:
        skill_lower = skill.lower()
        if any(keyword in skill_lower for keyword in technical_keywords):
            skill_categories['Technical'] += 1
        elif any(keyword in skill_lower for keyword in soft_keywords):
            skill_categories['Soft Skills'] += 1
        else:
            skill_categories['Domain Specific'] += 1
    
    fig_pie = px.pie(
        values=list(skill_categories.values()),
        names=list(skill_categories.keys()),
        title="Your Current Skill Distribution",
        color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#f5576c']
    )
    
    # Skill gap bar chart
    gap_data = {
        'Skills': recommended_skills[:5],
        'Priority': [5, 4, 4, 3, 3]  # Mock priority scores
    }
    
    fig_bar = px.bar(
        x=gap_data['Skills'],
        y=gap_data['Priority'],
        title="Top Skills to Learn (Priority Score)",
        color=gap_data['Priority'],
        color_continuous_scale='Viridis'
    )
    
    return fig_pie, fig_bar

def chatbot_response(user_message, api_key):
    """Generate chatbot response for career guidance"""
    try:
        openai.api_key = api_key
        
        system_prompt = """
        You are a career guidance chatbot for students and entry-level job seekers. 
        Provide helpful, encouraging, and practical advice about:
        - Skill development
        - Career planning
        - Job search strategies
        - Learning resources
        - Interview preparation
        
        Keep responses concise, friendly, and actionable.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return "I'm sorry, I'm having trouble responding right now. Please try again later."

# Main App Layout
def main():
    setup_apis()
    
    # Header Section
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">🎯 AI Skill Gap Analyzer</h1>
        <p class="subtitle">Discover your potential • Bridge the gap • Land your dream job</p>
        <p class="card-content">Empowering students and entry-level professionals with AI-driven career insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key Setup
    with st.expander("🔑 API Configuration", expanded=not st.session_state.openai_api_key):
        col1, col2 = st.columns(2)
        with col1:
            openai_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key)
            if openai_key:
                st.session_state.openai_api_key = openai_key
        
        with col2:
            jsearch_key = st.text_input("JSearch API Key (Optional)", type="password", value=st.session_state.jsearch_api_key)
            if jsearch_key:
                st.session_state.jsearch_api_key = jsearch_key
    
    if not st.session_state.openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        return
    
    # Main Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input Section
        st.markdown("""
        <div class="feature-card">
            <h2 class="card-title">📄 Upload Your Resume or Enter Skills</h2>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📤 Upload Resume", "✍️ Manual Entry"])
        
        with tab1:
            uploaded_file = st.file_uploader("Choose your resume (PDF)", type="pdf")
            
            if uploaded_file and st.button("🔍 Analyze Resume"):
                with st.spinner("Analyzing your resume..."):
                    resume_text = extract_text_from_pdf(uploaded_file)
                    if resume_text:
                        analysis = analyze_resume_with_ai(resume_text, st.session_state.openai_api_key)
                        if analysis:
                            st.session_state.user_skills = analysis.get('skills', [])
                            st.session_state.career_domain = analysis.get('career_domain', 'General')
                            st.session_state.analysis_complete = True
                            st.success("Resume analyzed successfully!")
        
        with tab2:
            skills_input = st.text_area("Enter your skills (comma-separated)", 
                                      placeholder="Python, JavaScript, Communication, Problem Solving...")
            career_domain = st.selectbox("Select your career domain", 
                                       ["Software Development", "Data Science", "Digital Marketing", 
                                        "Design", "Business Analysis", "Other"])
            
            if st.button("🚀 Analyze Skills"):
                if skills_input:
                    st.session_state.user_skills = [skill.strip() for skill in skills_input.split(',')]
                    st.session_state.career_domain = career_domain
                    st.session_state.analysis_complete = True
                    st.success("Skills analyzed successfully!")
        
        # Results Section
        if st.session_state.analysis_complete and st.session_state.user_skills:
            # Current Skills Display
            st.markdown("""
            <div class="feature-card">
                <h2 class="card-title">🎯 Your Current Skills</h2>
            </div>
            """, unsafe_allow_html=True)
            
            skills_html = ""
            for skill in st.session_state.user_skills:
                skills_html += f'<span class="skill-card">{skill}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
            
            # Get AI Analysis
            with st.spinner("Getting personalized recommendations..."):
                gap_analysis = get_skill_gap_analysis(
                    st.session_state.user_skills, 
                    st.session_state.career_domain, 
                    st.session_state.openai_api_key
                )
            
            if gap_analysis:
                # Skill Gap Analysis
                st.markdown("""
                <div class="feature-card">
                    <h2 class="card-title">📊 Skill Gap Analysis</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(gap_analysis.get('gap_analysis', 'Analysis not available'))
                
                # Recommended Skills
                recommended_skills = gap_analysis.get('recommended_skills', [])
                if recommended_skills:
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">🎓 Skills to Learn</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, skill in enumerate(recommended_skills[:5], 1):
                        st.markdown(f"""
                        <div class="learning-card">
                            <h3>{i}. {skill}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Learning Resources
                learning_resources = gap_analysis.get('learning_resources', {})
                if learning_resources:
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">📚 Learning Resources</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for skill, resources in learning_resources.items():
                        with st.expander(f"Resources for {skill}"):
                            if isinstance(resources, list):
                                for resource in resources:
                                    st.write(f"• {resource}")
                            else:
                                st.write(resources)
                
                # Visualizations
                st.markdown("""
                <div class="feature-card">
                    <h2 class="card-title">📈 Skill Analytics</h2>
                </div>
                """, unsafe_allow_html=True)
                
                fig_pie, fig_bar = create_skill_visualization(st.session_state.user_skills, recommended_skills)
                
                col_viz1, col_viz2 = st.columns(2)
                with col_viz1:
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col_viz2:
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Job Recommendations
                if st.session_state.jsearch_api_key:
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">💼 Job Opportunities</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🔍 Find Jobs"):
                        with st.spinner("Searching for relevant jobs..."):
                            jobs = search_jobs_jsearch(st.session_state.user_skills, api_key=st.session_state.jsearch_api_key)
                            
                            if jobs:
                                for job in jobs[:5]:
                                    st.markdown(f"""
                                    <div class="job-card">
                                        <div class="job-title">{job.get('job_title', 'N/A')}</div>
                                        <div class="job-company">{job.get('employer_name', 'N/A')}</div>
                                        <div class="job-location">{job.get('job_city', 'N/A')}, {job.get('job_country', 'N/A')}</div>
                                        <a href="{job.get('job_apply_link', '#')}" target="_blank" style="color: white; text-decoration: none;">
                                            🔗 Apply Now
                                        </a>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No jobs found. Try updating your skills or check your API key.")
    
    with col2:
        # Chatbot Section
        st.markdown("""
        <div class="feature-card">
            <h2 class="card-title">🤖 Career Assistant</h2>
            <p class="card-content">Ask me anything about career development, skills, or job search!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat Interface
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages
            for message in st.session_state.chat_messages[-5:]:  # Show last 5 messages
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>Assistant:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Ask a question...", key="chat_input")
        
        if st.button("Send") and user_input:
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Get bot response
            bot_response = chatbot_response(user_input, st.session_state.openai_api_key)
            st.session_state.chat_messages.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update chat
            st.rerun()
        
        # Quick action buttons
        st.markdown("### Quick Questions")
        if st.button("💡 How to improve my resume?"):
            response = chatbot_response("How can I improve my resume for entry-level positions?", st.session_state.openai_api_key)
            st.session_state.chat_messages.append({"role": "user", "content": "How to improve my resume?"})
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("🎯 Interview preparation tips"):
            response = chatbot_response("Give me tips for preparing for entry-level job interviews.", st.session_state.openai_api_key)
            st.session_state.chat_messages.append({"role": "user", "content": "Interview preparation tips"})
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("📈 Skill development roadmap"):
            response = chatbot_response("Create a skill development roadmap for entry-level professionals.", st.session_state.openai_api_key)
            st.session_state.chat_messages.append({"role": "user", "content": "Skill development roadmap"})
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()
