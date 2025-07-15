import streamlit as st
import openai
import PyPDF2
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import time
import re
from datetime import datetime, timedelta
import base64

# Page configuration
st.set_page_config(
    page_title="AI Skill Gap Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, student-friendly design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .skill-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .job-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .job-card:hover {
        transform: translateX(5px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        height: 500px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        display: flex;
        flex-direction: column;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 20px 20px 0 0;
        text-align: center;
        font-weight: 600;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        max-height: 350px;
    }
    
    .chat-input {
        padding: 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 0 0 20px 20px;
    }
    
    .user-message {
        background: #667eea;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 2rem;
        text-align: right;
    }
    
    .bot-message {
        background: #f0f2f6;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 2rem;
    }
    
    .quick-action-btn {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid #667eea;
        color: #667eea;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.8rem;
    }
    
    .quick-action-btn:hover {
        background: #667eea;
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        transition: transform 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .learning-resource {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0;
    }
    
    .floating-chat-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        z-index: 999;
        transition: transform 0.3s ease;
    }
    
    .floating-chat-toggle:hover {
        transform: scale(1.1);
    }
    
    @media (max-width: 768px) {
        .chatbot-container {
            width: 90%;
            right: 5%;
            height: 400px;
        }
        
        .feature-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'show_chatbot' not in st.session_state:
    st.session_state.show_chatbot = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Helper Functions
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
        return None

def analyze_resume_with_ai(resume_text, api_key):
    """Analyze resume using OpenAI API"""
    try:
        openai.api_key = api_key
        
        prompt = f"""
        Analyze the following resume and extract information in JSON format:
        
        Resume Text: {resume_text}
        
        Please provide a comprehensive analysis in the following JSON structure:
        {{
            "personal_info": {{
                "name": "extracted name",
                "email": "extracted email",
                "phone": "extracted phone",
                "location": "extracted location"
            }},
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "institution name",
                    "year": "graduation year",
                    "gpa": "if mentioned"
                }}
            ],
            "experience": [
                {{
                    "title": "job title",
                    "company": "company name",
                    "duration": "duration",
                    "description": "key responsibilities"
                }}
            ],
            "skills": {{
                "technical": ["list of technical skills"],
                "soft_skills": ["list of soft skills"],
                "tools": ["list of tools/software"],
                "programming_languages": ["list of programming languages"]
            }},
            "experience_level": "entry/junior/mid/senior",
            "career_domain": "identified career domain",
            "strengths": ["key strengths identified"],
            "areas_for_improvement": ["areas that need development"]
        }}
        
        Be thorough and accurate in your analysis.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")
        return None

def get_skill_gap_analysis(user_skills, career_domain, api_key):
    """Get comprehensive skill gap analysis"""
    try:
        openai.api_key = api_key
        
        prompt = f"""
        Provide a comprehensive skill gap analysis for someone with these skills: {user_skills}
        Career Domain: {career_domain}
        
        Please provide analysis in JSON format:
        {{
            "current_skill_assessment": {{
                "technical_score": "score out of 100",
                "soft_skills_score": "score out of 100",
                "overall_readiness": "percentage",
                "market_alignment": "percentage"
            }},
            "skill_gaps": [
                {{
                    "skill": "missing skill name",
                    "importance": "high/medium/low",
                    "priority_score": "1-10",
                    "reason": "why this skill is important",
                    "time_to_learn": "estimated time"
                }}
            ],
            "learning_recommendations": [
                {{
                    "type": "course/book/project/certification",
                    "title": "resource title",
                    "provider": "provider name",
                    "duration": "estimated duration",
                    "difficulty": "beginner/intermediate/advanced",
                    "priority": "high/medium/low",
                    "description": "brief description",
                    "estimated_cost": "cost range"
                }}
            ],
            "career_roadmap": {{
                "short_term": ["goals for next 3 months"],
                "medium_term": ["goals for next 6-12 months"],
                "long_term": ["goals for next 1-2 years"]
            }},
            "salary_insights": {{
                "current_range": "estimated current salary range",
                "potential_range": "potential salary after skill development",
                "market_demand": "high/medium/low"
            }},
            "industry_trends": [
                "current trend 1",
                "current trend 2",
                "current trend 3"
            ]
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    except Exception as e:
        st.error(f"Error getting skill gap analysis: {str(e)}")
        return None

def search_jobs(query, location="", api_key=""):
    """Search for jobs using JSearch API"""
    try:
        url = "https://jsearch.p.rapidapi.com/search"
        
        querystring = {
            "query": f"{query} entry level",
            "page": "1",
            "num_pages": "1",
            "date_posted": "month"
        }
        
        if location:
            querystring["location"] = location
        
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
        st.error(f"Error searching jobs: {str(e)}")
        return []

def create_skill_distribution_chart(skills_data):
    """Create skill distribution pie chart"""
    if not skills_data:
        return None
    
    categories = []
    counts = []
    
    for category, skills in skills_data.items():
        if isinstance(skills, list) and skills:
            categories.append(category.replace('_', ' ').title())
            counts.append(len(skills))
    
    if not categories:
        return None
    
    fig = px.pie(
        values=counts,
        names=categories,
        title="Your Skill Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        font=dict(size=14),
        title_font_size=18,
        showlegend=True,
        height=400
    )
    
    return fig

def create_skill_gap_chart(skill_gaps):
    """Create skill gap priority chart"""
    if not skill_gaps:
        return None
    
    skills = [gap['skill'] for gap in skill_gaps[:10]]  # Top 10
    priorities = [gap['priority_score'] for gap in skill_gaps[:10]]
    
    fig = px.bar(
        x=priorities,
        y=skills,
        orientation='h',
        title="Top Skills to Develop (Priority Score)",
        color=priorities,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        font=dict(size=12),
        title_font_size=18,
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_learning_timeline_chart(recommendations):
    """Create learning timeline chart"""
    if not recommendations:
        return None
    
    # Create timeline data
    timeline_data = []
    start_date = datetime.now()
    
    for i, rec in enumerate(recommendations[:8]):  # Top 8 recommendations
        duration_weeks = 4  # Default
        if 'duration' in rec:
            duration_str = rec['duration'].lower()
            if 'week' in duration_str:
                duration_weeks = int(re.findall(r'\d+', duration_str)[0]) if re.findall(r'\d+', duration_str) else 4
            elif 'month' in duration_str:
                duration_weeks = int(re.findall(r'\d+', duration_str)[0]) * 4 if re.findall(r'\d+', duration_str) else 4
        
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        timeline_data.append({
            'Task': rec['title'][:30] + '...' if len(rec['title']) > 30 else rec['title'],
            'Start': start_date,
            'Finish': end_date,
            'Type': rec['type'].title()
        })
        
        start_date = end_date + timedelta(days=3)  # Small gap between tasks
    
    if not timeline_data:
        return None
    
    df = pd.DataFrame(timeline_data)
    
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Type",
        title="Recommended Learning Timeline"
    )
    
    fig.update_layout(
        font=dict(size=12),
        title_font_size=18,
        height=500
    )
    
    return fig

def chat_with_ai(message, context, api_key):
    """Chat with AI assistant"""
    try:
        openai.api_key = api_key
        
        system_prompt = f"""
        You are a helpful career guidance AI assistant for students and entry-level job seekers. 
        
        User Context: {context}
        
        Provide helpful, encouraging, and practical advice. Keep responses concise but informative.
        Focus on career development, skill building, job search strategies, and educational guidance.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I'm having trouble connecting right now. Please try again later. Error: {str(e)}"

# Main App Header
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin: 0; font-size: 3rem; font-weight: 700;">🎯 AI Skill Gap Analyzer</h1>
    <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        Empowering Students & Entry-Level Professionals with AI-Driven Career Insights
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🔧 Configuration")
    
    with st.expander("🔑 API Keys", expanded=False):
        openai_api_key = st.text_input("OpenAI API Key", type="password", help="Required for AI analysis")
        jsearch_api_key = st.text_input("JSearch API Key", type="password", help="Optional for job search")
    
    st.markdown("### 📊 Quick Stats")
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        if 'current_skill_assessment' in results:
            assessment = results['current_skill_assessment']
            st.metric("Overall Readiness", f"{assessment.get('overall_readiness', 'N/A')}")
            st.metric("Market Alignment", f"{assessment.get('market_alignment', 'N/A')}")
            st.metric("Technical Score", f"{assessment.get('technical_score', 'N/A')}")

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    # Input Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("## 📄 Resume Analysis & Skill Input")
    
    input_method = st.radio(
        "Choose your input method:",
        ["Upload Resume (PDF)", "Manual Skill Entry"],
        horizontal=True
    )
    
    if input_method == "Upload Resume (PDF)":
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['pdf'],
            help="Upload a PDF version of your resume for AI analysis"
        )
        
        if uploaded_file and openai_api_key:
            if st.button("🔍 Analyze Resume", type="primary"):
                with st.spinner("Extracting and analyzing your resume..."):
                    # Extract text from PDF
                    resume_text = extract_text_from_pdf(uploaded_file)
                    
                    if resume_text:
                        # Analyze with AI
                        analysis = analyze_resume_with_ai(resume_text, openai_api_key)
                        
                        if analysis:
                            st.session_state.user_profile = analysis
                            st.success("✅ Resume analyzed successfully!")
                            
                            # Display extracted information
                            st.markdown("### 📋 Extracted Information")
                            
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                if 'personal_info' in analysis:
                                    st.markdown("**Personal Information:**")
                                    info = analysis['personal_info']
                                    st.write(f"• Name: {info.get('name', 'Not found')}")
                                    st.write(f"• Email: {info.get('email', 'Not found')}")
                                    st.write(f"• Location: {info.get('location', 'Not found')}")
                            
                            with col_b:
                                if 'skills' in analysis:
                                    st.markdown("**Skills Summary:**")
                                    skills = analysis['skills']
                                    st.write(f"• Technical: {len(skills.get('technical', []))}")
                                    st.write(f"• Programming: {len(skills.get('programming_languages', []))}")
                                    st.write(f"• Tools: {len(skills.get('tools', []))}")
    
    else:  # Manual Entry
        st.markdown("### ✍️ Enter Your Information")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            career_domain = st.selectbox(
                "Career Domain",
                ["Software Development", "Data Science", "Digital Marketing", "UI/UX Design", 
                 "Cybersecurity", "Product Management", "Business Analysis", "Other"]
            )
        
        with col_b:
            experience_level = st.selectbox(
                "Experience Level",
                ["Student", "Fresh Graduate", "Entry Level (0-1 years)", "Junior (1-2 years)"]
            )
            location = st.text_input("Location (Optional)")
        
        # Skills input
        st.markdown("### 🛠️ Your Skills")
        
        technical_skills = st.text_area(
            "Technical Skills",
            placeholder="e.g., Python, JavaScript, SQL, React, Machine Learning",
            help="Separate skills with commas"
        )
        
        soft_skills = st.text_area(
            "Soft Skills",
            placeholder="e.g., Communication, Leadership, Problem Solving, Teamwork",
            help="Separate skills with commas"
        )
        
        tools = st.text_area(
            "Tools & Software",
            placeholder="e.g., Git, Docker, AWS, Figma, Tableau",
            help="Separate tools with commas"
        )
        
        if st.button("💡 Analyze My Skills", type="primary"):
            if technical_skills or soft_skills or tools:
                # Create user profile from manual input
                user_profile = {
                    "personal_info": {
                        "name": name,
                        "email": email,
                        "location": location
                    },
                    "skills": {
                        "technical": [skill.strip() for skill in technical_skills.split(',') if skill.strip()],
                        "soft_skills": [skill.strip() for skill in soft_skills.split(',') if skill.strip()],
                        "tools": [tool.strip() for tool in tools.split(',') if tool.strip()],
                        "programming_languages": []
                    },
                    "experience_level": experience_level.lower(),
                    "career_domain": career_domain
                }
                
                st.session_state.user_profile = user_profile
                st.success("✅ Profile created successfully!")
            else:
                st.warning("Please enter at least some skills to analyze.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis Results Section
    if st.session_state.user_profile and openai_api_key:
        if st.button("🚀 Get Comprehensive Analysis", type="primary"):
            with st.spinner("Generating your personalized skill gap analysis..."):
                profile = st.session_state.user_profile
                
                # Combine all skills for analysis
                all_skills = []
                if 'skills' in profile:
                    skills = profile['skills']
                    all_skills.extend(skills.get('technical', []))
                    all_skills.extend(skills.get('soft_skills', []))
                    all_skills.extend(skills.get('tools', []))
                    all_skills.extend(skills.get('programming_languages', []))
                
                career_domain = profile.get('career_domain', 'General')
                
                # Get skill gap analysis
                analysis_results = get_skill_gap_analysis(all_skills, career_domain, openai_api_key)
                
                if analysis_results:
                    st.session_state.analysis_results = analysis_results
                    st.success("✅ Analysis complete!")
    
    # Display Analysis Results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Skill Assessment Metrics
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 📊 Your Skill Assessment")
        
        if 'current_skill_assessment' in results:
            assessment = results['current_skill_assessment']
            
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{assessment.get('technical_score', 'N/A')}</h3>
                    <p>Technical Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{assessment.get('soft_skills_score', 'N/A')}</h3>
                    <p>Soft Skills Score</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_c:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{assessment.get('overall_readiness', 'N/A')}</h3>
                    <p>Overall Readiness</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_d:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{assessment.get('market_alignment', 'N/A')}</h3>
                    <p>Market Alignment</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Visualizations
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 📈 Visual Analysis")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Skill Distribution Chart
            if 'skills' in st.session_state.user_profile:
                skills_chart = create_skill_distribution_chart(st.session_state.user_profile['skills'])
                if skills_chart:
                    st.plotly_chart(skills_chart, use_container_width=True)
        
        with viz_col2:
            # Skill Gap Chart
            if 'skill_gaps' in results:
                gap_chart = create_skill_gap_chart(results['skill_gaps'])
                if gap_chart:
                    st.plotly_chart(gap_chart, use_container_width=True)
        
        # Learning Timeline
        if 'learning_recommendations' in results:
            timeline_chart = create_learning_timeline_chart(results['learning_recommendations'])
            if timeline_chart:
                st.plotly_chart(timeline_chart, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Skill Gaps Section
        if 'skill_gaps' in results:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("## 🎯 Skills You Should Develop")
            
            for gap in results['skill_gaps'][:6]:  # Show top 6
                importance_color = {
                    'high': '#ff4757',
                    'medium': '#ffa502',
                    'low': '#2ed573'
                }.get(gap.get('importance', 'medium').lower(), '#ffa502')
                
                st.markdown(f"""
                <div class="recommendation-card" style="background: linear-gradient(135deg, {importance_color}20 0%, {importance_color}40 100%); border-left: 4px solid {importance_color};">
                    <h4 style="color: #333; margin: 0 0 0.5rem 0;">{gap['skill']}</h4>
                    <p style="color: #666; margin: 0 0 0.5rem 0;"><strong>Priority:</strong> {gap.get('priority_score', 'N/A')}/10 | <strong>Importance:</strong> {gap.get('importance', 'N/A').title()}</p>
                    <p style="color: #666; margin: 0 0 0.5rem 0;"><strong>Time to Learn:</strong> {gap.get('time_to_learn', 'N/A')}</p>
                    <p style="color: #333; margin: 0;">{gap.get('reason', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Learning Recommendations
        if 'learning_recommendations' in results:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("## 📚 Personalized Learning Resources")
            
            # Filter by type
            rec_types = list(set([rec['type'] for rec in results['learning_recommendations']]))
            selected_type = st.selectbox("Filter by type:", ["All"] + rec_types)
            
            recommendations = results['learning_recommendations']
            if selected_type != "All":
                recommendations = [rec for rec in recommendations if rec['type'] == selected_type]
            
            for rec in recommendations[:8]:  # Show top 8
                priority_color = {
                    'high': '#667eea',
                    'medium': '#764ba2',
                    'low': '#a8a8a8'
                }.get(rec.get('priority', 'medium').lower(), '#764ba2')
                
                st.markdown(f"""
                <div class="learning-resource">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h4 style="color: #333; margin: 0;">{rec['title']}</h4>
                        <span style="background: {priority_color}; color: white; padding: 0.2rem 0.8rem; border-radius: 15px; font-size: 0.8rem;">
                            {rec.get('type', 'Resource').title()}
                        </span>
                    </div>
                    <p style="color: #666; margin: 0 0 0.5rem 0;"><strong>Provider:</strong> {rec.get('provider', 'N/A')} | <strong>Duration:</strong> {rec.get('duration', 'N/A')} | <strong>Level:</strong> {rec.get('difficulty', 'N/A')}</p>
                    <p style="color: #666; margin: 0 0 0.5rem 0;"><strong>Estimated Cost:</strong> {rec.get('estimated_cost', 'N/A')}</p>
                    <p style="color: #333; margin: 0;">{rec.get('description', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Career Roadmap
        if 'career_roadmap' in results:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("## 🗺️ Your Career Roadmap")
            
            roadmap = results['career_roadmap']
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown("### 🎯 Short Term (3 months)")
                for goal in roadmap.get('short_term', []):
                    st.markdown(f"• {goal}")
            
            with col_b:
                st.markdown("### 🚀 Medium Term (6-12 months)")
                for goal in roadmap.get('medium_term', []):
                    st.markdown(f"• {goal}")
            
            with col_c:
                st.markdown("### 🏆 Long Term (1-2 years)")
                for goal in roadmap.get('long_term', []):
                    st.markdown(f"• {goal}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Salary Insights
        if 'salary_insights' in results:
            st.markdown('<div class="feature-card">', unsafe_allow_html=True)
            st.markdown("## 💰 Salary Insights")
            
            salary = results['salary_insights']
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Current Range</h4>
                    <p>{salary.get('current_range', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Potential Range</h4>
                    <p>{salary.get('potential_range', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_c:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Market Demand</h4>
                    <p>{salary.get('market_demand', 'N/A').title()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Job Search Section
    st.markdown('<div class="feature-card">', unsafe_allow_html=True)
    st.markdown("## 💼 Job Opportunities")
    
    if st.session_state.user_profile and jsearch_api_key:
        profile = st.session_state.user_profile
        career_domain = profile.get('career_domain', '')
        location = profile.get('personal_info', {}).get('location', '')
        
        if st.button("🔍 Find Jobs", type="primary"):
            with st.spinner("Searching for relevant job opportunities..."):
                jobs = search_jobs(career_domain, location, jsearch_api_key)
                
                if jobs:
                    st.success(f"Found {len(jobs)} job opportunities!")
                    
                    for job in jobs[:5]:  # Show top 5 jobs
                        st.markdown(f"""
                        <div class="job-card">
                            <h4 style="color: #333; margin: 0 0 0.5rem 0;">{job.get('job_title', 'N/A')}</h4>
                            <p style="color: #666; margin: 0 0 0.5rem 0;"><strong>Company:</strong> {job.get('employer_name', 'N/A')}</p>
                            <p style="color: #666; margin: 0 0 0.5rem 0;"><strong>Location:</strong> {job.get('job_city', 'N/A')}, {job.get('job_state', 'N/A')}</p>
                            <p style="color: #666; margin: 0 0 1rem 0;"><strong>Type:</strong> {job.get('job_employment_type', 'N/A')}</p>
                            <a href="{job.get('job_apply_link', '#')}" target="_blank" style="background: #667eea; color: white; padding: 0.5rem 1rem; border-radius: 5px; text-decoration: none; display: inline-block;">Apply Now</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No jobs found. Try adjusting your search criteria.")
    else:
        if not jsearch_api_key:
            st.info("Add JSearch API key to search for jobs")
        else:
            st.info("Complete your profile analysis to see relevant job opportunities")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Industry Trends
    if st.session_state.analysis_results and 'industry_trends' in st.session_state.analysis_results:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("## 📈 Industry Trends")
        
        trends = st.session_state.analysis_results['industry_trends']
        for i, trend in enumerate(trends, 1):
            st.markdown(f"**{i}.** {trend}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Floating Chatbot
if st.session_state.show_chatbot:
    st.markdown("""
    <div class="chatbot-container">
        <div class="chat-header">
            🤖 Career Assistant
        </div>
        <div class="chat-messages" id="chat-messages">
    """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        if message['role'] == 'user':
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("### Quick Questions:")
    quick_questions = [
        "How to improve my resume?",
        "Best skills for my field?",
        "Interview preparation tips?",
        "Salary negotiation advice?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(question, key=f"quick_{i}"):
                if openai_api_key:
                    context = str(st.session_state.user_profile) + str(st.session_state.analysis_results)
                    response = chat_with_ai(question, context, openai_api_key)
                    
                    st.session_state.chat_messages.append({"role": "user", "content": question})
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.rerun()
    
    # Chat input
    user_input = st.text_input("Ask me anything about your career...", key="chat_input")
    
    if st.button("Send", key="send_chat") and user_input:
        if openai_api_key:
            context = str(st.session_state.user_profile) + str(st.session_state.analysis_results)
            response = chat_with_ai(user_input, context, openai_api_key)
            
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
        else:
            st.warning("Please add your OpenAI API key to use the chat feature.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Floating chat toggle button
if st.button("💬", key="chat_toggle", help="Open Career Assistant"):
    st.session_state.show_chatbot = not st.session_state.show_chatbot
    st.rerun()

# Footer
st.markdown("""
<div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.7);">
    <p>🎯 AI Skill Gap Analyzer - Empowering Your Career Journey with AI</p>
    <p>Built with ❤️ for Students and Entry-Level Professionals</p>
</div>
""", unsafe_allow_html=True)