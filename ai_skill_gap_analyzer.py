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
import hashlib

# 🎨 Professional Streamlit Configuration
st.set_page_config(
    page_title="Professional Skill Gap Analyzer", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 Modern Professional CSS Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Header Styling */
    .hero-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.05)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    
    /* Professional Cards */
    .pro-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .pro-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
    }
    
    .pro-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10b981, #3b82f6);
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Skill Badges */
    .skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
        border: none;
    }
    
    .skill-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    .missing-skill-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        transition: all 0.3s ease;
    }
    
    .missing-skill-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
    }
    
    /* Status Boxes */
    .success-box {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
        font-weight: 500;
    }
    
    .warning-box {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.3);
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
        font-weight: 500;
    }
    
    /* Job Cards */
    .job-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #10b981;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .job-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
    }
    
    .job-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .job-company {
        color: #3b82f6;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .job-details {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .job-detail-item {
        background: #f1f5f9;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #475569;
    }
    
    /* Learning Cards */
    .learning-card {
        background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #8b5cf6;
        transition: all 0.3s ease;
    }
    
    .learning-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
    }
    
    .learning-skill-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .learning-resource {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #3b82f6;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
        font-size: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
    }
    
    /* Upload Area */
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Progress Indicators */
    .progress-step {
        display: flex;
        align-items: center;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8fafc;
        border-radius: 12px;
        border-left: 4px solid #e2e8f0;
    }
    
    .progress-step.active {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border-left-color: #3b82f6;
    }
    
    .progress-step.completed {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        border-left-color: #10b981;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-header h1 {
            font-size: 2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .pro-card {
            padding: 1.5rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
    }
</style>
""", unsafe_allow_html=True)

# 🎨 Professional Hero Header
st.markdown("""
<div class="hero-header">
    <h1>🚀 Professional Skill Gap Analyzer</h1>
    <p class="hero-subtitle">Advanced AI-powered career insights for modern professionals • Discover your potential • Bridge skill gaps • Accelerate your career</p>
</div>
""", unsafe_allow_html=True)

# ----------------------- Enhanced Knowledge Base ----------------------------
COMPREHENSIVE_SKILL_DATABASE = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "PHP", "Ruby", "Go", "Rust", 
        "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Dart", "Objective-C", "C", "Assembly",
        "Haskell", "Clojure", "F#", "Erlang", "Elixir", "Julia", "Lua", "VB.NET", "COBOL", "Fortran"
    ],
    "web_technologies": [
        "HTML5", "CSS3", "React", "Angular", "Vue.js", "Node.js", "Express.js", "Django", "Flask",
        "Spring Boot", "Laravel", "Ruby on Rails", "ASP.NET", "jQuery", "Bootstrap", "Tailwind CSS",
        "SASS", "LESS", "Webpack", "Vite", "Next.js", "Nuxt.js", "Svelte", "Gatsby", "GraphQL",
        "REST API", "WebSocket", "PWA", "Responsive Design", "Cross-browser Compatibility"
    ],
    "databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "SQL Server", "Cassandra",
        "DynamoDB", "Firebase", "Elasticsearch", "Neo4j", "CouchDB", "InfluxDB", "MariaDB",
        "Amazon RDS", "Google Cloud SQL", "Azure SQL", "Snowflake", "BigQuery"
    ],
    "cloud_devops": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab",
        "CI/CD", "Terraform", "Ansible", "Linux", "Bash", "PowerShell", "Nginx", "Apache", "Load Balancing",
        "Microservices", "Serverless", "CloudFormation", "Helm", "Prometheus", "Grafana", "ELK Stack"
    ],
    "data_science": [
        "Machine Learning", "Deep Learning", "Data Analysis", "Statistics", "Pandas", "NumPy",
        "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow", "PyTorch", "Jupyter", "Tableau",
        "Power BI", "Excel", "SQL", "Big Data", "Hadoop", "Spark", "Kafka", "Airflow", "MLOps",
        "Feature Engineering", "Model Deployment", "A/B Testing", "Statistical Modeling"
    ],
    "mobile_development": [
        "Android", "iOS", "React Native", "Flutter", "Xamarin", "Ionic", "Swift", "Kotlin", "Java",
        "Objective-C", "Dart", "PhoneGap", "Cordova", "Unity", "Unreal Engine", "ARKit", "ARCore",
        "Mobile UI/UX", "App Store Optimization", "Mobile Security"
    ],
    "soft_skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving", "Critical Thinking",
        "Time Management", "Project Management", "Agile", "Scrum", "Presentation Skills",
        "Analytical Thinking", "Creativity", "Adaptability", "Collaboration", "Negotiation",
        "Emotional Intelligence", "Conflict Resolution", "Decision Making", "Strategic Planning"
    ],
    "design_skills": [
        "UI/UX Design", "Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "InDesign",
        "Prototyping", "Wireframing", "User Research", "Design Systems", "Accessibility",
        "Color Theory", "Typography", "Brand Design", "Motion Graphics", "3D Design"
    ],
    "security_skills": [
        "Cybersecurity", "Network Security", "Penetration Testing", "Ethical Hacking", "OWASP",
        "Security Auditing", "Incident Response", "Risk Assessment", "Compliance", "Encryption",
        "Identity Management", "Vulnerability Assessment", "Security Architecture"
    ]
}

ENHANCED_JOB_REQUIREMENTS = {
    "Software Developer": {
        "technical": ["Python", "JavaScript", "React", "Node.js", "SQL", "Git", "HTML5", "CSS3", "REST API", "Testing", "Docker", "AWS", "MongoDB", "Express.js", "TypeScript"],
        "soft": ["Problem Solving", "Communication", "Teamwork", "Debugging", "Agile", "Critical Thinking", "Time Management", "Adaptability", "Collaboration", "Analytical Thinking"]
    },
    "Full Stack Developer": {
        "technical": ["JavaScript", "React", "Node.js", "Python", "SQL", "MongoDB", "Express.js", "HTML5", "CSS3", "Git", "REST API", "GraphQL", "Docker", "AWS", "TypeScript"],
        "soft": ["Problem Solving", "Communication", "Project Management", "Time Management", "Adaptability", "Leadership", "Teamwork", "Critical Thinking", "Creativity", "Analytical Thinking"]
    },
    "Frontend Developer": {
        "technical": ["JavaScript", "React", "HTML5", "CSS3", "TypeScript", "Vue.js", "Angular", "Webpack", "SASS", "Bootstrap", "Responsive Design", "PWA", "GraphQL", "Next.js", "Tailwind CSS"],
        "soft": ["Creativity", "Attention to Detail", "Communication", "Problem Solving", "Collaboration", "User Empathy", "Design Thinking", "Adaptability", "Time Management", "Critical Thinking"]
    },
    "Backend Developer": {
        "technical": ["Python", "Java", "Node.js", "SQL", "MongoDB", "REST API", "Docker", "AWS", "Git", "Linux", "Microservices", "GraphQL", "Redis", "Kubernetes", "Spring Boot"],
        "soft": ["Problem Solving", "Analytical Thinking", "Communication", "Teamwork", "Critical Thinking", "System Design", "Performance Optimization", "Security Awareness", "Documentation", "Debugging"]
    },
    "Data Scientist": {
        "technical": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Pandas", "NumPy", "Matplotlib", "Jupyter", "TensorFlow", "Scikit-learn", "Deep Learning", "Big Data", "Tableau", "Feature Engineering"],
        "soft": ["Analytical Thinking", "Problem Solving", "Communication", "Critical Thinking", "Presentation Skills", "Business Acumen", "Curiosity", "Statistical Reasoning", "Data Storytelling", "Research Skills"]
    },
    "Data Analyst": {
        "technical": ["SQL", "Python", "Excel", "Tableau", "Power BI", "Statistics", "Data Analysis", "Pandas", "R", "Data Visualization", "ETL", "Business Intelligence", "Google Analytics", "A/B Testing", "Statistical Modeling"],
        "soft": ["Analytical Thinking", "Communication", "Attention to Detail", "Problem Solving", "Critical Thinking", "Business Understanding", "Presentation Skills", "Data Storytelling", "Curiosity", "Time Management"]
    },
    "Mobile App Developer": {
        "technical": ["Java", "Kotlin", "Swift", "React Native", "Flutter", "Android", "iOS", "Git", "REST API", "Mobile UI/UX", "SQLite", "Firebase", "Dart", "Objective-C", "Cross-platform Development"],
        "soft": ["Problem Solving", "Creativity", "Communication", "Teamwork", "Adaptability", "User-Centric Thinking", "Attention to Detail", "Performance Optimization", "Testing Mindset", "Continuous Learning"]
    },
    "DevOps Engineer": {
        "technical": ["Docker", "Kubernetes", "AWS", "Jenkins", "Git", "Linux", "Bash", "CI/CD", "Terraform", "Ansible", "Monitoring", "Prometheus", "Grafana", "Nginx", "Microservices"],
        "soft": ["Problem Solving", "Communication", "Teamwork", "Critical Thinking", "Time Management", "Automation Mindset", "System Thinking", "Collaboration", "Incident Management", "Continuous Improvement"]
    },
    "UI/UX Designer": {
        "technical": ["Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "HTML5", "CSS3", "JavaScript", "Prototyping", "Wireframing", "User Research", "Design Systems", "Accessibility", "Responsive Design", "Usability Testing"],
        "soft": ["Creativity", "Communication", "Empathy", "Problem Solving", "Attention to Detail", "User-Centric Thinking", "Collaboration", "Visual Thinking", "Research Skills", "Adaptability"]
    },
    "Cybersecurity Analyst": {
        "technical": ["Network Security", "Penetration Testing", "Linux", "Python", "Wireshark", "Nmap", "Metasploit", "SIEM", "Incident Response", "Risk Assessment", "Compliance", "Ethical Hacking", "Vulnerability Assessment", "Security Architecture", "Encryption"],
        "soft": ["Analytical Thinking", "Problem Solving", "Attention to Detail", "Communication", "Critical Thinking", "Ethical Mindset", "Continuous Learning", "Risk Assessment", "Documentation", "Team Collaboration"]
    }
}

SAMPLE_JOBS_DATABASE = {
    "Software Developer": [
        {
            "title": "Software Developer",
            "company": "TechCorp Solutions",
            "location": "Bangalore, India",
            "type": "Full-time",
            "salary": "₹6-10 LPA",
            "experience": "0-2 years",
            "description": "Join our innovative team to build cutting-edge software solutions using modern technologies and best practices.",
            "posted": "2024-01-15",
            "skills_required": ["Python", "JavaScript", "React", "SQL", "Git"]
        },
        {
            "title": "Junior Software Engineer",
            "company": "InnovateTech",
            "location": "Hyderabad, India", 
            "type": "Full-time",
            "salary": "₹5-8 LPA",
            "experience": "0-1 years",
            "description": "Perfect opportunity for fresh graduates to start their software development career with mentorship and growth opportunities.",
            "posted": "2024-01-14",
            "skills_required": ["Java", "Spring Boot", "MySQL", "Git", "REST API"]
        },
        {
            "title": "Python Developer",
            "company": "DataFlow Systems",
            "location": "Pune, India",
            "type": "Full-time", 
            "salary": "₹7-12 LPA",
            "experience": "1-3 years",
            "description": "Develop scalable applications using Python, Django, and modern web technologies in an agile environment.",
            "posted": "2024-01-13",
            "skills_required": ["Python", "Django", "PostgreSQL", "Docker", "AWS"]
        }
    ],
    "Data Scientist": [
        {
            "title": "Data Scientist",
            "company": "Analytics Pro",
            "location": "Mumbai, India",
            "type": "Full-time",
            "salary": "₹8-15 LPA", 
            "experience": "1-3 years",
            "description": "Work with big data to extract insights, build predictive models, and drive business decisions through data science.",
            "posted": "2024-01-15",
            "skills_required": ["Python", "Machine Learning", "SQL", "Pandas", "TensorFlow"]
        },
        {
            "title": "Junior Data Analyst",
            "company": "Business Intelligence Corp",
            "location": "Chennai, India",
            "type": "Full-time",
            "salary": "₹5-9 LPA",
            "experience": "0-2 years", 
            "description": "Analyze business data, create meaningful reports and dashboards, and support data-driven decision making.",
            "posted": "2024-01-14",
            "skills_required": ["SQL", "Python", "Tableau", "Excel", "Statistics"]
        }
    ],
    "Frontend Developer": [
        {
            "title": "React Developer",
            "company": "WebCraft Studios", 
            "location": "Bangalore, India",
            "type": "Full-time",
            "salary": "₹6-11 LPA",
            "experience": "1-3 years",
            "description": "Build responsive and interactive user interfaces using React, modern CSS, and cutting-edge frontend technologies.",
            "posted": "2024-01-15",
            "skills_required": ["React", "JavaScript", "HTML5", "CSS3", "TypeScript"]
        },
        {
            "title": "UI Developer",
            "company": "DesignTech Solutions",
            "location": "Gurgaon, India",
            "type": "Full-time",
            "salary": "₹5-9 LPA", 
            "experience": "0-2 years",
            "description": "Create beautiful and functional user interfaces for web applications with focus on user experience and performance.",
            "posted": "2024-01-14",
            "skills_required": ["HTML5", "CSS3", "JavaScript", "Bootstrap", "Responsive Design"]
        }
    ]
}

COMPREHENSIVE_LEARNING_RESOURCES = {
    "Python": {
        "course": "Complete Python Bootcamp (Udemy) - Jose Portilla",
        "free": "Python.org Official Tutorial & Real Python",
        "project": "Build a personal expense tracker with data visualization",
        "time": "6-8 weeks",
        "difficulty": "Beginner to Intermediate",
        "certification": "Python Institute PCAP Certification"
    },
    "JavaScript": {
        "course": "The Complete JavaScript Course (Udemy) - Jonas Schmedtmann", 
        "free": "MDN Web Docs & freeCodeCamp JavaScript Course",
        "project": "Create a dynamic task management application",
        "time": "4-6 weeks",
        "difficulty": "Beginner to Advanced",
        "certification": "JavaScript Institute JSE Certification"
    },
    "React": {
        "course": "React - The Complete Guide (Udemy) - Maximilian Schwarzmüller",
        "free": "React Official Documentation & Scrimba React Course",
        "project": "Build a social media dashboard with real-time updates",
        "time": "5-7 weeks", 
        "difficulty": "Intermediate",
        "certification": "Meta React Developer Certificate"
    },
    "SQL": {
        "course": "The Complete SQL Bootcamp (Udemy) - Jose Portilla",
        "free": "W3Schools SQL Tutorial & SQLBolt Interactive Lessons",
        "project": "Design and optimize a e-commerce database system",
        "time": "3-4 weeks",
        "difficulty": "Beginner to Intermediate", 
        "certification": "Oracle SQL Certification"
    },
    "Machine Learning": {
        "course": "Machine Learning Specialization (Coursera) - Andrew Ng",
        "free": "Kaggle Learn & YouTube ML Crash Course",
        "project": "Build a recommendation system for movies/products",
        "time": "10-12 weeks",
        "difficulty": "Intermediate to Advanced",
        "certification": "Google ML Engineer Certificate"
    },
    "Git": {
        "course": "Git Complete: The definitive guide (Udemy)",
        "free": "Git Documentation & GitHub Learning Lab",
        "project": "Contribute to open-source projects and manage team workflows",
        "time": "2-3 weeks",
        "difficulty": "Beginner",
        "certification": "GitHub Certified Developer"
    },
    "Docker": {
        "course": "Docker Mastery (Udemy) - Bret Fisher",
        "free": "Docker Official Documentation & Play with Docker",
        "project": "Containerize a full-stack application with microservices",
        "time": "4-5 weeks",
        "difficulty": "Intermediate",
        "certification": "Docker Certified Associate"
    },
    "AWS": {
        "course": "AWS Certified Solutions Architect (A Cloud Guru)",
        "free": "AWS Free Tier & AWS Training and Certification",
        "project": "Deploy a scalable web application on AWS cloud",
        "time": "8-10 weeks",
        "difficulty": "Intermediate to Advanced", 
        "certification": "AWS Solutions Architect Associate"
    }
}

# ----------------------- Utility Functions ----------------------------
def create_skill_hash(skills_list):
    """Create a consistent hash for skills to prevent percentage changes on refresh"""
    if not skills_list:
        return ""
    skills_string = ",".join(sorted(skills_list))
    return hashlib.md5(skills_string.encode()).hexdigest()

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF with enhanced error handling"""
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
    """Enhanced skill extraction with better pattern matching"""
    found_skills = []
    text_lower = text.lower()
    
    # Check all skill categories
    for category, skills in COMPREHENSIVE_SKILL_DATABASE.items():
        for skill in skills:
            # More flexible matching patterns
            skill_variations = [
                skill.lower(),
                skill.lower().replace('.', ''),
                skill.lower().replace(' ', ''),
                skill.lower().replace('-', ''),
                skill.lower().replace('/', ''),
            ]
            
            for variation in skill_variations:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text_lower) or variation in text_lower:
                    if skill not in found_skills:
                        found_skills.append(skill)
                    break
    
    return found_skills

