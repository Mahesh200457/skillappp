import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
from typing import List, Dict
from io import BytesIO
import re
import json
from datetime import datetime

# 🎓 FREE VERSION FOR STUDENTS - NO API REQUIRED!
st.set_page_config(
    page_title="Free Student Skill Gap Analyzer", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 Neumorphism Design CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: linear-gradient(145deg, #ffffff, #e6e6e6);
        padding: 2.5rem;
        border-radius: 25px;
        color: #333;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            20px 20px 60px #bebebe,
            -20px -20px 60px #ffffff;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .main-header h1 {
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .neumorphic-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 
            15px 15px 30px #d1d1d1,
            -15px -15px 30px #ffffff;
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
    }
    
    .neumorphic-card:hover {
        transform: translateY(-5px);
        box-shadow: 
            20px 20px 40px #d1d1d1,
            -20px -20px 40px #ffffff;
    }
    
    .skill-badge {
        display: inline-block;
        background: linear-gradient(145deg, #667eea, #764ba2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 
            5px 5px 10px #bebebe,
            -5px -5px 10px #ffffff;
        transition: all 0.3s ease;
    }
    
    .skill-badge:hover {
        transform: scale(1.05);
        box-shadow: 
            8px 8px 15px #bebebe,
            -8px -8px 15px #ffffff;
    }
    
    .missing-skill-badge {
        display: inline-block;
        background: linear-gradient(145deg, #ff6b6b, #ee5a52);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 
            5px 5px 10px #bebebe,
            -5px -5px 10px #ffffff;
        transition: all 0.3s ease;
    }
    
    .missing-skill-badge:hover {
        transform: scale(1.05);
        box-shadow: 
            8px 8px 15px #bebebe,
            -8px -8px 15px #ffffff;
    }
    
    .success-box {
        background: linear-gradient(145deg, #51cf66, #40c057);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 
            10px 10px 20px #bebebe,
            -10px -10px 20px #ffffff;
        font-weight: 500;
    }
    
    .warning-box {
        background: linear-gradient(145deg, #ffd43b, #fab005);
        color: #333;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 
            10px 10px 20px #bebebe,
            -10px -10px 20px #ffffff;
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(145deg, #74c0fc, #339af0);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 
            10px 10px 20px #bebebe,
            -10px -10px 20px #ffffff;
        font-weight: 500;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 
            15px 15px 30px #d1d1d1,
            -15px -15px 30px #ffffff;
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 
            18px 18px 35px #d1d1d1,
            -18px -18px 35px #ffffff;
    }
    
    .sidebar-info {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 
            10px 10px 20px #d1d1d1,
            -10px -10px 20px #ffffff;
        border-left: 4px solid #667eea;
    }
    
    .job-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 
            15px 15px 30px #d1d1d1,
            -15px -15px 30px #ffffff;
        border-left: 5px solid #51cf66;
        transition: all 0.3s ease;
    }
    
    .job-card:hover {
        transform: translateY(-3px);
        box-shadow: 
            20px 20px 40px #d1d1d1,
            -20px -20px 40px #ffffff;
    }
    
    .stButton > button {
        background: linear-gradient(145deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        box-shadow: 
            8px 8px 16px #bebebe,
            -8px -8px 16px #ffffff;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 
            12px 12px 24px #bebebe,
            -12px -12px 24px #ffffff;
    }
    
    .stSelectbox > div > div {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 15px;
        box-shadow: 
            inset 5px 5px 10px #d1d1d1,
            inset -5px -5px 10px #ffffff;
    }
    
    .student-badge {
        background: linear-gradient(45deg, #ff6b6b, #ffd93d);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0;
        box-shadow: 
            5px 5px 10px #bebebe,
            -5px -5px 10px #ffffff;
    }
    
    .free-badge {
        background: linear-gradient(45deg, #51cf66, #40c057);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 1rem;
        box-shadow: 
            3px 3px 6px #bebebe,
            -3px -3px 6px #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# 🎨 Main header with neumorphism design
st.markdown("""
<div class="main-header">
    <h1>🎓 Free Student Skill Gap Analyzer</h1>
    <div class="student-badge">100% Free for Students</div>
    <div class="free-badge">No API Required</div>
    <p style="margin-top: 1rem; font-size: 1.1rem; color: #666;">
        Transform your career with AI-free insights • Find skill gaps • Get personalized learning paths • Discover opportunities
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------------- Built-in Knowledge Base (No API Required) ----------------------------
SKILL_DATABASE = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Ruby", "Go", "Rust", "Swift",
        "Kotlin", "TypeScript", "Scala", "R", "MATLAB", "Perl", "Dart", "Objective-C"
    ],
    "web_technologies": [
        "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django",
        "Flask", "Spring Boot", "Laravel", "Ruby on Rails", "ASP.NET", "jQuery", "Bootstrap",
        "Tailwind CSS", "SASS", "LESS", "Webpack", "Vite"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "SQL Server",
        "Cassandra", "DynamoDB", "Firebase", "Elasticsearch", "Neo4j"
    ],
    "cloud_devops": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub",
        "GitLab", "CI/CD", "Terraform", "Ansible", "Linux", "Bash", "PowerShell"
    ],
    "data_science": [
        "Machine Learning", "Deep Learning", "Data Analysis", "Statistics", "Pandas",
        "NumPy", "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow", "PyTorch",
        "Jupyter", "Tableau", "Power BI", "Excel", "SQL", "Big Data", "Hadoop", "Spark"
    ],
    "mobile_development": [
        "Android", "iOS", "React Native", "Flutter", "Xamarin", "Ionic", "Swift",
        "Kotlin", "Java", "Objective-C", "Dart"
    ],
    "soft_skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Critical Thinking",
        "Time Management", "Project Management", "Agile", "Scrum", "Presentation Skills",
        "Analytical Thinking", "Creativity", "Adaptability", "Collaboration"
    ]
}

JOB_REQUIREMENTS = {
    "Software Developer": {
        "technical": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git", "HTML", "CSS", "REST APIs", "Testing"],
        "soft": ["Problem Solving", "Communication", "Teamwork", "Debugging", "Agile"]
    },
    "Full Stack Developer": {
        "technical": ["JavaScript", "React", "Node.js", "Python", "SQL", "MongoDB", "Express.js", "HTML", "CSS", "Git", "REST APIs"],
        "soft": ["Problem Solving", "Communication", "Project Management", "Time Management", "Adaptability"]
    },
    "Frontend Developer": {
        "technical": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Vue.js", "Angular", "Webpack", "SASS", "Bootstrap"],
        "soft": ["Creativity", "Attention to Detail", "Communication", "Problem Solving", "Collaboration"]
    },
    "Backend Developer": {
        "technical": ["Python", "Java", "Node.js", "SQL", "MongoDB", "REST APIs", "Docker", "AWS", "Git", "Linux"],
        "soft": ["Problem Solving", "Analytical Thinking", "Communication", "Teamwork", "Critical Thinking"]
    },
    "Data Scientist": {
        "technical": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Matplotlib", "Jupyter", "TensorFlow"],
        "soft": ["Analytical Thinking", "Problem Solving", "Communication", "Critical Thinking", "Presentation Skills"]
    },
    "Data Analyst": {
        "technical": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Statistics", "Data Analysis", "Pandas", "R"],
        "soft": ["Analytical Thinking", "Communication", "Attention to Detail", "Problem Solving", "Critical Thinking"]
    },
    "Mobile App Developer": {
        "technical": ["Java", "Kotlin", "Swift", "React Native", "Flutter", "Android", "iOS", "Git", "REST APIs"],
        "soft": ["Problem Solving", "Creativity", "Communication", "Teamwork", "Adaptability"]
    },
    "DevOps Engineer": {
        "technical": ["Docker", "Kubernetes", "AWS", "Jenkins", "Git", "Linux", "Bash", "CI/CD", "Terraform", "Ansible"],
        "soft": ["Problem Solving", "Communication", "Teamwork", "Critical Thinking", "Time Management"]
    },
    "UI/UX Designer": {
        "technical": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "HTML", "CSS", "JavaScript", "Prototyping"],
        "soft": ["Creativity", "Communication", "Empathy", "Problem Solving", "Attention to Detail"]
    },
    "Cybersecurity Analyst": {
        "technical": ["Network Security", "Penetration Testing", "Linux", "Python", "Wireshark", "Nmap", "Metasploit", "SIEM"],
        "soft": ["Analytical Thinking", "Problem Solving", "Attention to Detail", "Communication", "Critical Thinking"]
    }
}

SAMPLE_JOBS = {
    "Software Developer": [
        {
            "title": "Junior Software Developer",
            "company": "TechStart Solutions",
            "location": "Bangalore, India",
            "type": "Full-time",
            "salary": "₹4-6 LPA",
            "description": "Join our dynamic team to build innovative software solutions using modern technologies.",
            "posted": "2024-01-15"
        },
        {
            "title": "Python Developer",
            "company": "DataFlow Systems",
            "location": "Hyderabad, India",
            "type": "Full-time",
            "salary": "₹5-8 LPA",
            "description": "Develop scalable applications using Python, Django, and modern web technologies.",
            "posted": "2024-01-14"
        },
        {
            "title": "Software Engineer Trainee",
            "company": "InnovateTech",
            "location": "Pune, India",
            "type": "Full-time",
            "salary": "₹3.5-5 LPA",
            "description": "Perfect opportunity for fresh graduates to start their software development career.",
            "posted": "2024-01-13"
        }
    ],
    "Data Scientist": [
        {
            "title": "Junior Data Scientist",
            "company": "Analytics Pro",
            "location": "Mumbai, India",
            "type": "Full-time",
            "salary": "₹6-9 LPA",
            "description": "Work with big data to extract insights and build predictive models.",
            "posted": "2024-01-15"
        },
        {
            "title": "Data Analyst",
            "company": "Business Intelligence Corp",
            "location": "Chennai, India",
            "type": "Full-time",
            "salary": "₹4-7 LPA",
            "description": "Analyze business data and create meaningful reports and dashboards.",
            "posted": "2024-01-14"
        }
    ],
    "Frontend Developer": [
        {
            "title": "React Developer",
            "company": "WebCraft Studios",
            "location": "Bangalore, India",
            "type": "Full-time",
            "salary": "₹5-8 LPA",
            "description": "Build responsive and interactive user interfaces using React and modern CSS.",
            "posted": "2024-01-15"
        },
        {
            "title": "UI Developer",
            "company": "DesignTech Solutions",
            "location": "Gurgaon, India",
            "type": "Full-time",
            "salary": "₹4-6 LPA",
            "description": "Create beautiful and functional user interfaces for web applications.",
            "posted": "2024-01-14"
        }
    ]
}

LEARNING_RESOURCES = {
    "Python": {
        "course": "Python for Everybody (Coursera) - University of Michigan",
        "free": "Python.org Tutorial & freeCodeCamp Python Course",
        "project": "Build a personal expense tracker with GUI",
        "time": "4-6 weeks"
    },
    "JavaScript": {
        "course": "JavaScript Algorithms and Data Structures (freeCodeCamp)",
        "free": "MDN Web Docs & JavaScript.info",
        "project": "Create an interactive to-do list application",
        "time": "3-5 weeks"
    },
    "React": {
        "course": "React - The Complete Guide (Udemy)",
        "free": "React Official Documentation & YouTube tutorials",
        "project": "Build a weather app with API integration",
        "time": "4-6 weeks"
    },
    "SQL": {
        "course": "SQL for Data Science (Coursera)",
        "free": "W3Schools SQL Tutorial & SQLBolt",
        "project": "Design and query a library management database",
        "time": "2-3 weeks"
    },
    "Machine Learning": {
        "course": "Machine Learning Course (Coursera) - Andrew Ng",
        "free": "Kaggle Learn & YouTube ML tutorials",
        "project": "Build a house price prediction model",
        "time": "8-10 weeks"
    },
    "Git": {
        "course": "Git Complete: The definitive guide (Udemy)",
        "free": "Git Documentation & GitHub Learning Lab",
        "project": "Contribute to an open-source project",
        "time": "1-2 weeks"
    },
    "HTML": {
        "course": "HTML5 and CSS3 Fundamentals (edX)",
        "free": "MDN Web Docs & freeCodeCamp",
        "project": "Create a personal portfolio website",
        "time": "2-3 weeks"
    },
    "CSS": {
        "course": "Advanced CSS and Sass (Udemy)",
        "free": "CSS-Tricks & MDN CSS Documentation",
        "project": "Build a responsive restaurant website",
        "time": "3-4 weeks"
    }
}

# ----------------------- Offline Analysis Functions ----------------------------
def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF"""
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

def extract_skills_from_text(text: str) -> List[str]:
    """Extract skills from resume text using pattern matching"""
    found_skills = []
    text_lower = text.lower()
    
    # Check all skill categories
    for category, skills in SKILL_DATABASE.items():
        for skill in skills:
            # More flexible matching
            skill_variations = [
                skill.lower(),
                skill.lower().replace('.', ''),
                skill.lower().replace(' ', ''),
                skill.lower().replace('-', ''),
            ]
            
            for variation in skill_variations:
                if variation in text_lower:
                    if skill not in found_skills:
                        found_skills.append(skill)
                    break
    
    return found_skills

def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information from resume text"""
    info = {
        'email': 'Not specified',
        'phone': 'Not specified',
        'name': 'Not specified'
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        info['email'] = emails[0]
    
    # Extract phone
    phone_patterns = [
        r'\+91[\s-]?\d{10}',
        r'\d{10}',
        r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}',
        r'\d{3}[\s-]?\d{3}[\s-]?\d{4}'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            info['phone'] = phones[0]
            break
    
    # Extract name (first few words that look like a name)
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and len(line.split()) <= 4 and len(line) > 3:
            # Simple heuristic: if it's not an email, phone, or common resume words
            if '@' not in line and not re.search(r'\d{10}', line):
                common_words = ['resume', 'cv', 'curriculum', 'vitae', 'profile', 'summary']
                if not any(word in line.lower() for word in common_words):
                    info['name'] = line
                    break
    
    return info

def analyze_resume_offline(text: str) -> Dict:
    """Analyze resume without using any APIs"""
    contact_info = extract_contact_info(text)
    skills = extract_skills_from_text(text)
    
    # Extract education info
    education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd', 'diploma']
    education_info = "Not specified"
    
    text_lower = text.lower()
    for keyword in education_keywords:
        if keyword in text_lower:
            # Find the section with education
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if keyword in line.lower():
                    # Get next few lines as education info
                    edu_lines = lines[i:i+3]
                    education_info = ' '.join(edu_lines).strip()[:200]
                    break
            break
    
    # Extract experience info
    experience_keywords = ['experience', 'work', 'employment', 'job', 'position', 'role']
    experience_info = "Not specified"
    
    for keyword in experience_keywords:
        if keyword in text_lower:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if keyword in line.lower():
                    exp_lines = lines[i:i+5]
                    experience_info = ' '.join(exp_lines).strip()[:300]
                    break
            break
    
    # Extract certifications
    cert_keywords = ['certification', 'certificate', 'certified', 'course', 'training']
    certifications = "Not specified"
    
    for keyword in cert_keywords:
        if keyword in text_lower:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if keyword in line.lower():
                    cert_lines = lines[i:i+3]
                    certifications = ' '.join(cert_lines).strip()[:200]
                    break
            break
    
    return {
        'Name': contact_info['name'],
        'Email': contact_info['email'],
        'Phone': contact_info['phone'],
        'Skills': ', '.join(skills) if skills else 'Not specified',
        'Education': education_info,
        'Experience': experience_info,
        'Certifications': certifications
    }

def analyze_skill_gaps(user_skills: List[str], required_skills: List[str]) -> Dict:
    """Analyze skill gaps with fuzzy matching"""
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
            # Fuzzy matching
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

def generate_learning_recommendations(missing_skills: List[str]) -> str:
    """Generate learning recommendations from built-in database"""
    if not missing_skills:
        return "🎉 Excellent! You have all the required skills for this role. Consider exploring advanced topics to stay ahead!"
    
    recommendations = "# 📚 Your Personalized Learning Path\n\n"
    recommendations += "*Completely free resources curated for students!*\n\n"
    
    for i, skill in enumerate(missing_skills[:8], 1):
        recommendations += f"## {i}. {skill}\n\n"
        
        if skill in LEARNING_RESOURCES:
            resource = LEARNING_RESOURCES[skill]
            recommendations += f"**📚 Recommended Course:** {resource['course']}\n\n"
            recommendations += f"**🆓 Free Resources:** {resource['free']}\n\n"
            recommendations += f"**🛠️ Practice Project:** {resource['project']}\n\n"
            recommendations += f"**⏱️ Estimated Time:** {resource['time']}\n\n"
        else:
            recommendations += f"**📚 Recommended Course:** Search for '{skill}' courses on Coursera, edX, or Udemy\n\n"
            recommendations += f"**🆓 Free Resources:** YouTube tutorials and official documentation for {skill}\n\n"
            recommendations += f"**🛠️ Practice Project:** Build a small project using {skill}\n\n"
            recommendations += f"**⏱️ Estimated Time:** 2-4 weeks\n\n"
        
        recommendations += "---\n\n"
    
    recommendations += "## 💡 Additional Tips for Students:\n\n"
    recommendations += "- Start with free resources before investing in paid courses\n"
    recommendations += "- Join online communities and forums for support\n"
    recommendations += "- Build a portfolio showcasing your projects\n"
    recommendations += "- Practice coding daily, even if just for 30 minutes\n"
    recommendations += "- Contribute to open-source projects on GitHub\n\n"
    
    return recommendations

def create_student_report(analysis: Dict, role: str, gap_analysis: Dict, recommendations: str, jobs: List[Dict]) -> BytesIO:
    """Generate a student-friendly PDF report"""
    try:
        pdf = FPDF(format='A4')
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 15, "Student Skill Gap Analysis Report", ln=True, align='C')
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%B %d, %Y')}", ln=True, align='C')
        pdf.ln(10)
        
        # Personal Information
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Personal Information", ln=True)
        pdf.set_font("Arial", "", 11)
        
        name = analysis.get("Name", "Student")
        email = analysis.get("Email", "Not specified")
        phone = analysis.get("Phone", "Not specified")
        
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Email: {email}", ln=True)
        pdf.cell(0, 8, f"Phone: {phone}", ln=True)
        pdf.cell(0, 8, f"Target Role: {role}", ln=True)
        pdf.ln(5)
        
        # Skills Analysis
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Skills Analysis Summary", ln=True)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(0, 8, f"Skills Match: {gap_analysis['match_percentage']}%", ln=True)
        pdf.cell(0, 8, f"Skills You Have: {len(gap_analysis['matched'])}", ln=True)
        pdf.cell(0, 8, f"Skills to Learn: {len(gap_analysis['missing'])}", ln=True)
        pdf.ln(5)
        
        # Matched Skills
        if gap_analysis['matched']:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Your Existing Skills:", ln=True)
            pdf.set_font("Arial", "", 10)
            for skill in gap_analysis['matched'][:15]:
                pdf.cell(0, 6, f"✓ {skill}", ln=True)
            pdf.ln(5)
        
        # Skills to Develop
        if gap_analysis['missing']:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Skills to Develop:", ln=True)
            pdf.set_font("Arial", "", 10)
            for skill in gap_analysis['missing'][:15]:
                pdf.cell(0, 6, f"○ {skill}", ln=True)
            pdf.ln(5)
        
        # Learning Plan
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Your Learning Action Plan", ln=True)
        pdf.set_font("Arial", "", 9)
        
        # Simple text version of recommendations
        simple_recs = f"Focus on learning these {len(gap_analysis['missing'])} skills:\n\n"
        for i, skill in enumerate(gap_analysis['missing'][:8], 1):
            simple_recs += f"{i}. {skill}\n"
            if skill in LEARNING_RESOURCES:
                simple_recs += f"   - Course: {LEARNING_RESOURCES[skill]['course']}\n"
                simple_recs += f"   - Time: {LEARNING_RESOURCES[skill]['time']}\n\n"
            else:
                simple_recs += f"   - Search for free tutorials online\n"
                simple_recs += f"   - Time: 2-4 weeks\n\n"
        
        # Split into lines and add to PDF
        lines = simple_recs.split('\n')
        for line in lines[:40]:  # Limit lines
            if line.strip():
                pdf.multi_cell(0, 5, line.strip())
        
        # Job Market Info
        if jobs:
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Job Opportunities for Students", ln=True)
            pdf.set_font("Arial", "", 10)
            
            for i, job in enumerate(jobs[:5], 1):
                pdf.set_font("Arial", "B", 11)
                pdf.cell(0, 8, f"{i}. {job['title']} at {job['company']}", ln=True)
                pdf.set_font("Arial", "", 9)
                pdf.cell(0, 6, f"Location: {job['location']}", ln=True)
                pdf.cell(0, 6, f"Salary: {job['salary']}", ln=True)
                pdf.cell(0, 6, f"Type: {job['type']}", ln=True)
                pdf.ln(3)
        
        # Generate PDF
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        return BytesIO()

# ----------------------- Sidebar ----------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-info">
        <h3>🎓 For Students, By Students</h3>
        <p><strong>100% Free • No API Required • Works Offline</strong></p>
        <ol>
            <li>Upload your PDF resume</li>
            <li>Get instant skill analysis</li>
            <li>Select target job role</li>
            <li>Discover skill gaps</li>
            <li>Get free learning resources</li>
            <li>Find student-friendly jobs</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class="sidebar-info">
        <h4>💡 Student Success Tips</h4>
        <ul>
            <li>Focus on 2-3 skills at a time</li>
            <li>Build projects while learning</li>
            <li>Join coding communities</li>
            <li>Practice daily coding</li>
            <li>Create a GitHub portfolio</li>
            <li>Apply for internships early</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div class="sidebar-info">
        <h4>🆓 Free Learning Resources</h4>
        <ul>
            <li><strong>Coding:</strong> freeCodeCamp, Codecademy</li>
            <li><strong>Courses:</strong> Coursera, edX, Khan Academy</li>
            <li><strong>Practice:</strong> HackerRank, LeetCode</li>
            <li><strong>Projects:</strong> GitHub, CodePen</li>
            <li><strong>Community:</strong> Stack Overflow, Reddit</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ----------------------- Main Application ----------------------------

# File Upload Section
st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
st.subheader("📤 Upload Your Resume")
st.markdown("*Upload your PDF resume for instant analysis - completely free!*")

uploaded_file = st.file_uploader(
    "Choose your PDF resume file", 
    type=["pdf"],
    help="Upload a PDF version of your resume for analysis"
)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # Process the uploaded file
    with st.spinner("📄 Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    
    if resume_text:
        st.markdown('<div class="success-box">✅ Resume uploaded and processed successfully!</div>', unsafe_allow_html=True)
        
        # Show text preview
        with st.expander("📄 Resume Text Preview"):
            st.text_area("Extracted Text", resume_text[:2000] + "..." if len(resume_text) > 2000 else resume_text, height=200)
        
        # Offline Analysis
        with st.spinner("🔍 Analyzing your resume (offline analysis)..."):
            analysis = analyze_resume_offline(resume_text)
        
        # Display Analysis Results
        st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
        st.subheader("📊 Resume Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Personal Information**")
            st.write(f"**Name:** {analysis.get('Name', 'Not specified')}")
            st.write(f"**Email:** {analysis.get('Email', 'Not specified')}")
            st.write(f"**Phone:** {analysis.get('Phone', 'Not specified')}")
        
        with col2:
            st.markdown("**🎓 Education & Experience**")
            education = analysis.get('Education', 'Not specified')
            st.write(f"**Education:** {education[:100]}..." if len(education) > 100 else f"**Education:** {education}")
            certifications = analysis.get('Certifications', 'Not specified')
            st.write(f"**Certifications:** {certifications[:100]}..." if len(certifications) > 100 else f"**Certifications:** {certifications}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Skills Display
        skills_text = analysis.get('Skills', '')
        if skills_text and skills_text != 'Not specified':
            user_skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            
            st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
            st.markdown("**🛠️ Your Detected Skills**")
            skills_html = ""
            for skill in user_skills:
                skills_html += f'<span class="skill-badge">{skill}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            user_skills = []
            st.markdown('<div class="warning-box">⚠️ No skills detected in your resume. Please ensure your skills are clearly listed in a skills section.</div>', unsafe_allow_html=True)
        
        # Job Role Selection
        st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
        st.subheader("🎯 Select Your Target Role")
        st.markdown("*Choose the role you're aiming for to get personalized analysis*")
        
        job_categories = {
            "💻 Software Development": ["Software Developer", "Full Stack Developer", "Frontend Developer", "Backend Developer", "Mobile App Developer"],
            "📊 Data & Analytics": ["Data Analyst", "Data Scientist"],
            "🎨 Design & UX": ["UI/UX Designer"],
            "🔒 Cybersecurity": ["Cybersecurity Analyst"],
            "☁️ Cloud & DevOps": ["DevOps Engineer"]
        }
        
        selected_category = st.selectbox("Choose a category:", list(job_categories.keys()))
        selected_role = st.selectbox("Select specific role:", job_categories[selected_category])
        st.markdown('</div>', unsafe_allow_html=True)
        
        if selected_role:
            # Get job requirements
            job_req = JOB_REQUIREMENTS.get(selected_role, {"technical": [], "soft": []})
            required_skills = job_req["technical"] + job_req["soft"]
            
            # Skill Gap Analysis
            gap_analysis = analyze_skill_gaps(user_skills, required_skills)
            
            # Skills Gap Visualization
            st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
            st.subheader("🔍 Your Skill Gap Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "🎯 Skills Match", 
                    f"{gap_analysis['match_percentage']}%",
                    delta=f"{len(gap_analysis['matched'])} skills"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "✅ Skills You Have", 
                    len(gap_analysis['matched']),
                    delta="Ready to use"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric(
                    "📚 Skills to Learn", 
                    len(gap_analysis['missing']),
                    delta="Growth opportunities"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Skills Breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
                if gap_analysis['matched']:
                    st.markdown("**✅ Your Matching Skills**")
                    matched_html = ""
                    for skill in gap_analysis['matched']:
                        matched_html += f'<span class="skill-badge">{skill}</span>'
                    st.markdown(matched_html, unsafe_allow_html=True)
                else:
                    st.info("No matching skills found. This is a great opportunity to start learning!")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
                if gap_analysis['missing']:
                    st.markdown("**📚 Skills to Develop**")
                    missing_html = ""
                    for skill in gap_analysis['missing']:
                        missing_html += f'<span class="missing-skill-badge">{skill}</span>'
                    st.markdown(missing_html, unsafe_allow_html=True)
                else:
                    st.success("🎉 You have all the required skills!")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Skill Gap Visualization Chart
            if gap_analysis['matched'] or gap_analysis['missing']:
                fig = go.Figure(data=[
                    go.Bar(
                        name='Skills You Have',
                        x=['Skills Analysis'],
                        y=[len(gap_analysis['matched'])],
                        marker_color='#51cf66',
                        text=[len(gap_analysis['matched'])],
                        textposition='auto',
                    ),
                    go.Bar(
                        name='Skills to Learn',
                        x=['Skills Analysis'],
                        y=[len(gap_analysis['missing'])],
                        marker_color='#ff6b6b',
                        text=[len(gap_analysis['missing'])],
                        textposition='auto',
                    )
                ])
                
                fig.update_layout(
                    title='Your Skill Gap Analysis',
                    barmode='stack',
                    height=400,
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Learning Recommendations
            st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
            st.subheader("📚 Your Free Learning Path")
            st.markdown("*Curated free resources perfect for students*")
            
            if gap_analysis['missing']:
                recommendations = generate_learning_recommendations(gap_analysis['missing'])
                st.markdown(recommendations)
            else:
                st.markdown('<div class="success-box">🎉 Congratulations! You have all the required skills. Consider exploring advanced topics or leadership skills to advance your career further.</div>', unsafe_allow_html=True)
                recommendations = "All required skills are present. Focus on advanced topics and leadership development."
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Job Opportunities
            st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
            st.subheader("💼 Student-Friendly Job Opportunities")
            
            jobs = SAMPLE_JOBS.get(selected_role, [])
            if jobs:
                st.info(f"Found {len(jobs)} entry-level opportunities for {selected_role}")
                
                for i, job in enumerate(jobs):
                    st.markdown('<div class="job-card">', unsafe_allow_html=True)
                    st.markdown(f"### 🏢 {job['title']}")
                    st.markdown(f"**Company:** {job['company']}")
                    st.markdown(f"**📍 Location:** {job['location']}")
                    st.markdown(f"**💼 Type:** {job['type']}")
                    st.markdown(f"**💰 Salary:** {job['salary']}")
                    st.markdown(f"**📝 Description:** {job['description']}")
                    st.markdown(f"**📅 Posted:** {job['posted']}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">💡 Keep checking job portals like Naukri, LinkedIn, and company websites for fresh opportunities!</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Report Generation
            st.markdown('<div class="neumorphic-card">', unsafe_allow_html=True)
            st.subheader("📥 Download Your Career Report")
            st.markdown("*Get a comprehensive PDF report with your analysis and learning plan*")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate Student Report", use_container_width=True):
                    with st.spinner("📊 Creating your personalized report..."):
                        try:
                            report_buffer = create_student_report(
                                analysis, selected_role, gap_analysis, recommendations, jobs
                            )
                            
                            if report_buffer.getvalue():
                                st.success("✅ Report generated successfully!")
                                
                                st.download_button(
                                    label="⬇️ Download PDF Report",
                                    data=report_buffer,
                                    file_name=f"Student_Career_Report_{selected_role.replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            else:
                                st.error("❌ Error generating report. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error generating report: {str(e)}")
            
            with col2:
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.markdown(f"""
                **📊 Your Analysis Summary**
                - Skills Analyzed: {len(required_skills)}
                - Match Rate: {gap_analysis['match_percentage']}%
                - Jobs Found: {len(jobs)}
                - Learning Resources: ✅ Generated
                - Report Type: Student-Friendly
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="neumorphic-card" style="text-align: center;">
    <h4>🎓 Built for Students, By Students</h4>
    <p><strong>100% Free • No API Required • Privacy First</strong></p>
    <p>Your resume data is processed locally and never stored on our servers.</p>
    <p>💡 <strong>Pro Tip:</strong> Bookmark this tool and use it regularly to track your skill development!</p>
    <div class="student-badge">Keep Learning • Keep Growing • Keep Coding</div>
</div>
""", unsafe_allow_html=True)
