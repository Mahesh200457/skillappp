import streamlit as st
import PyPDF2
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import time
import re
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
# No google-generativeai, openai, nltk, spacy, python-docx, streamlit-option-menu, python-dotenv

# --- Configuration (Hardcoded for single file, NOT recommended for production) ---
# NOTE: Since actual AI APIs (Gemini/ChatGPT) are excluded as per the new library list,
# these keys are placeholders. The AI features will be simulated.
# Please replace with your actual JSearch API key if you plan to run this
# and expect real job data.
JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e" # Replace with your actual JSearch API Key

# --- Helper Functions ---

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file using PyPDF2."""
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text() or ""
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

def parse_resume_for_skills(resume_text):
    """
    Parses resume text to identify potential skills using basic keyword matching.
    This is a very simplified version due to the exclusion of NLP libraries (NLTK, spaCy).
    """
    text = resume_text.lower()
    # A broader list of common tech and soft skills. Expand as needed.
    common_skills = [
        "python", "java", "c++", "javascript", "react", "angular", "node.js",
        "sql", "nosql", "aws", "azure", "gcp", "docker", "kubernetes",
        "machine learning", "deep learning", "data science", "statistics",
        "tableau", "power bi", "excel", "git", "linux", "agile",
        "scrum", "project management", "communication", "teamwork", "leadership",
        "html", "css", "api", "database", "frontend", "backend", "full stack",
        "cloud computing", "cybersecurity", "network", "devops", "testing",
        "problem solving", "critical thinking", "adaptability", "creativity",
        "presentation", "negotiation", "research", "analysis", "marketing",
        "finance", "accounting", "sales", "customer service", "ux", "ui",
        "design", "autocad", "photoshop", "illustrator", "video editing",
        "microsoft office", "word", "powerpoint", "outlook"
    ]
    identified_skills = set()
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            identified_skills.add(skill)
    return list(identified_skills)

def get_job_role_options():
    """Provides a list of common job roles."""
    return [
        "Software Engineer", "Data Scientist", "Product Manager",
        "UX Designer", "Marketing Specialist", "Business Analyst",
        "Full Stack Developer", "Frontend Developer", "Backend Developer",
        "DevOps Engineer", "Cloud Architect", "Cybersecurity Analyst",
        "Technical Writer", "HR Specialist", "Financial Analyst",
        "Graphic Designer", "Content Creator", "Sales Representative",
        "Project Manager", "Consultant", "Data Analyst", "Machine Learning Engineer",
        "Network Administrator", "System Administrator", "Database Administrator",
        "QA Engineer", "Scrum Master", "IT Support", "Technical Recruiter"
    ]

# --- Simulated AI Functions (NO ACTUAL AI API CALLS) ---

def simulated_generate_skill_gap_analysis(user_skills, target_role):
    """
    Simulates AI-powered skill gap analysis.
    In a real app, this would call Google Gemini or OpenAI ChatGPT.
    """
    required_skills_map = {
        "Software Engineer": ["Python", "Java", "Data Structures", "Algorithms", "Git", "SQL", "Problem Solving", "Object-Oriented Programming"],
        "Data Scientist": ["Python", "R", "Statistics", "Machine Learning", "SQL", "Data Visualization", "Pandas", "NumPy", "Deep Learning"],
        "Product Manager": ["Market Research", "Product Strategy", "Roadmapping", "Communication", "Agile", "User Experience", "Data Analysis"],
        "UX Designer": ["Wireframing", "Prototyping", "User Research", "Figma", "Adobe XD", "Information Architecture", "Usability Testing"],
        "Marketing Specialist": ["SEO", "SEM", "Content Marketing", "Social Media Marketing", "Email Marketing", "Google Analytics", "Campaign Management"],
        "Business Analyst": ["Data Modeling", "SQL", "Requirements Gathering", "Process Mapping", "Communication", "Excel", "Data Visualization"],
        "Full Stack Developer": ["JavaScript", "React", "Node.js", "Python", "SQL", "HTML", "CSS", "APIs", "Cloud Platforms"],
        # Add more roles and their skills as needed
    }

    target_role_lower = target_role.lower()
    relevant_required_skills = []
    for role_key, skills in required_skills_map.items():
        if target_role_lower in role_key.lower():
            relevant_required_skills = skills
            break
    if not relevant_required_skills:
        # Fallback if the role isn't explicitly mapped
        relevant_required_skills = ["Core Skills for " + target_role, "Problem Solving", "Communication", "Adaptability"]

    # Basic comparison
    missing_skills = [skill for skill in relevant_required_skills if skill.lower() not in [us.lower() for us in user_skills]]
    present_skills = [skill for skill in relevant_required_skills if skill.lower() in [us.lower() for us in user_skills]]

    overall_assessment = "Based on the provided skills, here's a preliminary assessment:\n"
    if len(present_skills) >= len(relevant_required_skills) * 0.7:
        overall_assessment += f"You have a strong foundation for a '{target_role}' role."
    elif len(present_skills) >= len(relevant_required_skills) * 0.4:
        overall_assessment += f"You have some relevant skills for a '{target_role}' role, but significant gaps exist."
    else:
        overall_assessment += f"You currently have limited skills for a '{target_role}' role. Focused learning is recommended."

    response = f"""
    **Required Core Skills for {target_role}:**
    {'- ' + '\\n- '.join(relevant_required_skills) if relevant_required_skills else 'No specific core skills identified for this role.'}

    **Missing Skills (Skill Gaps):**
    {'- ' + '\\n- '.join(missing_skills) if missing_skills else 'Great news! No major skill gaps identified based on basic analysis.'}

    **Advanced/Desirable Skills for {target_role}:**
    - Cloud Computing (AWS/Azure/GCP)
    - Advanced Algorithms (if applicable)
    - Domain-specific expertise
    - Public Speaking
    - Mentorship

    **Overall Assessment:**
    {overall_assessment}
    """
    return response, relevant_required_skills, missing_skills

def simulated_generate_learning_recommendations(user_skills, target_role, skill_gaps):
    """
    Simulates AI-powered learning recommendations.
    In a real app, this would call Google Gemini or OpenAI ChatGPT.
    """
    if not skill_gaps:
        return f"""
        Congratulations! Based on our analysis, you currently have no significant skill gaps for the '{target_role}' role.
        To continue your growth, consider exploring advanced topics or niche areas within {target_role}, or delve into leadership and mentorship skills.

        **Example Next Steps:**
        - **Online Courses:** "Advanced {target_role} Techniques" on Coursera, "Mastering Industry Tools" on Udemy.
        - **Books:** "Clean Code" by Robert C. Martin (for developers), "Inspired" by Marty Cagan (for product roles).
        - **Project Ideas:** Lead a small open-source project, build a complex personal project incorporating new technologies.
        """

    recommendations = f"""
    Based on your identified skill gaps for the '{target_role}' role ({', '.join(skill_gaps)}), here are personalized learning recommendations:

    **Online Courses:**
    - **Coursera:** "Google IT Automation with Python Professional Certificate" (for Python/IT), "Deep Learning Specialization" (for ML), "Data Science Professional Certificate" (for Data Science).
    - **Udemy:** Search for "{skill_gaps[0] if skill_gaps else 'relevant'}" bootcamp or "complete guide to {target_role}."
    - **edX:** Explore courses from top universities related to your skill gaps, e.g., "MITx: Introduction to Computer Science and Programming Using Python."
    - **LinkedIn Learning:** Look for specific skill-focused courses like "Learning SQL," "Agile Foundations."

    **Books:**
    - For general software development: "Cracking the Coding Interview" by Gayle Laakmann McDowell.
    - For data science: "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow" by Aurélien Géron.
    - For product management: "The Lean Startup" by Eric Ries.
    - For soft skills: "Atomic Habits" by James Clear, "How to Win Friends and Influence People" by Dale Carnegie.
    - Search for "[Skill Gap Name] for Dummies" or "[Skill Gap Name] in 24 Hours".

    **Project Ideas:**
    - Build a small application that uses some of your missing skills (e.g., a web app using a new framework, a data analysis project using a new library).
    - Contribute to an open-source project that utilizes the skills you want to learn.
    - Create a personal portfolio website showcasing your current and newly acquired skills.
    - Participate in hackathons focused on areas where you have skill gaps.
    - For data-related roles: Find a dataset on Kaggle and perform a complete end-to-end analysis, from cleaning to visualization and modeling.
    """
    return recommendations

def simulated_ai_chatbot_response(user_query, chat_history):
    """
    Simulates AI chatbot responses using rule-based logic.
    No actual AI model is called here.
    """
    user_query_lower = user_query.lower()

    if "hello" in user_query_lower or "hi" in user_query_lower:
        return "Hello there! How can I assist you with your career journey today?"
    elif "skill gap" in user_query_lower:
        return "The skill gap analysis feature helps you compare your current skills with those required for your target job role. Just upload your resume or input your skills, and select a role."
    elif "recommendations" in user_query_lower or "learn" in user_query_lower:
        return "After the skill gap analysis, I can provide personalized recommendations for online courses, books, and project ideas to help you bridge those gaps."
    elif "jobs" in user_query_lower or "opportunities" in user_query_lower:
        return "You can use the 'Job Search' tab to find real-time job listings relevant to your target role or other keywords you provide."
    elif "resume" in user_query_lower or "upload" in user_query_lower:
        return "You can upload your resume (PDF format) on the 'Skill Analysis' page, and I will try to extract your skills from it."
    elif "thank" in user_query_lower:
        return "You're welcome! Feel free to ask if you need anything else."
    elif "help" in user_query_lower:
        return "I'm here to guide you. What specific question do you have about career planning, skill development, or job searching?"
    else:
        return "That's an interesting question! While I'm a simulated AI for this demo, in a full application, I could answer complex career queries. For now, try asking about skill gaps, recommendations, or jobs!"

# --- JSearch API Integration ---

def search_jobs(query, num_pages=1):
    """
    Searches for job listings using the JSearch API.
    """
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    jobs = []
    for page in range(1, num_pages + 1):
        querystring = {
            "query": query,
            "page": str(page),
            "num_pages": str(num_pages), # JSearch might use num_pages differently
            "date_posted": "week" # Example: jobs posted in the last week
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if data and 'data' in data:
                jobs.extend(data['data'])
            else:
                break # No more data
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching jobs: {e}. Please check your API key or network connection.")
            break
    return jobs

def format_job_card(job):
    """
    Formats a job dictionary into an HTML string for display in Streamlit.
    """
    title = job.get('job_title', 'N/A')
    company = job.get('employer_name', 'N/A')
    location = ""
    if job.get('job_city'):
        location += job['job_city']
    if job.get('job_state'):
        location += f", {job['job_state']}" if location else job['job_state']
    if job.get('job_country'):
        location += f", {job['job_country']}" if location else job['job_country']
    location = location or 'N/A'

    description_snippet = job.get('job_description', 'No description available.')
    # Clean up description for snippet - remove HTML tags, extra whitespace
    description_snippet = re.sub(r'<.*?>', '', description_snippet)
    description_snippet = ' '.join(description_snippet.split())
    description_snippet = (description_snippet[:250] + '...') if len(description_snippet) > 250 else description_snippet

    apply_link = job.get('job_apply_link', '#')

    return f"""
    <div class="job-card">
        <h4 style="color: #0056b3; margin-top: 0px; margin-bottom: 5px;">{title}</h4>
        <p style="margin-bottom: 5px; font-weight: bold;">{company}</p>
        <p style="font-size: 0.9em; color: #555; margin-bottom: 5px;">📍 {location}</p>
        <p style="font-size: 0.9em; color: #666; margin-bottom: 10px;">{description_snippet}</p>
        <a href="{apply_link}" target="_blank" class="job-apply-button">Apply Now</a>
    </div>
    """

# --- Visualizations (Plotly) ---

def create_skill_gap_bar_chart(identified_skills, required_skills):
    """
    Generates a Plotly bar chart showing the presence/absence of key skills.
    """
    all_relevant_skills = list(set(identified_skills) | set(required_skills))
    if not all_relevant_skills:
        st.info("No skills to visualize for the gap analysis.")
        return None

    # Ensure consistent casing for comparison, but display original
    identified_skills_lower = [s.lower() for s in identified_skills]
    required_skills_lower = [s.lower() for s in required_skills]

    data = []
    for skill in all_relevant_skills:
        status = "Identified" if skill.lower() in identified_skills_lower else "Missing"
        data.append({"Skill": skill, "Status": status})

    df = pd.DataFrame(data)

    fig = px.bar(
        df,
        y='Skill',
        color='Status',
        color_discrete_map={'Identified': '#28a745', 'Missing': '#dc3545'}, # Green for identified, Red for missing
        orientation='h',
        title='Your Skills vs. Required Skills',
        labels={'count': 'Number of Skills'},
        height=max(400, len(all_relevant_skills) * 40) # Dynamic height
    )
    fig.update_layout(
        xaxis_title="Status",
        yaxis_title="Skill",
        legend_title="Skill Status",
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="y unified"
    )
    return fig

def create_skill_distribution_pie_chart(skills_list):
    """
    Generates a Plotly pie chart for the top 10 identified skills.
    """
    if not skills_list:
        st.info("No identified skills to visualize for distribution.")
        return None

    skill_counts = pd.Series(skills_list).value_counts().head(10) # Top 10 skills

    fig = px.pie(
        names=skill_counts.index,
        values=skill_counts.values,
        title='Top 10 Identified Skills Distribution',
        hole=0.3, # Donut chart
        color_discrete_sequence=px.colors.qualitative.Pastel # Softer color palette
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# --- PDF Report Generation (ReportLab) ---

def generate_report_pdf(user_name, user_skills, target_role, analysis_text, recommendations_text, chart_image_buffer_bytes):
    """
    Generates a PDF report summarizing the skill gap analysis with ReportLab.
    chart_image_buffer_bytes should be a BytesIO object of the chart PNG.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = styles['h1']
    title_style.alignment = TA_CENTER
    heading_style = styles['h2']
    subheading_style = styles['h3']
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 14 # Line spacing

    # Markdown to ReportLab compatible text (basic conversion for bold/italics)
    def markdown_to_reportlab(text):
        # Basic markdown to ReportLab HTML-like tags
        text = text.replace('**', '<b>').replace('*', '<i>')
        return text.replace('\n', '<br/>')

    story = []

    # Title
    story.append(Paragraph("AI-Powered Skill Gap Analysis Report", title_style))
    story.append(Spacer(1, 0.3 * 72)) # 0.3 inch spacer

    # User Info
    story.append(Paragraph(f"<b>Name:</b> {user_name or 'User'}", normal_style))
    story.append(Paragraph(f"<b>Target Role:</b> {target_role}", normal_style))
    story.append(Spacer(1, 0.2 * 72))

    # Identified Skills
    story.append(Paragraph("<b>Your Identified Skills:</b>", subheading_style))
    story.append(Paragraph(markdown_to_reportlab(f"{', '.join(user_skills) if user_skills else 'No skills identified.'}"), normal_style))
    story.append(Spacer(1, 0.3 * 72))

    # Skill Gap Analysis
    story.append(Paragraph("<b>Skill Gap Analysis:</b>", heading_style))
    story.append(Paragraph(markdown_to_reportlab(analysis_text), normal_style))
    story.append(Spacer(1, 0.3 * 72))

    # Learning Recommendations
    story.append(Paragraph("<b>Personalized Learning Recommendations:</b>", heading_style))
    story.append(Paragraph(markdown_to_reportlab(recommendations_text), normal_style))
    story.append(Spacer(1, 0.3 * 72))

    # Add Chart if available
    if chart_image_buffer_bytes:
        story.append(PageBreak()) # Start charts on a new page
        story.append(Paragraph("<b>Skill Status Visualization:</b>", heading_style))
        story.append(Spacer(1, 0.1 * 72))
        try:
            # Need to get image dimensions to scale correctly
            img = Image(chart_image_buffer_bytes, width=450, height=300) # Adjust dimensions as needed
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 0.3 * 72))
        except Exception as e:
            st.warning(f"Could not embed chart in PDF: {e}")
            story.append(Paragraph("<i>(Error embedding chart visualization)</i>", normal_style))


    story.append(Spacer(1, 0.5 * 72)) # Spacer before footer
    story.append(Paragraph(f"<i>Report generated by AI-Powered Skill Gap Analyzer on {datetime.now().strftime('%Y-%m-%d')}</i>", styles['h6']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Streamlit Application ---

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Skill Gap Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Professional Design ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="st"] {
        font-family: 'Poppins', sans-serif;
    }

    .main-header {
        font-size: 3.2em;
        color: #1A2E44; /* Dark Blue */
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
        letter-spacing: -1px;
    }
    .stApp {
        background-color: #F8F9FA; /* Light Gray background */
    }
    .stSidebar {
        background-color: #FFFFFF; /* White sidebar */
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
        padding-top: 20px;
    }
    .stButton>button {
        background-color: #007BFF; /* Primary Blue */
        color: white;
        border-radius: 12px; /* More rounded */
        padding: 12px 25px;
        font-size: 1.1em;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #0056b3; /* Darker Blue on hover */
        transform: translateY(-2px); /* Slight lift */
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 1px solid #CED4DA; /* Light gray border */
        padding: 12px;
        font-size: 1em;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }
    .stSelectbox>div>div {
        border-radius: 10px;
        border: 1px solid #CED4DA;
        padding: 8px 12px;
        font-size: 1em;
    }
    .stFileUploader>div>div>button {
        background-color: #28A745; /* Green */
        color: white;
        border-radius: 12px;
        padding: 12px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stFileUploader>div>div>button:hover {
        background-color: #1F7C3C; /* Darker Green on hover */
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        font-size: 1em;
    }
    .recommendation-card, .job-card {
        border: 1px solid #E9ECEF; /* Lighter border */
        border-radius: 15px; /* More rounded */
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.08); /* More subtle shadow */
        background-color: white;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .recommendation-card:hover, .job-card:hover {
        transform: translateY(-5px); /* Lift effect */
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    .job-card a.job-apply-button {
        display: inline-block;
        background-color: #007BFF;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 10px;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .job-card a.job-apply-button:hover {
        background-color: #0056b3;
    }
    h2, h3, h4 {
        color: #34495E; /* Darker text for headers */
        font-weight: 600;
    }
    p {
        color: #495057; /* Slightly darker body text */
    }

    /* Chatbot specific styles */
    .chat-message-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-height: 400px; /* Constrain height */
        overflow-y: auto; /* Scrollable */
        padding-right: 10px; /* For scrollbar */
    }
    .chat-message {
        padding: 12px 18px;
        border-radius: 20px;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 0.95em;
    }
    .chat-message.user {
        background-color: #E6F3FF; /* Light blue for user */
        align-self: flex-end;
        margin-left: auto;
        border-bottom-right-radius: 5px;
        color: #1A2E44;
    }
    .chat-message.ai {
        background-color: #F1F3F5; /* Very light gray for AI */
        align-self: flex-start;
        margin-right: auto;
        border-bottom-left-radius: 5px;
        color: #34495E;
    }
    .stTextInput[data-testid="stChatInput"] {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 10px 0;
        border-top: 1px solid #E9ECEF;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'user_skills' not in st.session_state:
    st.session_state.user_skills = []
if 'analysis_results_text' not in st.session_state:
    st.session_state.analysis_results_text = None
if 'analysis_required_skills' not in st.session_state: # Store for charting
    st.session_state.analysis_required_skills = []
if 'analysis_missing_skills' not in st.session_state: # Store for charting
    st.session_state.analysis_missing_skills = []
if 'recommendations_text' not in st.session_state:
    st.session_state.recommendations_text = None
if 'job_listings' not in st.session_state:
    st.session_state.job_listings = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I'm your AI Career Assistant. How can I help you today?"}]
if 'target_role' not in st.session_state:
    st.session_state.target_role = ""
if 'user_name_for_pdf' not in st.session_state:
    st.session_state.user_name_for_pdf = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Skill Analysis"

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://i.ibb.co/L84p803/AI-Brain-Logo.png", width=120) # Example Logo Placeholder
    st.markdown("## Navigation")
    if st.button("Skill Analysis", key="nav_skill_analysis"):
        st.session_state.current_page = "Skill Analysis"
    if st.button("Job Search", key="nav_job_search"):
        st.session_state.current_page = "Job Search"
    if st.button("About", key="nav_about"):
        st.session_state.current_page = "About"

    st.markdown("---")
    st.markdown("### 🧑‍💻 AI Career Assistant")
    # Chat message display area
    st.markdown('<div class="chat-message-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai">{message["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input at the bottom of the sidebar
    user_query = st.text_input("Ask me anything about your career!", key="chat_input_sidebar")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.spinner("Thinking..."):
            ai_response = simulated_ai_chatbot_response(user_query, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun() # Rerun to update chat display


# --- Main Content Area ---
st.markdown('<h1 class="main-header">🧠 AI-Powered Skill Gap Analyzer</h1>', unsafe_allow_html=True)
st.write("Your personalized career assistant to identify skill gaps, get recommendations, and find jobs.")
st.markdown("---")

if st.session_state.current_page == "Skill Analysis":
    st.header("Step 1: Provide Your Skills")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Upload Your Resume (PDF only)")
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
        if uploaded_file is not None:
            with st.spinner("Parsing resume..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                if resume_text:
                    st.session_state.user_skills = parse_resume_for_skills(resume_text)
                    st.success("Resume parsed successfully!")
                    if st.session_state.user_skills:
                        st.info(f"**Identified Skills:** {', '.join(st.session_state.user_skills)}")
                    else:
                        st.warning("No specific skills identified from resume. Please try manual input or ensure skills are clearly listed.")
                else:
                    st.error("Could not extract text from the resume. Please ensure it's a searchable PDF.")

    with col2:
        st.subheader("Or Manually Input Skills")
        manual_skills_input = st.text_area(
            "Enter your skills, separated by commas (e.g., Python, SQL, Data Analysis)",
            value=", ".join(st.session_state.user_skills),
            height=120,
            key="manual_skills_input"
        )
        if st.button("Update Skills from Manual Input", key="update_manual_skills_button"):
            st.session_state.user_skills = [skill.strip() for skill in manual_skills_input.split(',') if skill.strip()]
            if st.session_state.user_skills:
                st.success(f"Skills updated: {', '.join(st.session_state.user_skills)}")
            else:
                st.info("No skills entered manually.")

    st.markdown("---")
    st.header("Step 2: Select Your Target Job Role")
    st.session_state.target_role = st.selectbox(
        "Choose a target job role or type your own:",
        options=get_job_role_options() + ["Other (Specify)"],
        index=get_job_role_options().index(st.session_state.target_role) if st.session_state.target_role in get_job_role_options() else 0,
        help="This will help the platform simulate a relevant skill gap analysis.",
        key="target_role_select"
    )
    if st.session_state.target_role == "Other (Specify)":
        st.session_state.target_role = st.text_input("Please specify the job role:", key="other_role_input")
        if not st.session_state.target_role:
             st.warning("Please specify the 'Other' job role.")

    st.markdown("---")
    if st.button("Perform Skill Gap Analysis", key="analyze_button"):
        if not st.session_state.user_skills:
            st.warning("Please provide your skills first (upload resume or manual input).")
        elif not st.session_state.target_role:
            st.warning("Please select or specify a target job role.")
        else:
            with st.spinner("Analyzing skill gaps and generating recommendations... (Simulated AI)"):
                time.sleep(2) # Simulate AI processing time
                analysis_text, required_skills, missing_skills = simulated_generate_skill_gap_analysis(st.session_state.user_skills, st.session_state.target_role)
                st.session_state.analysis_results_text = analysis_text
                st.session_state.analysis_required_skills = required_skills
                st.session_state.analysis_missing_skills = missing_skills # Store these
                st.session_state.recommendations_text = simulated_generate_learning_recommendations(st.session_state.user_skills, st.session_state.target_role, st.session_state.analysis_missing_skills)
            st.success("Analysis complete!")

    if st.session_state.analysis_results_text:
        st.markdown("---")
        st.header("📊 Skill Gap Analysis Results")
        st.markdown(st.session_state.analysis_results_text)

        st.markdown("---")
        st.header("📚 Personalized Learning Recommendations")
        st.markdown(st.session_state.recommendations_text)

        # --- Visualizations ---
        st.markdown("---")
        st.header("📈 Skill Visualizations")
        st.write("Here are some insights into your skills compared to the target role.")

        col_viz1, col_viz2 = st.columns(2)
        with col_viz1:
            st.subheader("Your Skills vs. Required Skills")
            bar_chart_fig = create_skill_gap_bar_chart(
                st.session_state.user_skills,
                st.session_state.analysis_required_skills
            )
            if bar_chart_fig:
                st.plotly_chart(bar_chart_fig, use_container_width=True)
                # Save chart to bytes for PDF
                bar_chart_buffer = io.BytesIO()
                bar_chart_fig.write_image(bar_chart_buffer, format="png")
                bar_chart_buffer.seek(0)
                st.session_state.chart_for_pdf = bar_chart_buffer.getvalue() # Store bytes
            else:
                st.info("No data to generate skill gap chart.")
                st.session_state.chart_for_pdf = None

        with col_viz2:
            st.subheader("Distribution of Your Identified Skills")
            pie_chart_fig = create_skill_distribution_pie_chart(st.session_state.user_skills)
            if pie_chart_fig:
                st.plotly_chart(pie_chart_fig, use_container_width=True)
            else:
                st.info("No data to generate skill distribution chart.")

        # --- Download PDF Report ---
        st.markdown("---")
        st.header("📄 Download Your Report")
        st.session_state.user_name_for_pdf = st.text_input("Enter your name for the PDF report (Optional):", value=st.session_state.user_name_for_pdf, key="pdf_name_input")
        if st.button("Generate and Download PDF Report", key="download_pdf_button"):
            if st.session_state.analysis_results_text and st.session_state.recommendations_text:
                with st.spinner("Generating PDF..."):
                    pdf_buffer = generate_report_pdf(
                        st.session_state.user_name_for_pdf,
                        st.session_state.user_skills,
                        st.session_state.target_role,
                        st.session_state.analysis_results_text,
                        st.session_state.recommendations_text,
                        st.session_state.get('chart_for_pdf', None) # Pass the chart bytes
                    )
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"Skill_Gap_Report_{st.session_state.user_name_for_pdf.replace(' ', '_') or 'User'}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("PDF report generated!")
            else:
                st.warning("Please perform the skill gap analysis first to generate a report.")

elif st.session_state.current_page == "Job Search":
    st.header("Explore Relevant Job Opportunities")
    st.write("Find entry-level jobs tailored to your target role using the JSearch API.")

    search_query = st.text_input(
        "Enter keywords for job search (e.g., 'Software Engineer fresher', 'Data Analyst entry-level')",
        value=f"{st.session_state.target_role} fresher" if st.session_state.target_role else "",
        help="Based on your selected role, a default query is provided.",
        key="job_search_query_input"
    )
    job_limit = st.slider("Number of jobs to retrieve", min_value=5, max_value=50, value=15, step=5)


    if st.button("Search Jobs", key="job_search_button"):
        if search_query:
            with st.spinner(f"Searching for '{search_query}' jobs..."):
                # JSearch API doesn't support a direct 'limit', so we'll fetch a bit more
                # and then slice to the desired limit. 'num_pages' is imprecise.
                fetched_jobs = search_jobs(search_query, num_pages=2) # Fetching from 2 pages
                st.session_state.job_listings = fetched_jobs[:job_limit] # Slice to desired limit

            if st.session_state.job_listings:
                st.success(f"Found {len(st.session_state.job_listings)} job listings for '{search_query}'.")
            else:
                st.info("No job listings found for this query. Try different keywords or check your JSearch API key.")
        else:
            st.warning("Please enter a job search query.")

    if st.session_state.job_listings:
        st.subheader("Live Job Listings for Freshers")
        for job in st.session_state.job_listings:
            st.markdown(format_job_card(job), unsafe_allow_html=True)
    elif st.button("Reset Job Search", key="reset_job_search_button"):
        st.session_state.job_listings = []
        st.rerun()


elif st.session_state.current_page == "About":
    st.header("About the AI-Powered Skill Gap Analyzer")
    st.write("""
    This platform is a dynamic, student-focused career assistant designed to help students and entry-level professionals
    identify gaps in their skillsets, receive personalized learning recommendations, and explore relevant job opportunities.
    """)
    st.subheader("Key Features:")
    st.markdown("""
    * **Resume Parsing & Manual Skill Input:** Easily provide your current skillset by uploading a PDF resume or manually entering skills.
    * **Simulated AI Skill Gap Analysis:** The platform simulates comparing your skills with target job role requirements and identifies potential gaps.
    * **Personalized Learning Recommendations:** Get tailored suggestions for online courses, books, and project ideas to bridge your skill gaps.
    * **Real-time Job Listings:** Explore relevant entry-level job opportunities fetched via the JSearch API.
    * **Insightful Visualizations:** Understand your skill status at a glance with interactive Plotly charts.
    * **Downloadable PDF Report:** Get a comprehensive summary of your analysis and recommendations.
    * **Interactive Simulated AI Chatbot:** A simple chatbot ready to answer basic questions about the platform's features.
    """)
    st.subheader("Technologies Used:")
    st.markdown("""
    * **Python:** Core programming language.
    * **Streamlit:** For rapid web application development and responsive UI.
    * **PyPDF2:** For parsing PDF resumes.
    * **Requests:** For making HTTP calls to the JSearch API.
    * **Pandas:** For data manipulation.
    * **Plotly Express & Plotly Graph Objects:** For interactive data visualizations.
    * **ReportLab:** For generating professional PDF reports.
    * **Regular Expressions (`re`):** For basic text processing and skill extraction.
    """)
    st.subheader("Important Note on AI Functionality:")
    st.warning("""
    **This specific implementation uses simulated AI responses for skill gap analysis, recommendations, and the chatbot.**
    This is because the requested libraries excluded `google-generativeai` (Gemini) and `openai` (ChatGPT).
    In a full, truly AI-powered version, these features would be dynamically generated by advanced Large Language Models (LLMs).
    """)
    st.subheader("Future Enhancements (Potential):")
    st.markdown("""
    * Integration with actual LLMs (Google Gemini, OpenAI ChatGPT) for dynamic AI responses.
    * More sophisticated resume parsing using dedicated NLP libraries (e.g., SpaCy, NLTK with pre-trained models).
    * User authentication and profile management.
    * Skill tracking and progress monitoring.
    * Direct integration or deep links to recommended learning platforms.
    * AI-powered resume optimization suggestions.
    """)
