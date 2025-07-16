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

# Import the Google Generative AI library
import google.generativeai as genai

# --- API Keys ---
# YOUR GEMINI_API_KEY IS HERE. If this key is not valid or restricted, no models will be found.
GEMINI_API_KEY = "AIzaSyC9xWVau-jGsCd2bxromOhd2zCES9N9Ego" 
JSEARCH_API_KEY = "2cab498475mshcc1eeb3378ca34dp193e9fjsn4f1fd27b904e"

# --- Configure Gemini API ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"FATAL ERROR: Failed to configure Gemini API. Please check your API key: {e}")
    st.stop() # Stop the app immediately if API key configuration fails

# --- IMPORTANT: MODEL DISCOVERY (READ THIS ON YOUR RUNNING APP) ---
st.subheader("🛠️ Gemini Model Availability Diagnostic (IMPORTANT!)")
st.warning("Please read this section when the app runs:")
st.info("Below are the models available for YOUR API KEY that support text generation.")
st.info("1. **Copy the EXACT 'Available Model:' name** (e.g., `gemini-1.5-flash`).")
st.info("2. **PASTE that name** into the `GEMINI_MODEL = genai.GenerativeModel(...)` line in the Python code (around line 35).")
st.info("3. **SAVE and REFRESH** the Streamlit page.")

try:
    found_any_model = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.write(f"**Available Model:** `{m.name}` (Display Name: `{m.display_name}`) -- Copy this exact name!")
            found_any_model = True
    if not found_any_model:
        st.error("No models found that support 'generateContent' with your current API key/configuration. This means your API key might be invalid or restricted for this service.")
        st.info("ACTION REQUIRED: Go to Google AI Studio or Google Cloud Console to generate a new API key or check its permissions.")
        st.stop() # Stop if no models are found, as the app can't function.
except Exception as e:
    st.error(f"ERROR: Could not list models. Please verify your `GEMINI_API_KEY` is correct. Error: {e}")
    st.stop() # Stop if even listing models fails.

st.markdown("---") # Separator for clarity

# Initialize the Gemini model
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CRITICAL FIX LINE - YOU MUST EDIT THIS AFTER DIAGNOSTIC <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# REPLACE 'gemini-1.5-flash' WITH THE EXACT MODEL NAME YOU COPIED FROM THE "Available Model:" list ABOVE.
# For example: GEMINI_MODEL = genai.GenerativeModel('models/text-bison-001')
# For example: GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
try:
    GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash') # <<< CHANGE THIS BASED ON YOUR DIAGNOSTIC OUTPUT
    
    # Verify the selected model actually supports generateContent
    model_info = genai.get_model(GEMINI_MODEL.model_name)
    if 'generateContent' not in model_info.supported_generation_methods:
        st.error(f"ERROR: The model you set ('{GEMINI_MODEL.model_name}') does not support 'generateContent'. Please choose another from the list above and update the code.")
        st.stop()

except Exception as e:
    st.error(f"FATAL ERROR: Could not initialize the Gemini model you specified. Please ensure you pasted the correct model name from the diagnostic. Details: {e}")
    st.stop()


# --- JSearch API Configuration ---
JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com/"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": JSEARCH_API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

# --- Helper Functions (rest of your functions remain the same) ---

def extract_text_from_pdf(uploaded_file):
    """
    Extracts text content from an uploaded PDF file.
    """
    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}. Please ensure it's a valid PDF.")
            return None
    return None