def extract_contact_info(text: str) -> Dict[str, str]:
    """Enhanced contact information extraction"""
    info = {
        'email': 'Not specified',
        'phone': 'Not specified', 
        'name': 'Not specified'
    }
    
    # Extract email with better pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        info['email'] = emails[0]
    
    # Extract phone with multiple patterns
    phone_patterns = [
        r'\+91[\s-]?\d{10}',
        r'\d{10}',
        r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}',
        r'\d{3}[\s-]?\d{3}[\s-]?\d{4}',
        r'\+\d{1,3}[\s-]?\d{10,14}'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            info['phone'] = phones[0]
            break
    
    # Extract name with improved logic
    lines = text.split('\n')
    for line in lines[:15]:  # Check first 15 lines
        line = line.strip()
        if line and len(line.split()) <= 4 and len(line) > 3 and len(line) < 50:
            # Skip lines with common resume keywords
            skip_words = ['resume', 'cv', 'curriculum', 'vitae', 'profile', 'summary', 
                         'objective', 'experience', 'education', 'skills', 'contact',
                         'email', 'phone', 'address', 'linkedin', 'github']
            
            if not any(word in line.lower() for word in skip_words):
                if '@' not in line and not re.search(r'\d{10}', line):
                    # Check if it looks like a name (contains letters and possibly spaces)
                    if re.match(r'^[A-Za-z\s.]+$', line):
                        info['name'] = line
                        break
    
    return info

