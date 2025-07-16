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
# from reportlab.lib.pagesizes import letter # Not directly used in the web app UI
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image # Not directly used in the web app UI
# from reportlab.lib.styles import getSampleStyleSheets, ParagraphStyle # Not directly used in the web app UI
# from reportlab.lib.enums import TA_CENTER # Not directly used in the web app UI

# --- API Keys ---
# IMPORTANT: For a real application, consider using Streamlit Secrets or environment variables
# instead of hardcoding keys directly in the script for better security practices.
GEMINI_API_KEY = "AIzaSyDOsFhRWN2-uPpOZqHbU3HZ5prZkSuqiBA" # Replace with your actual Gemini API Key
JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e"
 # Replace with your actual JSearch API Key

# --- Gemini API Configuration ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# --- JSearch API Configuration ---
JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com/"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

# --- Helper Functions ---

def extract_text_from_pdf(uploaded_file):
    """
    Extracts text content from an uploaded PDF file.
    """
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text
    return None

def analyze_resume_with_gemini(resume_text, job_role):
    """
    Sends resume text and job role to Gemini API for analysis.
    This is a basic example; prompt engineering is crucial here for detailed output.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        st.error("Gemini API Key is not set. Please update the GEMINI_API_KEY.")
        return {"error": "API Key not set."}

    prompt = f"""
    Analyze the following resume text for the '{job_role}' role.
    Provide an ATS score out of 100 indicating how well the resume aligns with the role.
    Extract key skills, education, and experience.
    Suggest 3-5 high-level improvement areas.

    Resume Text:
    {resume_text}

    Format the output as a JSON object with the following keys:
    {{
        "ats_score": int,
        "extracted_skills": list of str,
        "extracted_education": list of str,
        "extracted_experience": list of str,
        "improvement_areas": list of str,
        "raw_analysis": str
    }}
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        response_json = response.json()
        
        # Gemini API often wraps the text in 'parts' -> 'text'
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            gemini_output_text = response_json['candidates'][0]['content']['parts'][0]['text']
            
            # Attempt to parse the JSON output from Gemini
            try:
                analysis_result = json.loads(gemini_output_text)
                return analysis_result
            except json.JSONDecodeError:
                st.warning("Gemini did not return a perfect JSON. Attempting to parse raw text.")
                return {"error": "JSON parsing failed from Gemini output", "raw_output": gemini_output_text}
        else:
            return {"error": "No candidates found in Gemini response", "raw_response": response_json}

    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Gemini API: {e}")
        return {"error": str(e)}