def analyze_resume_with_gemini(resume_text, job_role):
    """
    Sends resume text and job role to Gemini API for analysis using the client library.
    Prompt engineering is crucial here for detailed output.
    """
    if not resume_text:
        return {"error": "Resume text is empty."}
    
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
        "improvement_areas": list of str
    }}
    Ensure the output is valid JSON and nothing else.
    """

    try:
        response = GEMINI_MODEL.generate_content(prompt)
        gemini_output_text = response.text
        gemini_output_text = gemini_output_text.replace("```json", "").replace("```", "").strip()

        try:
            analysis_result = json.loads(gemini_output_text)
            return analysis_result
        except json.JSONDecodeError:
            st.warning(f"Gemini did not return a perfect JSON. Raw output: {gemini_output_text}")
            return {"error": "JSON parsing failed from Gemini output", "raw_output": gemini_output_text}

    except Exception as e:
        st.error(f"Error calling Gemini API for resume analysis: {e}")
        return {"error": str(e)}

def get_job_recommendations(query, num_jobs=10):
    """
    Fetches job listings using the JSearch API.
    """
    if not JSEARCH_API_KEY:
        st.error("JSearch API Key is not set. Please update the JSEARCH_API_KEY.")
        return []

    url = f"{JSEARCH_BASE_URL}search"
    querystring = {
        "query": query,
        "num_pages": "1",
        "date_posted": "week",
        "job_requirements": "entry_level"
    }

    try:
        response = requests.get(url, headers=JSEARCH_HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        if data and data.get('status') == 'OK' and 'data' in data:
            jobs = []
            for job in data['data'][:num_jobs]:
                jobs.append({
                    "title": job.get('job_title', 'N/A'),
                    "company": job.get('employer_name', 'N/A'),
                    "location": job.get('job_city', 'N/A') + ", " + job.get('job_state', 'N/A') if job.get('job_city') else job.get('job_country', 'N/A'),
                    "description": job.get('job_description', 'N/A')[:200] + "..." if job.get('job_description') else 'N/A',
                    "link": job.get('job_apply_link', job.get('job_google_link', '#'))
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
    Generate at least 5 distinct recommendations. Ensure the output is valid JSON and nothing else.
    """
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        gemini_output_text = response.text
        gemini_output_text = gemini_output_text.replace("```json", "").replace("```", "").strip()
        
        try:
            recommendations = json.loads(gemini_output_text)
            return recommendations
        except json.JSONDecodeError:
            st.warning(f"Gemini did not return a perfect JSON for recommendations. Raw: {gemini_output_text}")
            return [{"type": "Text", "title": "Parsing Error", "description": "Raw output from Gemini: " + gemini_output_text, "link": "#"}]
    except Exception as e:
        st.error(f"Error calling Gemini API for recommendations: {e}")
        return [{"type": "Error", "title": "API Call Failed", "description": str(e), "link": "#"}]

def get_chatbot_response(user_query):
    """
    Generates a chatbot response using Gemini API.
    """
    prompt = f"""
    You are an AI career assistant. Respond to the user's query professionally and helpfully.
    You can provide resume improvement tips, career guidance, job search help, or course clarification.
    Keep responses concise and directly address the user's question.

    User Query: {user_query}
    """
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text
    except Exception as e:
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
col1, col2 = st.columns([0.6, 0.4])

with col1:
    st.subheader("1. Upload Your Resume (PDF)")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    st.subheader("2. Select Your Desired Job Role")
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
                    st.session_state['resume_text'] = resume_text
                    st.session_state['selected_role'] = selected_role

                    st.info("Performing AI-based resume analysis...")
                    resume_analysis = analyze_resume_with_gemini(resume_text, selected_role)
                    st.session_state['resume_analysis'] = resume_analysis

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
                        
                        st.subheader("📈 Visualizations")
                        
                        if 'improvement_areas' in resume_analysis and resume_analysis['improvement_areas']:
                            skill_gaps_for_display = [re.sub(r'^\d+\.\s*', '', area).strip() for area in resume_analysis['improvement_areas']]
                            st.write("### Recommended Improvement Areas:")
                            for i, area in enumerate(skill_gaps_for_display):
                                st.markdown(f"- {area}")
                        else:
                            skill_gaps_for_display = ["Data Structures & Algorithms", "Cloud Computing (AWS/Azure)", "Advanced SQL"]
                            st.write("### Recommended Improvement Areas: (Based on general gaps for this role)")
                            for i, area in enumerate(skill_gaps_for_display):
                                st.markdown(f"- {area}")
                        
                        df_skills = pd.DataFrame({
                            'Category': ['Matched Skills', 'Skill Gaps'],
                            'Percentage': [resume_analysis.get('ats_score', 70), 100 - resume_analysis.get('ats_score', 70)]
                        })
                        fig_skill_gap = px.bar(df_skills, x='Category', y='Percentage',
                                            title='Skill Match vs. Gap',
                                            color='Category',
                                            color_discrete_map={'Matched Skills': 'lightblue', 'Skill Gaps': 'lightcoral'})
                        st.plotly_chart(fig_skill_gap, use_container_width=True)

                        st.subheader("📚 Learning Recommendations")
                        st.info("Generating personalized learning recommendations...")
                        learning_recs = get_learning_recommendations_gemini(skill_gaps_for_display, selected_role)
                        st.session_state['learning_recs'] = learning_recs

                        if learning_recs and not any("Error" in rec.get('type', '') for rec in learning_recs):
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
                            if learning_recs: st.json(learning_recs)

                        st.subheader("💼 Entry-Level Job Recommendations")
                        st.info("Fetching real-time entry-level job listings...")
                        job_recommendations = get_job_recommendations(selected_role + " entry level", num_jobs=10)
                        st.session_state['job_recommendations'] = job_recommendations

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
                        st.error("Failed to analyze resume. Please check the API key, the prompt formatting, or try again with a different model if issues persist.")
                        if resume_analysis: st.json(resume_analysis)
                else:
                    st.error("Could not extract text from the uploaded PDF. Please ensure it's a searchable PDF.")
    else:
        st.info("Please upload your resume and select a job role to begin the analysis.")

st.markdown("---")
st.caption("Powered by Google Gemini & JSearch APIs")