def analyze_resume_offline(text: str) -> Dict:
    """Comprehensive offline resume analysis"""
    contact_info = extract_contact_info(text)
    skills = extract_skills_from_text(text)
    
    # Extract education with better patterns
    education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd', 'diploma', 'certification', 'institute']
    education_info = "Not specified"
    
    text_lower = text.lower()
    for keyword in education_keywords:
        if keyword in text_lower:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if keyword in line.lower():
                    edu_lines = lines[i:i+4]
                    education_info = ' '.join(edu_lines).strip()[:300]
                    break
            break
    
    # Extract experience with better patterns
    experience_keywords = ['experience', 'work', 'employment', 'job', 'position', 'role', 'worked', 'developer', 'engineer', 'analyst']
    experience_info = "Not specified"
    
    for keyword in experience_keywords:
        if keyword in text_lower:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if keyword in line.lower():
                    exp_lines = lines[i:i+6]
                    experience_info = ' '.join(exp_lines).strip()[:400]
                    break
            break
    
    # Extract certifications
    cert_keywords = ['certification', 'certificate', 'certified', 'course', 'training', 'credential', 'license']
    certifications = "Not specified"
    
    for keyword in cert_keywords:
        if keyword in text_lower:
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if keyword in line.lower():
                    cert_lines = lines[i:i+4]
                    certifications = ' '.join(cert_lines).strip()[:300]
                    break
            break
    
    return {
        'Name': contact_info['name'],
        'Email': contact_info['email'],
        'Phone': contact_info['phone'],
        'Skills': ', '.join(skills) if skills else 'Not specified',
        'Education': education_info,
        'Experience': experience_info,
        'Certifications': certifications,
        'SkillsList': skills  # Keep original list for analysis
    }