def get_job_recommendations(query, num_jobs=10):
    """
    Fetches job listings using the JSearch API.
    """
    if not JSEARCH_API_KEY or JSEARCH_API_KEY == "YOUR_JSEARCH_API_KEY":
        st.error("JSearch API Key is not set. Please update the JSEARCH_API_KEY.")
        return []

    url = f"{JSEARCH_BASE_URL}search"
    querystring = {
        "query": query,
        "num_pages": "1",
        "date_posted": "week", # Filter for recent jobs
        "job_requirements": "entry_level" # Prioritize entry-level
    }

    try:
        response = requests.get(url, headers=JSEARCH_HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        if data and data['status'] == 'OK' and 'data' in data:
            jobs = []
            for job in data['data'][:num_jobs]:
                jobs.append({
                    "title": job.get('job_title', 'N/A'),
                    "company": job.get('employer_name', 'N/A'),
                    "location": job.get('job_city', 'N/A') + ", " + job.get('job_state', 'N/A') if job.get('job_city') else job.get('job_country', 'N/A'),
                    "description": job.get('job_description', 'N/A')[:200] + "..." if job.get('job_description') else 'N/A', # Shorten description
                    "link": job.get('job_apply_link', job.get('job_google_link', '#')) # Prefer direct apply link
                })
            return jobs
        else:
            st.warning("No job data found or JSearch API issue.")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling JSearch API: {e}")
        return []

def get_learning_recommendations_gemini(skill_gaps, job_role):
    """
    Generates learning recommendations based on skill gaps using Gemini API.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return {"error": "Gemini API Key not set."}

    # Crafting a detailed prompt for learning recommendations
    prompt = f"""
    Based on the following skill gaps for the '{job_role}' role, provide specific and actionable learning recommendations.
    Focus on online courses, books, certifications, and practice projects.
    For each recommendation, include a title, a short description, and a plausible (but dummy if real not available) link.
    If real links are not possible, explain what type of link it would be (e.g., "Search on Coursera for...").

    Skill Gaps: {', '.join(skill_gaps) if skill_gaps else 'No specific gaps identified, suggest general resources for the role.'}

    Provide the output as a JSON array of objects, each object having:
    {{
        "type": "Course" | "Book" | "Certification" | "Project",
        "title": "Recommendation Title",
        "description": "Short description of the recommendation.",
        "link": "https://example.com/link_to_resource"
    }}
    Generate at least 5 distinct recommendations.
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
        response.raise_for_status()
        response_json = response.json()
        
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            gemini_output_text = response_json['candidates'][0]['content']['parts'][0]['text']
            # Clean up potential markdown formatting that Gemini sometimes adds
            gemini_output_text = gemini_output_text.replace("```json", "").replace("```", "").strip()
            
            try:
                recommendations = json.loads(gemini_output_text)
                return recommendations
            except json.JSONDecodeError:
                st.warning(f"Gemini did not return a perfect JSON for recommendations. Raw: {gemini_output_text}")
                # Fallback: try to parse lines or return raw
                return [{"type": "Text", "title": "Parsing Error", "description": gemini_output_text, "link": "#"}]
        else:
            return [{"type": "Error", "title": "No Recommendations", "description": "Gemini could not generate recommendations.", "link": "#"}]
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling Gemini API for recommendations: {e}")
        return [{"type": "Error", "title": "API Call Failed", "description": str(e), "link": "#"}]

def get_chatbot_response(user_query):
    """
    Generates a chatbot response using Gemini API.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        return "Chatbot is not configured due to missing Gemini API Key."

    prompt = f"""
    You are an AI career assistant. Respond to the user's query professionally and helpfully.
    You can provide resume improvement tips, career guidance, job search help, or course clarification.
    Keep responses concise and directly address the user's question.

    User Query: {user_query}
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
        response.raise_for_status()
        response_json = response.json()
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Sorry, I couldn't generate a response at this time."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to chatbot: {e}"

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="AI Skill Gap Analyzer")

st.title("🚀 AI-Based Skill Gap Analyzer Platform")

