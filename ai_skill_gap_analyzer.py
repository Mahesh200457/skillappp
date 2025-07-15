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
import google.generativeai as genai

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
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
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
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #666;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .description {
        font-size: 1.1rem;
        color: #777;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Card Styles */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .card-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .card-content {
        color: #666;
        line-height: 1.7;
        font-size: 1.1rem;
    }
    
    /* Skill Cards */
    .skill-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin: 0.5rem;
        text-align: center;
        font-weight: 500;
        display: inline-block;
        min-width: 120px;
        box-shadow: 0 4px 15px rgba(67, 233, 123, 0.3);
        transition: all 0.3s ease;
    }
    
    .skill-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(67, 233, 123, 0.4);
    }
    
    .recommended-skill-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(240, 147, 251, 0.3);
        transition: all 0.3s ease;
    }
    
    .recommended-skill-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.4);
    }
    
    .skill-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .skill-priority {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.8rem;
    }
    
    /* Job Cards */
    .job-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border-radius: 16px;
        padding: 1.8rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .job-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
    }
    
    .job-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(79, 172, 254, 0.4);
    }
    
    .job-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .job-company {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .job-location {
        font-size: 0.95rem;
        opacity: 0.8;
        margin-bottom: 1rem;
    }
    
    .job-skills {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 1rem;
        font-style: italic;
    }
    
    .apply-btn {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    .apply-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-2px);
    }
    
    /* Learning Resource Cards */
    .learning-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .learning-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .resource-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .resource-list {
        list-style: none;
        padding: 0;
    }
    
    .resource-item {
        padding: 0.4rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .resource-item:last-child {
        border-bottom: none;
    }
    
    /* Chatbot Styles */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 380px;
        height: 550px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        text-align: center;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .chatbot-messages {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
        max-height: 380px;
    }
    
    .chat-message {
        margin: 0.8rem 0;
        padding: 1rem;
        border-radius: 12px;
        max-width: 85%;
        line-height: 1.5;
        font-size: 0.95rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background: #f8f9fa;
        color: #333;
        margin-right: auto;
        border: 1px solid #e9ecef;
    }
    
    .quick-actions {
        padding: 1rem;
        border-top: 1px solid #e9ecef;
    }
    
    .quick-btn {
        background: linear-gradient(135deg, #43e97b, #38f9d7);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(67, 233, 123, 0.3);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* File Uploader Styles */
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(102, 126, 234, 0.5);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: rgba(102, 126, 234, 0.8);
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .chatbot-container {
            width: 320px;
            height: 450px;
            bottom: 10px;
            right: 10px;
        }
        
        .feature-card {
            margin: 1rem 0;
            padding: 1.5rem;
        }
        
        .header-container {
            padding: 2rem 1.5rem;
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'user_skills' not in st.session_state:
        st.session_state.user_skills = []
    if 'recommended_skills' not in st.session_state:
        st.session_state.recommended_skills = []
    if 'job_recommendations' not in st.session_state:
        st.session_state.job_recommendations = []
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'learning_resources' not in st.session_state:
        st.session_state.learning_resources = {}
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ""
    if 'jsearch_api_key' not in st.session_state:
        st.session_state.jsearch_api_key = ""

# PDF Text Extraction
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

# AI Analysis Functions
def analyze_resume_with_openai(resume_text, api_key):
    """Use OpenAI to extract information from resume"""
    try:
        openai.api_key = api_key
        
        prompt = f"""
        Analyze the following resume and extract detailed information. Return a JSON object with the following structure:
        {{
            "email": "extracted email address",
            "skills": ["list of technical and soft skills"],
            "education": "education background summary",
            "experience_level": "entry/junior/mid/senior",
            "career_domain": "primary career field/domain",
            "certifications": ["list of certifications if any"],
            "projects": ["list of projects mentioned"],
            "languages": ["programming languages mentioned"],
            "tools": ["tools and technologies mentioned"],
            "soft_skills": ["communication, leadership, etc."],
            "summary": "brief professional summary"
        }}
        
        Resume text:
        {resume_text}
        
        Be thorough and extract as much relevant information as possible.
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
        st.error(f"Error analyzing resume with OpenAI: {str(e)}")
        return None

def analyze_resume_with_gemini(resume_text, api_key):
    """Use Google Gemini to extract information from resume"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Analyze the following resume and extract detailed information. Return a JSON object with the following structure:
        {{
            "email": "extracted email address",
            "skills": ["list of technical and soft skills"],
            "education": "education background summary",
            "experience_level": "entry/junior/mid/senior",
            "career_domain": "primary career field/domain",
            "certifications": ["list of certifications if any"],
            "projects": ["list of projects mentioned"],
            "languages": ["programming languages mentioned"],
            "tools": ["tools and technologies mentioned"],
            "soft_skills": ["communication, leadership, etc."],
            "summary": "brief professional summary"
        }}
        
        Resume text:
        {resume_text}
        
        Be thorough and extract as much relevant information as possible.
        """
        
        response = model.generate_content(prompt)
        result = response.text
        
        # Clean the response to extract JSON
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = result[json_start:json_end]
            return json.loads(json_str)
        else:
            return json.loads(result)
    
    except Exception as e:
        st.error(f"Error analyzing resume with Gemini: {str(e)}")
        return None

def get_skill_gap_analysis(user_profile, api_key, use_gemini=False):
    """Get comprehensive skill gap analysis and recommendations"""
    try:
        user_skills = user_profile.get('skills', [])
        career_domain = user_profile.get('career_domain', 'General')
        experience_level = user_profile.get('experience_level', 'entry')
        
        prompt = f"""
        Based on the user's profile:
        - Current skills: {user_skills}
        - Career domain: {career_domain}
        - Experience level: {experience_level}
        - Education: {user_profile.get('education', 'Not specified')}
        
        Provide a comprehensive analysis in JSON format:
        {{
            "gap_analysis": "detailed analysis of skill gaps and market alignment",
            "recommended_skills": [
                {{
                    "skill": "skill name",
                    "priority": "high/medium/low",
                    "reason": "why this skill is important",
                    "time_to_learn": "estimated learning time"
                }}
            ],
            "learning_resources": {{
                "skill_name": [
                    {{
                        "type": "course/book/project/certification",
                        "title": "resource title",
                        "provider": "platform/author",
                        "difficulty": "beginner/intermediate/advanced",
                        "estimated_time": "time to complete"
                    }}
                ]
            }},
            "industry_trends": ["current trends in the industry"],
            "career_roadmap": {{
                "short_term": ["goals for next 3-6 months"],
                "medium_term": ["goals for next 6-12 months"],
                "long_term": ["goals for next 1-2 years"]
            }},
            "salary_insights": {{
                "current_range": "estimated salary range for current skills",
                "potential_range": "potential salary after skill development"
            }}
        }}
        
        Make recommendations specific to {career_domain} and {experience_level} level positions.
        Focus on practical, actionable advice for career growth.
        """
        
        if use_gemini:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            result = response.text
            
            # Extract JSON from response
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                return json.loads(json_str)
        else:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            result = response.choices[0].message.content
            return json.loads(result)
    
    except Exception as e:
        st.error(f"Error getting skill gap analysis: {str(e)}")
        return None

def search_jobs_jsearch(skills, location="Remote", experience_level="entry level", api_key=""):
    """Search for jobs using JSearch API"""
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        
        # Create search query based on skills and experience level
        skills_str = " ".join(skills[:3])  # Use top 3 skills
        query = f"{experience_level} {skills_str} jobs"
        
        querystring = {
            "query": query,
            "page": "1",
            "num_pages": "1",
            "date_posted": "month",
            "remote_jobs_only": "true" if location.lower() == "remote" else "false"
        }
        
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('data', [])
            
            # Filter and enhance job data
            filtered_jobs = []
            for job in jobs[:10]:  # Limit to 10 jobs
                job_data = {
                    'title': job.get('job_title', 'N/A'),
                    'company': job.get('employer_name', 'N/A'),
                    'location': f"{job.get('job_city', 'N/A')}, {job.get('job_country', 'N/A')}",
                    'description': job.get('job_description', 'N/A')[:200] + "...",
                    'apply_link': job.get('job_apply_link', '#'),
                    'posted_date': job.get('job_posted_at_datetime_utc', 'N/A'),
                    'employment_type': job.get('job_employment_type', 'N/A'),
                    'required_skills': job.get('job_required_skills', []),
                    'salary': job.get('job_salary', 'Not specified')
                }
                filtered_jobs.append(job_data)
            
            return filtered_jobs
        else:
            st.warning(f"Job search API returned status code: {response.status_code}")
            return []
    
    except Exception as e:
        st.error(f"Error fetching jobs: {str(e)}")
        return []

def create_skill_visualizations(user_profile, gap_analysis):
    """Create comprehensive skill visualizations"""
    try:
        user_skills = user_profile.get('skills', [])
        recommended_skills = gap_analysis.get('recommended_skills', []) if gap_analysis else []
        
        # 1. Current Skills Distribution
        skill_categories = {
            'Technical Skills': 0,
            'Soft Skills': 0,
            'Tools & Frameworks': 0,
            'Domain Knowledge': 0
        }
        
        # Categorize skills (simplified logic)
        technical_keywords = ['python', 'javascript', 'java', 'sql', 'html', 'css', 'react', 'node', 'programming']
        soft_keywords = ['communication', 'leadership', 'teamwork', 'problem solving', 'creativity', 'management']
        tool_keywords = ['git', 'docker', 'aws', 'azure', 'jenkins', 'kubernetes', 'tableau', 'excel']
        
        for skill in user_skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in technical_keywords):
                skill_categories['Technical Skills'] += 1
            elif any(keyword in skill_lower for keyword in soft_keywords):
                skill_categories['Soft Skills'] += 1
            elif any(keyword in skill_lower for keyword in tool_keywords):
                skill_categories['Tools & Frameworks'] += 1
            else:
                skill_categories['Domain Knowledge'] += 1
        
        # Create pie chart for skill distribution
        fig_pie = px.pie(
            values=list(skill_categories.values()),
            names=list(skill_categories.keys()),
            title="Your Current Skill Distribution",
            color_discrete_sequence=['#667eea', '#764ba2', '#43e97b', '#f093fb']
        )
        fig_pie.update_layout(
            font=dict(size=14),
            title_font_size=18,
            showlegend=True
        )
        
        # 2. Skill Gap Priority Chart
        if recommended_skills:
            skill_names = []
            priorities = []
            colors = []
            
            for skill_data in recommended_skills[:8]:  # Top 8 skills
                if isinstance(skill_data, dict):
                    skill_names.append(skill_data.get('skill', 'Unknown'))
                    priority = skill_data.get('priority', 'medium').lower()
                    if priority == 'high':
                        priorities.append(5)
                        colors.append('#f5576c')
                    elif priority == 'medium':
                        priorities.append(3)
                        colors.append('#f093fb')
                    else:
                        priorities.append(1)
                        colors.append('#43e97b')
                else:
                    skill_names.append(str(skill_data))
                    priorities.append(3)
                    colors.append('#f093fb')
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=skill_names,
                    y=priorities,
                    marker_color=colors,
                    text=priorities,
                    textposition='auto',
                )
            ])
            fig_bar.update_layout(
                title="Skills to Learn - Priority Analysis",
                xaxis_title="Skills",
                yaxis_title="Priority Score",
                font=dict(size=12),
                title_font_size=18,
                xaxis_tickangle=-45
            )
        else:
            fig_bar = go.Figure()
            fig_bar.add_annotation(
                text="Complete skill analysis to see recommendations",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
        
        # 3. Learning Timeline
        if recommended_skills:
            timeline_data = []
            cumulative_time = 0
            
            for i, skill_data in enumerate(recommended_skills[:6]):
                if isinstance(skill_data, dict):
                    skill_name = skill_data.get('skill', f'Skill {i+1}')
                    time_str = skill_data.get('time_to_learn', '4 weeks')
                else:
                    skill_name = str(skill_data)
                    time_str = '4 weeks'
                
                # Extract weeks from time string
                weeks = 4  # default
                if 'week' in time_str.lower():
                    try:
                        weeks = int(re.findall(r'\d+', time_str)[0])
                    except:
                        weeks = 4
                elif 'month' in time_str.lower():
                    try:
                        months = int(re.findall(r'\d+', time_str)[0])
                        weeks = months * 4
                    except:
                        weeks = 8
                
                timeline_data.append({
                    'Skill': skill_name,
                    'Start_Week': cumulative_time,
                    'Duration': weeks,
                    'End_Week': cumulative_time + weeks
                })
                cumulative_time += weeks
            
            fig_timeline = go.Figure()
            
            colors = ['#667eea', '#764ba2', '#43e97b', '#f093fb', '#f5576c', '#00f2fe']
            
            for i, item in enumerate(timeline_data):
                fig_timeline.add_trace(go.Scatter(
                    x=[item['Start_Week'], item['End_Week']],
                    y=[i, i],
                    mode='lines+markers',
                    line=dict(width=8, color=colors[i % len(colors)]),
                    marker=dict(size=10),
                    name=item['Skill'],
                    hovertemplate=f"<b>{item['Skill']}</b><br>Duration: {item['Duration']} weeks<extra></extra>"
                ))
            
            fig_timeline.update_layout(
                title="Learning Timeline (Recommended Path)",
                xaxis_title="Weeks",
                yaxis_title="Skills",
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(timeline_data))),
                    ticktext=[item['Skill'] for item in timeline_data]
                ),
                font=dict(size=12),
                title_font_size=18,
                showlegend=False,
                height=400
            )
        else:
            fig_timeline = go.Figure()
            fig_timeline.add_annotation(
                text="Complete skill analysis to see learning timeline",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
        
        return fig_pie, fig_bar, fig_timeline
    
    except Exception as e:
        st.error(f"Error creating visualizations: {str(e)}")
        return None, None, None

def chatbot_response(user_message, api_key, use_gemini=False, user_context=None):
    """Generate intelligent chatbot response for career guidance"""
    try:
        context = ""
        if user_context:
            skills = user_context.get('skills', [])
            domain = user_context.get('career_domain', 'General')
            context = f"User's skills: {', '.join(skills[:5])}. Career domain: {domain}. "
        
        system_prompt = f"""
        You are an AI career guidance assistant for students and entry-level professionals. 
        {context}
        
        Provide helpful, encouraging, and practical advice about:
        - Skill development and learning paths
        - Career planning and goal setting
        - Job search strategies and networking
        - Interview preparation and resume tips
        - Industry insights and trends
        - Learning resources and certifications
        
        Keep responses concise (2-3 sentences), friendly, actionable, and personalized when possible.
        Use emojis sparingly but effectively. Be encouraging and supportive.
        """
        
        if use_gemini:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            full_prompt = f"{system_prompt}\n\nUser question: {user_message}"
            response = model.generate_content(full_prompt)
            return response.text
        else:
            openai.api_key = api_key
            
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
        return "I'm having trouble responding right now. Please try again later! 🤖"

def display_metrics(user_profile, gap_analysis):
    """Display key metrics and insights"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Current Skills</div>
        </div>
        """.format(len(user_profile.get('skills', []))), unsafe_allow_html=True)
    
    with col2:
        recommended_count = len(gap_analysis.get('recommended_skills', [])) if gap_analysis else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Skills to Learn</div>
        </div>
        """.format(recommended_count), unsafe_allow_html=True)
    
    with col3:
        experience_level = user_profile.get('experience_level', 'Entry').title()
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Experience Level</div>
        </div>
        """.format(experience_level), unsafe_allow_html=True)
    
    with col4:
        domain = user_profile.get('career_domain', 'General')
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Career Domain</div>
        </div>
        """.format(domain), unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header Section
    st.markdown("""
    <div class="header-container">
        <h1 class="main-title">🎯 AI Skill Gap Analyzer</h1>
        <p class="subtitle">Discover your potential • Bridge the gap • Land your dream job</p>
        <p class="description">Empowering students and entry-level professionals with AI-driven career insights and personalized learning recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Configuration Section
    with st.expander("🔑 API Configuration", expanded=not (st.session_state.openai_api_key or st.session_state.gemini_api_key)):
        st.markdown("**Configure your AI APIs to get started:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            openai_key = st.text_input(
                "OpenAI API Key", 
                type="password", 
                value=st.session_state.openai_api_key,
                help="Get your API key from https://platform.openai.com/api-keys"
            )
            if openai_key:
                st.session_state.openai_api_key = openai_key
        
        with col2:
            gemini_key = st.text_input(
                "Google Gemini API Key", 
                type="password", 
                value=st.session_state.gemini_api_key,
                help="Get your API key from https://makersuite.google.com/app/apikey"
            )
            if gemini_key:
                st.session_state.gemini_api_key = gemini_key
        
        with col3:
            jsearch_key = st.text_input(
                "JSearch API Key (Optional)", 
                type="password", 
                value=st.session_state.jsearch_api_key,
                help="Get your API key from RapidAPI for job search functionality"
            )
            if jsearch_key:
                st.session_state.jsearch_api_key = jsearch_key
        
        if not (st.session_state.openai_api_key or st.session_state.gemini_api_key):
            st.warning("⚠️ Please enter at least one AI API key (OpenAI or Gemini) to continue.")
            return
    
    # Main Layout
    col_main, col_chat = st.columns([3, 1])
    
    with col_main:
        # Input Section
        st.markdown("""
        <div class="feature-card">
            <h2 class="card-title">📄 Upload Your Resume or Enter Skills</h2>
            <p class="card-content">Choose your preferred method to analyze your skills and get personalized recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📤 Upload Resume (PDF)", "✍️ Manual Entry"])
        
        with tab1:
            uploaded_file = st.file_uploader(
                "Choose your resume (PDF format)", 
                type="pdf",
                help="Upload your resume in PDF format for AI-powered analysis"
            )
            
            if uploaded_file:
                col_analyze, col_ai_choice = st.columns([2, 1])
                
                with col_ai_choice:
                    ai_choice = st.selectbox(
                        "Choose AI Model",
                        ["OpenAI GPT", "Google Gemini"],
                        disabled=not (st.session_state.openai_api_key and st.session_state.gemini_api_key)
                    )
                
                with col_analyze:
                    if st.button("🔍 Analyze Resume", type="primary"):
                        with st.spinner("🤖 AI is analyzing your resume..."):
                            resume_text = extract_text_from_pdf(uploaded_file)
                            
                            if resume_text:
                                # Choose AI model based on selection and availability
                                use_gemini = (ai_choice == "Google Gemini" and st.session_state.gemini_api_key)
                                api_key = st.session_state.gemini_api_key if use_gemini else st.session_state.openai_api_key
                                
                                if use_gemini:
                                    analysis = analyze_resume_with_gemini(resume_text, api_key)
                                else:
                                    analysis = analyze_resume_with_openai(resume_text, api_key)
                                
                                if analysis:
                                    st.session_state.user_profile = analysis
                                    st.session_state.user_skills = analysis.get('skills', [])
                                    st.session_state.analysis_complete = True
                                    st.success("✅ Resume analyzed successfully!")
                                    st.rerun()
                            else:
                                st.error("❌ Could not extract text from the PDF. Please try a different file.")
        
        with tab2:
            with st.form("manual_entry_form"):
                skills_input = st.text_area(
                    "Enter your skills (comma-separated)", 
                    placeholder="Python, JavaScript, Communication, Problem Solving, SQL, React...",
                    height=100
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    career_domain = st.selectbox(
                        "Select your career domain", 
                        ["Software Development", "Data Science", "Digital Marketing", 
                         "UI/UX Design", "Business Analysis", "Cybersecurity", 
                         "Product Management", "DevOps", "Other"]
                    )
                
                with col2:
                    experience_level = st.selectbox(
                        "Experience Level",
                        ["Entry Level", "Junior", "Mid Level", "Senior"]
                    )
                
                email = st.text_input("Email (optional)", placeholder="your.email@example.com")
                education = st.text_input("Education (optional)", placeholder="Bachelor's in Computer Science")
                
                submitted = st.form_submit_button("🚀 Analyze Skills", type="primary")
                
                if submitted and skills_input:
                    skills_list = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
                    
                    st.session_state.user_profile = {
                        'skills': skills_list,
                        'career_domain': career_domain,
                        'experience_level': experience_level.lower(),
                        'email': email,
                        'education': education,
                        'summary': f"{experience_level} professional in {career_domain}"
                    }
                    st.session_state.user_skills = skills_list
                    st.session_state.analysis_complete = True
                    st.success("✅ Skills analyzed successfully!")
                    st.rerun()
        
        # Results Section
        if st.session_state.analysis_complete and st.session_state.user_profile:
            user_profile = st.session_state.user_profile
            
            # Display Metrics
            display_metrics(user_profile, None)
            
            # Current Skills Display
            st.markdown("""
            <div class="feature-card">
                <h2 class="card-title">🎯 Your Current Skills Profile</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Display skills in categories
            skills = user_profile.get('skills', [])
            if skills:
                skills_html = ""
                for skill in skills:
                    skills_html += f'<span class="skill-card">{skill}</span>'
                st.markdown(skills_html, unsafe_allow_html=True)
                
                # User summary
                if user_profile.get('summary'):
                    st.info(f"📋 **Profile Summary:** {user_profile['summary']}")
            
            # Get AI Analysis
            st.markdown("""
            <div class="feature-card">
                <h2 class="card-title">🤖 AI-Powered Skill Gap Analysis</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔍 Get Detailed Analysis", type="primary"):
                with st.spinner("🧠 AI is analyzing your skill gaps and generating recommendations..."):
                    # Choose AI model
                    use_gemini = bool(st.session_state.gemini_api_key)
                    api_key = st.session_state.gemini_api_key if use_gemini else st.session_state.openai_api_key
                    
                    gap_analysis = get_skill_gap_analysis(user_profile, api_key, use_gemini)
                    
                    if gap_analysis:
                        st.session_state.gap_analysis = gap_analysis
                        st.session_state.recommended_skills = gap_analysis.get('recommended_skills', [])
                        st.session_state.learning_resources = gap_analysis.get('learning_resources', {})
                        st.rerun()
            
            # Display Analysis Results
            if hasattr(st.session_state, 'gap_analysis'):
                gap_analysis = st.session_state.gap_analysis
                
                # Gap Analysis Summary
                st.markdown("""
                <div class="feature-card">
                    <h2 class="card-title">📊 Skill Gap Analysis</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(gap_analysis.get('gap_analysis', 'Analysis not available'))
                
                # Salary Insights
                if gap_analysis.get('salary_insights'):
                    salary_info = gap_analysis['salary_insights']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"💰 **Current Potential:** {salary_info.get('current_range', 'Not specified')}")
                    with col2:
                        st.success(f"🚀 **Future Potential:** {salary_info.get('potential_range', 'Not specified')}")
                
                # Recommended Skills
                recommended_skills = gap_analysis.get('recommended_skills', [])
                if recommended_skills:
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">🎓 Priority Skills to Learn</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for i, skill_data in enumerate(recommended_skills[:6], 1):
                        if isinstance(skill_data, dict):
                            skill_name = skill_data.get('skill', f'Skill {i}')
                            priority = skill_data.get('priority', 'medium').upper()
                            reason = skill_data.get('reason', 'Important for career growth')
                            time_to_learn = skill_data.get('time_to_learn', '4 weeks')
                            
                            priority_color = {
                                'HIGH': '#f5576c',
                                'MEDIUM': '#f093fb', 
                                'LOW': '#43e97b'
                            }.get(priority, '#f093fb')
                            
                            st.markdown(f"""
                            <div class="recommended-skill-card" style="background: linear-gradient(135deg, {priority_color}, {priority_color}dd);">
                                <div class="skill-title">{i}. {skill_name}</div>
                                <div class="skill-priority">Priority: {priority} | Time: {time_to_learn}</div>
                                <div style="font-size: 0.95rem; opacity: 0.9;">{reason}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="recommended-skill-card">
                                <div class="skill-title">{i}. {skill_data}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Learning Resources
                learning_resources = gap_analysis.get('learning_resources', {})
                if learning_resources:
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">📚 Personalized Learning Resources</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for skill, resources in learning_resources.items():
                        with st.expander(f"📖 Resources for {skill}"):
                            if isinstance(resources, list):
                                for resource in resources:
                                    if isinstance(resource, dict):
                                        st.markdown(f"""
                                        **{resource.get('title', 'Resource')}** ({resource.get('type', 'Course')})
                                        - Provider: {resource.get('provider', 'N/A')}
                                        - Difficulty: {resource.get('difficulty', 'Beginner')}
                                        - Time: {resource.get('estimated_time', 'N/A')}
                                        """)
                                    else:
                                        st.write(f"• {resource}")
                            else:
                                st.write(resources)
                
                # Career Roadmap
                if gap_analysis.get('career_roadmap'):
                    roadmap = gap_analysis['career_roadmap']
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">🗺️ Your Career Roadmap</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**🎯 Short-term (3-6 months)**")
                        for goal in roadmap.get('short_term', []):
                            st.write(f"• {goal}")
                    
                    with col2:
                        st.markdown("**📈 Medium-term (6-12 months)**")
                        for goal in roadmap.get('medium_term', []):
                            st.write(f"• {goal}")
                    
                    with col3:
                        st.markdown("**🚀 Long-term (1-2 years)**")
                        for goal in roadmap.get('long_term', []):
                            st.write(f"• {goal}")
                
                # Visualizations
                st.markdown("""
                <div class="feature-card">
                    <h2 class="card-title">📈 Skill Analytics & Insights</h2>
                </div>
                """, unsafe_allow_html=True)
                
                fig_pie, fig_bar, fig_timeline = create_skill_visualizations(user_profile, gap_analysis)
                
                if fig_pie and fig_bar and fig_timeline:
                    tab_viz1, tab_viz2, tab_viz3 = st.tabs(["📊 Skill Distribution", "📈 Priority Analysis", "⏱️ Learning Timeline"])
                    
                    with tab_viz1:
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with tab_viz2:
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with tab_viz3:
                        st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Industry Trends
                if gap_analysis.get('industry_trends'):
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">📊 Industry Trends</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for trend in gap_analysis['industry_trends']:
                        st.write(f"🔹 {trend}")
                
                # Job Recommendations
                if st.session_state.jsearch_api_key:
                    st.markdown("""
                    <div class="feature-card">
                        <h2 class="card-title">💼 Live Job Opportunities</h2>
                        <p class="card-content">Discover entry-level positions that match your skills and career goals.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_search, col_location = st.columns([2, 1])
                    
                    with col_location:
                        job_location = st.selectbox("Location", ["Remote", "United States", "Canada", "United Kingdom", "India"])
                    
                    with col_search:
                        if st.button("🔍 Find Matching Jobs", type="primary"):
                            with st.spinner("🔍 Searching for relevant job opportunities..."):
                                jobs = search_jobs_jsearch(
                                    user_profile.get('skills', []), 
                                    location=job_location,
                                    experience_level=user_profile.get('experience_level', 'entry level'),
                                    api_key=st.session_state.jsearch_api_key
                                )
                                
                                if jobs:
                                    st.session_state.job_recommendations = jobs
                                    st.success(f"✅ Found {len(jobs)} job opportunities!")
                                else:
                                    st.warning("⚠️ No jobs found. Try adjusting your search criteria or check your API key.")
                
                # Display Job Results
                if hasattr(st.session_state, 'job_recommendations') and st.session_state.job_recommendations:
                    for job in st.session_state.job_recommendations:
                        st.markdown(f"""
                        <div class="job-card">
                            <div class="job-title">{job['title']}</div>
                            <div class="job-company">🏢 {job['company']}</div>
                            <div class="job-location">📍 {job['location']}</div>
                            <div class="job-skills">💼 {job['employment_type']}</div>
                            <div style="margin: 1rem 0;">
                                <div style="font-size: 0.9rem; opacity: 0.9;">{job['description']}</div>
                            </div>
                            <a href="{job['apply_link']}" target="_blank" class="apply-btn">
                                🔗 Apply Now
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Chatbot Section
    with col_chat:
        st.markdown("""
        <div class="feature-card">
            <h2 class="card-title">🤖 Career Assistant</h2>
            <p class="card-content">Ask me anything about career development, skills, or job search strategies!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat Interface
        chat_container = st.container()
        
        with chat_container:
            # Display recent chat messages
            for message in st.session_state.chat_messages[-6:]:  # Show last 6 messages
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 Assistant:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("💬 Ask a question...", key="chat_input", placeholder="How can I improve my skills?")
        
        col_send, col_clear = st.columns([3, 1])
        
        with col_send:
            send_clicked = st.button("Send 📤", type="primary", use_container_width=True)
        
        with col_clear:
            if st.button("Clear 🗑️", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
        
        if send_clicked and user_input:
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            # Get bot response
            use_gemini = bool(st.session_state.gemini_api_key)
            api_key = st.session_state.gemini_api_key if use_gemini else st.session_state.openai_api_key
            
            bot_response = chatbot_response(
                user_input, 
                api_key, 
                use_gemini, 
                st.session_state.user_profile if st.session_state.analysis_complete else None
            )
            st.session_state.chat_messages.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update chat
            st.rerun()
        
        # Quick action buttons
        st.markdown("### 🚀 Quick Questions")
        
        quick_questions = [
            ("💡 Resume tips", "How can I improve my resume for entry-level positions?"),
            ("🎯 Interview prep", "Give me tips for preparing for job interviews."),
            ("📈 Skill roadmap", "Create a learning roadmap for my career goals."),
            ("🔍 Job search", "What are the best strategies for finding entry-level jobs?"),
            ("💼 LinkedIn tips", "How can I optimize my LinkedIn profile?"),
            ("📚 Learning resources", "Recommend free resources to learn new skills.")
        ]
        
        for button_text, question in quick_questions:
            if st.button(button_text, use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": question})
                
                use_gemini = bool(st.session_state.gemini_api_key)
                api_key = st.session_state.gemini_api_key if use_gemini else st.session_state.openai_api_key
                
                response = chatbot_response(
                    question, 
                    api_key, 
                    use_gemini, 
                    st.session_state.user_profile if st.session_state.analysis_complete else None
                )
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

if __name__ == "__main__":
    main()