def analyze_skill_gaps(user_skills: List[str], required_skills: List[str]) -> Dict:
    """Enhanced skill gap analysis with consistent results"""
    if not user_skills:
        return {"matched": [], "missing": required_skills, "match_percentage": 0}
    
    # Create consistent hash for reproducible results
    skill_hash = create_skill_hash(user_skills + required_skills)
    
    user_skills_lower = [skill.lower().strip() for skill in user_skills if skill.strip()]
    required_skills_clean = [skill.strip() for skill in required_skills if skill.strip()]
    
    matched = []
    missing = []
    
    for req_skill in required_skills_clean:
        req_skill_lower = req_skill.lower()
        is_matched = False
        
        for user_skill in user_skills_lower:
            # Enhanced fuzzy matching
            if (req_skill_lower in user_skill or 
                user_skill in req_skill_lower or
                any(word in user_skill for word in req_skill_lower.split() if len(word) > 2) or
                any(word in req_skill_lower for word in user_skill.split() if len(word) > 2)):
                matched.append(req_skill)
                is_matched = True
                break
        
        if not is_matched:
            missing.append(req_skill)
    
    match_percentage = (len(matched) / len(required_skills_clean)) * 100 if required_skills_clean else 0
    
    return {
        "matched": matched,
        "missing": missing,
        "match_percentage": round(match_percentage, 1),
        "hash": skill_hash  # For consistency
    }