# --- Sidebar for Chatbot ---
with st.sidebar:
    st.header("🤖 AI Career Assistant")
    st.write("Ask me anything about resume improvement, career guidance, job search, or courses!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chatbot_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


# --- Main Content Area ---
col1, col2 = st.columns([0.6, 0.4]) # Adjust column width for content and potential future use

with col1:
    st.subheader("1. Upload Your Resume (PDF)")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    st.subheader("2. Select Your Desired Job Role")
    # A more comprehensive list of roles would be better.
    # This could eventually be loaded from a database or a configuration file.
    job_roles = [
        "Data Analyst", "Software Developer", "Product Manager",
        "Marketing Specialist", "Financial Analyst", "UX/UI Designer",
        "Project Manager", "Cybersecurity Analyst", "Human Resources Generalist",
        "Sales Representative", "Customer Success Manager", "Cloud Engineer",
        "DevOps Engineer", "Business Analyst", "Data Scientist", "Machine Learning Engineer"
    ]
    selected_role = st.selectbox("Select a job role:", job_roles)

    if uploaded_file and selected_role:
        st.markdown("---")
        st.subheader("3. Analyze & Get Recommendations")
        if st.button("Analyze My Resume"):
            with st.spinner("Analyzing your resume and fetching data... This may take a moment."):
                resume_text = extract_text_from_pdf(uploaded_file)
                
                if resume_text:
                    st.session_state['resume_text'] = resume_text # Store in session state
                    st.session_state['selected_role'] = selected_role # Store in session state

                    # --- Resume Analysis ---
                    st.info("Performing AI-based resume analysis...")
                    resume_analysis = analyze_resume_with_gemini(resume_text, selected_role)
                    st.session_state['resume_analysis'] = resume_analysis # Store in session state

                    if resume_analysis and "error" not in resume_analysis:
                        st.success("Resume analysis complete!")
                        st.subheader("📊 Resume Analysis Results")
                        st.metric(label="ATS Score", value=f"{resume_analysis.get('ats_score', 'N/A')}/100")

                        st.write("#### Extracted Skills:")
                        st.json(resume_analysis.get('extracted_skills', []))
                        st.write("#### Extracted Education:")
                        st.json(resume_analysis.get('extracted_education', []))
                        st.write("#### Extracted Experience:")
                        st.json(resume_analysis.get('extracted_experience', []))
                        
                        # --- Visualizations Placeholder ---
                        st.subheader("📈 Visualizations")
                        
                        # Example: Skill Match vs. Gap Chart (Placeholder data)
                        # In a real app, you'd derive these from detailed Gemini analysis
                        # For now, let's assume some dummy gaps based on analysis or user input
                        if 'improvement_areas' in resume_analysis and resume_analysis['improvement_areas']:
                            skill_gaps_dummy = [re.sub(r'^\d+\.\s*', '', area).strip() for area in resume_analysis['improvement_areas']]
                            st.write("### Recommended Improvement Areas:")
                            for i, area in enumerate(skill_gaps_dummy):
                                st.markdown(f"- {area}")
                        else:
                            skill_gaps_dummy = ["Data Structures & Algorithms", "Cloud Computing (AWS/Azure)", "Advanced SQL"] # Fallback dummy
                            st.write("### Recommended Improvement Areas: (Based on general gaps for this role)")
                            for i, area in enumerate(skill_gaps_dummy):
                                st.markdown(f"- {area}")

                        
                        # Simple Bar Chart for Skill Match vs. Gap (Conceptual)
                        # In a real scenario, Gemini would provide specific skill matches/gaps
                        # For this example, let's assume a fixed skill set and calculate a "match"
                        df_skills = pd.DataFrame({
                            'Category': ['Matched Skills', 'Skill Gaps'],
                            'Percentage': [resume_analysis.get('ats_score', 70), 100 - resume_analysis.get('ats_score', 70)]
                        })
                        fig_skill_gap = px.bar(df_skills, x='Category', y='Percentage',
                                            title='Skill Match vs. Gap',
                                            color='Category',
                                            color_discrete_map={'Matched Skills': 'lightblue', 'Skill Gaps': 'lightcoral'})
                        st.plotly_chart(fig_skill_gap, use_container_width=True)

                        # --- Learning Recommendations ---
                        st.subheader("📚 Learning Recommendations")
                        st.info("Generating personalized learning recommendations...")
                        # Use skill_gaps_dummy for now; ideally, Gemini provides specific gaps.
                        learning_recs = get_learning_recommendations_gemini(skill_gaps_dummy, selected_role)
                        st.session_state['learning_recs'] = learning_recs # Store in session state

                        if learning_recs and "error" not in learning_recs:
                            for rec in learning_recs:
                                st.markdown(f"""
                                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                                    <h5 style="color: #4CAF50;">{rec.get('type', 'Recommendation')}</h5>
                                    <h4 style="margin-top: 5px; margin-bottom: 5px;">{rec.get('title', 'N/A')}</h4>
                                    <p>{rec.get('description', 'N/A')}</p>
                                    <a href="{rec.get('link', '#')}" target="_blank" style="text-decoration: none; color: #1E90FF;">Learn More &rarr;</a>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("Could not generate learning recommendations.")
                            st.json(learning_recs) # Show raw error if available

                        # --- Job Recommendations ---
                        st.subheader("💼 Entry-Level Job Recommendations")
                        st.info("Fetching real-time entry-level job listings...")
                        # Use selected_role for job search query
                        job_recommendations = get_job_recommendations(selected_role + " entry level", num_jobs=10)
                        st.session_state['job_recommendations'] = job_recommendations # Store in session state

                        if job_recommendations:
                            for job in job_recommendations:
                                st.markdown(f"""
                                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: #f9f9f9;">
                                    <h4 style="margin-top: 0; color: #333;">{job.get('title', 'N/A')}</h4>
                                    <p><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                                    <p><strong>Location:</strong> {job.get('location', 'N/A')}</p>
                                    <p>{job.get('description', 'N/A')}</p>
                                    <a href="{job.get('link', '#')}" target="_blank" style="text-decoration: none; color: #FF4B4B; font-weight: bold;">Apply Now &rarr;</a>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning("No entry-level job recommendations found for this role.")
                            
                    else:
                        st.error("Failed to analyze resume. Please check the API key or try again.")
                        st.json(resume_analysis) # Display raw error from Gemini
                else:
                    st.error("Could not extract text from the uploaded PDF. Please ensure it's a searchable PDF.")
    else:
        st.info("Please upload your resume and select a job role to begin the analysis.")

st.markdown("---")
st.caption("Powered by Google Gemini & JSearch APIs")