def generate_learning_recommendations(missing_skills: List[str], user_skills: List[str] = None) -> str:
    """Generate comprehensive learning recommendations"""
    if not missing_skills:
        return "🎉 Excellent! You have all the required skills for this role. Consider exploring advanced topics to stay ahead!"
    
    recommendations = ""
    
    # Prioritize skills based on user's existing skills
    prioritized_skills = missing_skills[:6]  # Focus on top 6 skills
    
    for i, skill in enumerate(prioritized_skills, 1):
        recommendations += f"## {i}. {skill}\n\n"
        
        if skill in COMPREHENSIVE_LEARNING_RESOURCES:
            resource = COMPREHENSIVE_LEARNING_RESOURCES[skill]
            recommendations += f"**📚 Recommended Course:** {resource['course']}\n\n"
            recommendations += f"**🆓 Free Resources:** {resource['free']}\n\n"
            recommendations += f"**🛠️ Practice Project:** {resource['project']}\n\n"
            recommendations += f"**⏱️ Estimated Time:** {resource['time']}\n\n"
            recommendations += f"**📊 Difficulty Level:** {resource['difficulty']}\n\n"
            recommendations += f"**🏆 Certification:** {resource['certification']}\n\n"
        else:
            recommendations += f"**📚 Recommended Course:** Search for '{skill}' courses on Coursera, Udemy, or edX\n\n"
            recommendations += f"**🆓 Free Resources:** YouTube tutorials and official documentation for {skill}\n\n"
            recommendations += f"**🛠️ Practice Project:** Build a portfolio project showcasing {skill}\n\n"
            recommendations += f"**⏱️ Estimated Time:** 3-5 weeks\n\n"
        
        recommendations += "---\n\n"
    
    return recommendations

def create_professional_report(analysis: Dict, role: str, gap_analysis: Dict, recommendations: str, jobs: List[Dict]) -> BytesIO:
    """Generate a professional PDF report"""
    try:
        pdf = FPDF(format='A4')
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 22)
        pdf.cell(0, 15, "Professional Skill Gap Analysis Report", ln=True, align='C')
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%B %d, %Y')}", ln=True, align='C')
        pdf.ln(15)
        
        # Executive Summary
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("Arial", "", 11)
        
        name = analysis.get("Name", "Professional")
        pdf.cell(0, 8, f"Candidate: {name}", ln=True)
        pdf.cell(0, 8, f"Target Role: {role}", ln=True)
        pdf.cell(0, 8, f"Skills Match: {gap_analysis['match_percentage']}%", ln=True)
        pdf.cell(0, 8, f"Skills Assessment Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(10)
        
        # Contact Information
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Contact Information", ln=True)
        pdf.set_font("Arial", "", 11)
        
        email = analysis.get("Email", "Not specified")
        phone = analysis.get("Phone", "Not specified")
        
        pdf.cell(0, 8, f"Email: {email}", ln=True)
        pdf.cell(0, 8, f"Phone: {phone}", ln=True)
        pdf.ln(10)
        
        # Skills Analysis
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Skills Analysis", ln=True)
        pdf.set_font("Arial", "", 11)
        
        pdf.cell(0, 8, f"Total Skills Evaluated: {len(gap_analysis['matched']) + len(gap_analysis['missing'])}", ln=True)
        pdf.cell(0, 8, f"Skills You Possess: {len(gap_analysis['matched'])}", ln=True)
        pdf.cell(0, 8, f"Skills to Develop: {len(gap_analysis['missing'])}", ln=True)
        pdf.cell(0, 8, f"Overall Match Rate: {gap_analysis['match_percentage']}%", ln=True)
        pdf.ln(10)
        
        # Existing Skills
        if gap_analysis['matched']:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Your Current Skills:", ln=True)
            pdf.set_font("Arial", "", 10)
            for skill in gap_analysis['matched'][:20]:
                pdf.cell(0, 6, f"✓ {skill}", ln=True)
            pdf.ln(5)
        
        # Skills to Develop
        if gap_analysis['missing']:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Skills to Develop:", ln=True)
            pdf.set_font("Arial", "", 10)
            for skill in gap_analysis['missing'][:20]:
                pdf.cell(0, 6, f"○ {skill}", ln=True)
            pdf.ln(5)
        
        # Career Recommendations
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Career Development Plan", ln=True)
        pdf.set_font("Arial", "", 10)
        
        # Add simplified recommendations
        if gap_analysis['missing']:
            pdf.multi_cell(0, 6, f"Focus on developing these key skills for {role}:")
            pdf.ln(5)
            for i, skill in enumerate(gap_analysis['missing'][:8], 1):
                pdf.multi_cell(0, 5, f"{i}. {skill} - Estimated learning time: 3-6 weeks")
        
        # Job Market Insights
        if jobs:
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Current Job Market Opportunities", ln=True)
            pdf.set_font("Arial", "", 10)
            
            for i, job in enumerate(jobs[:5], 1):
                pdf.set_font("Arial", "B", 11)
                title = job.get('title', 'Job Title')[:40]
                company = job.get('company', 'Company')[:25]
                pdf.cell(0, 8, f"{i}. {title} at {company}", ln=True)
                
                pdf.set_font("Arial", "", 9)
                pdf.cell(0, 6, f"Location: {job.get('location', 'N/A')}", ln=True)
                pdf.cell(0, 6, f"Salary: {job.get('salary', 'Not specified')}", ln=True)
                pdf.cell(0, 6, f"Experience: {job.get('experience', 'N/A')}", ln=True)
                pdf.ln(3)
        
        # Generate PDF
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        return BytesIO()

# ----------------------- Main Application ----------------------------

# Progress Tracking
if 'progress_step' not in st.session_state:
    st.session_state.progress_step = 1

# File Upload Section
st.markdown('<div class="pro-card">', unsafe_allow_html=True)
st.markdown("### 📤 Upload Your Resume")
st.markdown("*Upload your PDF resume for comprehensive professional analysis*")

uploaded_file = st.file_uploader(
    "Choose your PDF resume file", 
    type=["pdf"],
    help="Upload a PDF version of your resume for detailed skill analysis"
)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # Update progress
    st.session_state.progress_step = 2
    
    # Process the uploaded file
    with st.spinner("📄 Processing your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    
    if resume_text:
        st.markdown('<div class="success-box">✅ Resume processed successfully! Advanced analysis complete.</div>', unsafe_allow_html=True)
        
        # Show text preview
        with st.expander("📄 Resume Content Preview"):
            st.text_area("Extracted Text", resume_text[:2000] + "..." if len(resume_text) > 2000 else resume_text, height=200)
        
        # Offline Analysis
        with st.spinner("🔍 Analyzing your professional profile..."):
            analysis = analyze_resume_offline(resume_text)
        
        # Display Analysis Results
        st.markdown('<div class="pro-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Professional Profile Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**👤 Personal Information**")
            st.write(f"**Name:** {analysis.get('Name', 'Not specified')}")
            st.write(f"**Email:** {analysis.get('Email', 'Not specified')}")
            st.write(f"**Phone:** {analysis.get('Phone', 'Not specified')}")
        
        with col2:
            st.markdown("**🎓 Professional Background**")
            education = analysis.get('Education', 'Not specified')
            st.write(f"**Education:** {education[:80]}..." if len(education) > 80 else f"**Education:** {education}")
            certifications = analysis.get('Certifications', 'Not specified')
            st.write(f"**Certifications:** {certifications[:80]}..." if len(certifications) > 80 else f"**Certifications:** {certifications}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Skills Display
        skills_text = analysis.get('Skills', '')
        user_skills = analysis.get('SkillsList', [])
        
        if user_skills:
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("### 🛠️ Detected Technical Skills")
            skills_html = ""
            for skill in user_skills:
                skills_html += f'<span class="skill-badge">{skill}</span>'
            st.markdown(skills_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-box">⚠️ Limited skills detected. Please ensure your technical skills are clearly listed in your resume.</div>', unsafe_allow_html=True)
        
        # Job Role Selection
        st.markdown('<div class="pro-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Target Role Selection")
        st.markdown("*Select your desired career path for personalized analysis*")
        
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
            # Update progress
            st.session_state.progress_step = 3
            
            # Get job requirements
            job_req = ENHANCED_JOB_REQUIREMENTS.get(selected_role, {"technical": [], "soft": []})
            required_skills = job_req["technical"] + job_req["soft"]
            
            # Skill Gap Analysis
            gap_analysis = analyze_skill_gaps(user_skills, required_skills)
            
            # Skills Gap Visualization
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("### 🔍 Professional Skill Gap Analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">{}%</div>'.format(gap_analysis['match_percentage']), unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Skills Match</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-delta">{} skills aligned</div>'.format(len(gap_analysis['matched'])), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">{}</div>'.format(len(gap_analysis['matched'])), unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Current Skills</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-delta">Ready to leverage</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-value">{}</div>'.format(len(gap_analysis['missing'])), unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Growth Areas</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-delta">Development opportunities</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Skills Breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="pro-card">', unsafe_allow_html=True)
                if gap_analysis['matched']:
                    st.markdown("### ✅ Your Matching Skills")
                    matched_html = ""
                    for skill in gap_analysis['matched']:
                        matched_html += f'<span class="skill-badge">{skill}</span>'
                    st.markdown(matched_html, unsafe_allow_html=True)
                else:
                    st.info("No matching skills found. This represents a significant growth opportunity!")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="pro-card">', unsafe_allow_html=True)
                if gap_analysis['missing']:
                    st.markdown("### 📚 Skills to Develop")
                    missing_html = ""
                    for skill in gap_analysis['missing']:
                        missing_html += f'<span class="missing-skill-badge">{skill}</span>'
                    st.markdown(missing_html, unsafe_allow_html=True)
                else:
                    st.success("🎉 Outstanding! You possess all required skills for this role.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Interactive Skill Gap Chart
            if gap_analysis['matched'] or gap_analysis['missing']:
                fig = go.Figure()
                
                # Add bars with custom colors
                fig.add_trace(go.Bar(
                    name='Skills You Have',
                    x=['Current Skills', 'Skills to Learn'],
                    y=[len(gap_analysis['matched']), 0],
                    marker_color='#10b981',
                    text=[len(gap_analysis['matched']), ''],
                    textposition='auto',
                ))
                
                fig.add_trace(go.Bar(
                    name='Skills to Learn',
                    x=['Current Skills', 'Skills to Learn'],
                    y=[0, len(gap_analysis['missing'])],
                    marker_color='#ef4444',
                    text=['', len(gap_analysis['missing'])],
                    textposition='auto',
                ))
                
                fig.update_layout(
                    title={
                        'text': f'Skill Analysis for {selected_role}',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 20, 'color': '#1e293b'}
                    },
                    barmode='group',
                    height=400,
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': '#1e293b'},
                    legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'right', 'x': 1}
                )
                
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Learning Recommendations
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("### 📚 Personalized Learning Roadmap")
            
            if gap_analysis['missing']:
                recommendations = generate_learning_recommendations(gap_analysis['missing'], user_skills)
                
                # Create learning cards for each skill
                for i, skill in enumerate(gap_analysis['missing'][:6]):
                    st.markdown(f'<div class="learning-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="learning-skill-title">🎯 {skill}</div>', unsafe_allow_html=True)
                    
                    if skill in COMPREHENSIVE_LEARNING_RESOURCES:
                        resource = COMPREHENSIVE_LEARNING_RESOURCES[skill]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f'<div class="learning-resource"><strong>📚 Course:</strong> {resource["course"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="learning-resource"><strong>🆓 Free Resource:</strong> {resource["free"]}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f'<div class="learning-resource"><strong>⏱️ Time:</strong> {resource["time"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="learning-resource"><strong>📊 Level:</strong> {resource["difficulty"]}</div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="learning-resource"><strong>🛠️ Project:</strong> {resource["project"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="learning-resource"><strong>🏆 Certification:</strong> {resource["certification"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="learning-resource"><strong>📚 Recommended:</strong> Search for "{skill}" courses on Coursera, Udemy, or edX</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="learning-resource"><strong>🆓 Free Resources:</strong> YouTube tutorials and official documentation</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="learning-resource"><strong>⏱️ Estimated Time:</strong> 3-5 weeks</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="success-box">🎉 Exceptional! You have all required skills. Consider exploring advanced topics or leadership development to further enhance your profile.</div>', unsafe_allow_html=True)
                recommendations = "All required skills are present. Focus on advanced topics and leadership development."
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Job Opportunities
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("### 💼 Current Market Opportunities")
            
            jobs = SAMPLE_JOBS_DATABASE.get(selected_role, [])
            if jobs:
                st.info(f"Found {len(jobs)} relevant opportunities for {selected_role}")
                
                for job in jobs:
                    st.markdown('<div class="job-card">', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-title">{job["title"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-company">🏢 {job["company"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="job-details">', unsafe_allow_html=True)
                    st.markdown(f'<span class="job-detail-item">📍 {job["location"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="job-detail-item">💰 {job["salary"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="job-detail-item">⏱️ {job["experience"]}</span>', unsafe_allow_html=True)
                    st.markdown(f'<span class="job-detail-item">📅 {job["posted"]}</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown(f'**Description:** {job["description"]}')
                    
                    # Show required skills
                    if job.get("skills_required"):
                        st.markdown("**Required Skills:**")
                        skills_html = ""
                        for skill in job["skills_required"]:
                            if skill in user_skills:
                                skills_html += f'<span class="skill-badge">{skill}</span>'
                            else:
                                skills_html += f'<span class="missing-skill-badge">{skill}</span>'
                        st.markdown(skills_html, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">💡 Keep monitoring job portals and company websites for new opportunities in your field!</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Report Generation
            st.markdown('<div class="pro-card">', unsafe_allow_html=True)
            st.markdown("### 📥 Professional Career Report")
            st.markdown("*Generate a comprehensive PDF report with your complete analysis*")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate Professional Report", use_container_width=True):
                    with st.spinner("📊 Creating your comprehensive career report..."):
                        try:
                            report_buffer = create_professional_report(
                                analysis, selected_role, gap_analysis, recommendations, jobs
                            )
                            
                            if report_buffer.getvalue():
                                st.success("✅ Professional report generated successfully!")
                                
                                st.download_button(
                                    label="⬇️ Download PDF Report",
                                    data=report_buffer,
                                    file_name=f"Professional_Career_Analysis_{selected_role.replace(' ', '_')}.pdf",
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
                **📊 Analysis Summary**
                - **Skills Evaluated:** {len(required_skills)}
                - **Match Rate:** {gap_analysis['match_percentage']}%
                - **Opportunities Found:** {len(jobs)}
                - **Learning Resources:** Comprehensive
                - **Report Type:** Professional Grade
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 20px; margin-top: 3rem; color: white;'>
    <h3>🚀 Professional Career Development Platform</h3>
    <p style='margin: 1rem 0; opacity: 0.9;'>Advanced skill analysis • Personalized learning paths • Career acceleration</p>
    <p style='font-size: 0.9rem; opacity: 0.7;'>Your professional data is processed securely and never stored permanently. Built with cutting-edge technology for modern professionals.</p>
</div>
""", unsafe_allow_html=True)
