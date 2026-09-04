from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from docx import Document
import pdfplumber
import io
import re
from collections import Counter
from enum import Enum
import sqlite3
import datetime

# --- NEW PDF IMPORTS ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from pydantic import BaseModel, Field
from typing import List

# 1. Initialize FastAPI App
app = FastAPI()

# 2. Define Database Name
DB_NAME = "jobquest.db" 

# 3. Add CORS Middleware
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Define Job Roles Enum
class JobRole(str, Enum):
    JavaDeveloper = "Java Developer"
    FullStackDeveloper = "Full Stack Developer"
    BackendDeveloperJava = "Backend Developer (Java/Spring Boot)"
    FrontendDeveloper = "Frontend Developer"
    DevOpsEngineer = "DevOps Engineer"
    BusinessAnalyst = "Business Analyst (IT/Software)"
    TechnicalBusinessAnalyst = "Technical Business Analyst (Java)"
    SoftwareEngineer = "Software Engineer"
    DataAnalyst = "Data Analyst"
    DataScientist = "Data Scientist"
    CloudEngineer = "Cloud Engineer"
    QAEngineer = "QA Engineer"
    AndroidDeveloper = "Android Developer"
    iOSDeveloper = "iOS Developer"
    CybersecurityAnalyst = "Cybersecurity Analyst"
    ProjectManagerIT = "Project Manager (IT)"
    Embedded_Design_IoT_Engineer = "Embedded Design/IoT Engineer"
    VLSI_Design_Engineer = "VLSI Design Engineer"
    Robotics_Automation_Engineer = "Robotics/Automation Engineer"
    Automotive_Powertrain_Engineer = "Automotive/Powertrain Engineer"

# --- NEW: Pydantic model for PDF Report data ---
class ReportData(BaseModel):
    role: str
    ats_score: int
    missing_keywords: List[str] = Field(default_factory=list)
    improvement_advice: List[str] = Field(default_factory=list)


# 5. Define Keywords, Advice, and Courses for each role
ROLES = {
    "Java Developer": {
        "keywords": [
            "java", "spring", "spring boot", "hibernate", "microservices", "maven", "rest", "sql",
            "spring security", "junit", "git", "docker", "kafka", "jenkins", "lambda",
            "api", "cloud", "aws", "gcp", "azure", "jpa", "restful", "soap", "jvm", "jdbc"
        ],
        "project_keywords": ["api", "microservice", "e-commerce", "payment", "inventory", "backend"],
        "soft_skills": ["problem solving", "agile", "communication", "teamwork"], 
        "advice": [
            "Highlight projects using Spring Boot and microservices.",
            "Mention any experience with cloud platforms (AWS, Azure, GCP).",
            "List specific Java versions (Java 8, Java 11, etc.) and features (like Lambda, Streams) you've used."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/spring-hibernate-tutorial/",
            "coursera": "https://www.coursera.org/specializations/java-spring-framework"
        }
    },
    "Full Stack Developer": {
        "keywords": [
            "java", "react", "angular", "vue", "spring boot", "html", "css", "node.js",
            "docker", "mysql", "typescript", "redux", "mongodb", "graphql", "aws", "javascript",
            "webpack", "jest", "api", "rest", "python", "django", "flask", "postgresql"
        ],
        "project_keywords": ["full-stack", "fullstack", "e-commerce", "dashboard", "portal", "web app"],
        "soft_skills": ["agile", "scrum", "problem solving", "communication"], 
        "advice": [
            "Show at least one project with a clear backend (API) and frontend (React/Angular/Vue).",
            "Mention your database experience (e.g., SQL, MongoDB).",
            "Include version control (Git) in your skills."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/the-web-developer-bootcamp/",
            "coursera": "https://www.coursera.org/professional-certificates/meta-full-stack-developer"
        }
    },
    "Backend Developer (Java/Spring Boot)": {
        "keywords": [
            "java", "spring boot", "spring", "microservices", "docker", "api", "mysql", "linux",
            "jpa", "rest", "redis", "kafka", "postgresql", "aws", "gcp", "hibernate", "maven", "nosql"
        ],
        "project_keywords": ["backend", "api", "microservice", "database", "system design", "payment"],
        "soft_skills": ["problem solving", "agile", "system design", "communication"], 
        "advice": [
            "Emphasize your understanding of API design and RESTful principles.",
            "Detail your experience with databases, distinguishing between SQL and NoSQL.",
            "Mention any messaging queues (Kafka, RabbitMQ) or caching (Redis) you've used."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/java-spring-boot-master-microservices-docker-kubernetes/",
            "coursera": "https://www.coursera.org/specializations/backend-java-spring-boot"
        }
    },
    "Frontend Developer": {
        "keywords": [
            "javascript", "react", "angular", "vue", "css", "html", "html5", "css3", "redux", "typescript",
            "ui/ux", "webpack", "babel", "sass", "less", "figma", "jest", "next.js", "tailwind"
        ],
        "project_keywords": ["frontend", "ui", "ux", "dashboard", "responsive", "website", "landing page"],
        "soft_skills": ["ui/ux", "agile", "teamwork", "creative"], 
        "advice": [
            "Provide links to your portfolio or live websites you've built.",
            "Highlight your experience with state management (Redux, Context API).",
            "Mention your understanding of responsive design and CSS pre-processors."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
            "coursera": "https://www.coursera.org/professional-certificates/meta-front-end-developer"
        }
    },
    "DevOps Engineer": {
        "keywords": [
            "docker", "kubernetes", "jenkins", "aws", "terraform", "ci/cd", "linux", "azure", "gcp",
            "bash", "ansible", "prometheus", "grafana", "python", "groovy", "git", "helm"
        ],
        "project_keywords": ["ci/cd", "pipeline", "automation", "infrastructure", "deployment", "scaling"],
        "soft_skills": ["automation", "problem solving", "communication", "collaboration"], 
        "advice": [
            "Quantify your achievements: 'Automated deployment, reducing time by 50%'.",
            "Show deep knowledge of a specific cloud provider (AWS, Azure, or GCP).",
            "List your IaC (Infrastructure as Code) tools, like Terraform or Ansible."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/",
            "coursera": "https://www.coursera.org/professional-certificates/google-devops"
        }
    },
    "Business Analyst (IT/Software)": {
        "keywords": [
            "sql", "powerbi", "excel", "data visualization", "uml", "requirements gathering",
            "tableau", "jira", "agile", "scrum", "user stories", "srs", "brd", "use case"
        ],
        "project_keywords": ["analysis", "requirements", "documentation", "dashboard", "reporting", "process flow"],
        "soft_skills": ["communication", "stakeholder management", "problem solving", "analytical"], 
        "advice": [
            "Emphasize your role as the bridge between technical teams and business stakeholders.",
            "Mention specific methodologies (Agile, Scrum) you've worked with.",
            "Showcase your data skills (SQL, Tableau, PowerBI)."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/business-analysis-fundamentals/",
            "coursera": "https://www.coursera.org/professional-certificates/google-data-analytics"
        }
    },
    "Technical Business Analyst (Java)": {
        "keywords": [
            "java", "sql", "uml", "requirements gathering", "jira", "excel", "api", "spring",
            "agile", "visio", "user stories", "srs", "brd", "database", "rest"
        ],
        "project_keywords": ["technical", "analysis", "requirements", "api", "database", "documentation", "java"],
        "soft_skills": ["communication", "technical writing", "problem solving", "analytical"], 
        "advice": [
            "Highlight your ability to read and understand Java code, even if you don't write it daily.",
            "Explain how you've translated business needs into technical API or database requirements.",
            "Mention your proficiency in SQL for data analysis and validation."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/technical-business-analyst-training/",
            "coursera": "https://www.coursera.org/specializations/business-analysis"
        }
    },
    "Software Engineer": {
        "keywords": [
            "java", "c++", "python", "data structures", "algorithms", "oop", "object-oriented",
            "unit testing", "rest", "git", "linux", "sql", "docker", "agile", "c#", ".net"
        ],
        "project_keywords": ["software", "development", "algorithm", "backend", "application", "system"],
        "soft_skills": ["problem solving", "agile", "communication", "teamwork"], 
        "advice": [
            "This is a general role. Your resume should highlight strong fundamentals in OOP, Data Structures, and Algorithms.",
            "List the programming languages you are most proficient in first.",
            "Include links to your GitHub or LeetCode/HackerRank profiles."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/data-structures-and-algorithms-deep-dive-using-java/",
            "coursera": "https://www.coursera.org/specializations/data-structures-algorithms"
        }
    },
    "Data Analyst": {
        "keywords": [
            "python", "sql", "excel", "tableau", "powerbi", "data visualization", "r",
            "statistics", "pandas", "numpy", "sas", "ssis", "google analytics", "looker"
        ],
        "project_keywords": ["dashboard", "analysis", "reporting", "visualization", "insights", "sql"],
        "soft_skills": ["analytical", "problem solving", "communication", "detail-oriented"], 
        "advice": [
            "Provide links to a public portfolio of your dashboards (Tableau Public, etc.).",
            "Quantify your impact: 'Created a dashboard that identified 10% cost savings'.",
            "Emphasize your SQL and Python (Pandas) skills for data cleaning and manipulation."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/the-data-analyst-bootcamp/",
            "coursera": "https://www.coursera.org/professional-certificates/google-data-analytics"
        }
    },
    "Data Scientist": {
        "keywords": [
            "python", "machine learning", "deep learning", "scikit-learn", "sql", "r",
            "pandas", "numpy", "tensorflow", "keras", "pytorch", "nlp", "statistics", "tableau"
        ],
        "project_keywords": ["model", "machine learning", "nlp", "deep learning", "prediction", "classification"],
        "soft_skills": ["analytical", "research", "problem solving", "communication"], 
        "advice": [
            "Clearly list your Machine Learning projects, including the models used (e.g., Random Forest, LSTM) and the outcome.",
            "Mention any experience with large datasets or big data tools (Spark).",
            "Include links to your Kaggle profile or GitHub projects."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/machinelearning/",
            "coursera": "https://www.coursera.org/professional-certificates/ibm-data-science"
        }
    },
    "Cloud Engineer": {
        "keywords": [
            "aws", "azure", "gcp", "terraform", "docker", "devops", "cloudformation",
            "kubernetes", "ci/cd", "serverless", "lambda", "iam", "s3", "ec2", "ansible"
        ],
        "project_keywords": ["cloud", "aws", "azure", "gcp", "migration", "infrastructure", "serverless"],
        "soft_skills": ["automation", "problem solving", "collaboration", "security-conscious"], 
        "advice": [
            "List your cloud certifications (e.g., AWS Certified Solutions Architect) prominently.",
            "Be specific about the services you've used (e.g., 'Used EC2, S3, and Lambda for a serverless application').",
            "Mention experience with Infrastructure as Code (Terraform, CloudFormation)."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/aws-certified-solutions-architect-associate-saa-c03/",
            "coursera": "https://www.coursera.org/professional-certificates/google-cloud-computing-foundations"
        }
    },
    "QA Engineer": {
        "keywords": [
            "selenium", "automation", "manual testing", "junit", "testng", "java", "python",
            "api testing", "postman", "regression testing", "jira", "test cases", "cypress", "playwright"
        ],
        "project_keywords": ["testing", "qa", "automation", "selenium", "test plan", "bug report"],
        "soft_skills": ["detail-oriented", "analytical", "communication", "problem solving"], 
        "advice": [
            "Clearly distinguish between your manual and automation testing skills.",
            "List the automation frameworks you've used (Selenium, Cypress, Playwright).",
            "Mention your experience with API testing tools like Postman."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/selenium-webdriver-with-java-basics-to-advanced/",
            "coursera": "https://www.coursera.org/specializations/software-testing-automation"
        }
    },
    "Android Developer": {
        "keywords": [
            "android", "kotlin", "java", "firebase", "android studio", "xml", "sdk",
            "gradle", "jetpack", "mvvm", "dagger", "hilt", "rxjava", "coroutines"
        ],
        "project_keywords": ["android", "app", "mobile", "kotlin", "java", "play store"],
        "soft_skills": ["problem solving", "ui/ux", "teamwork", "detail-oriented"], 
        "advice": [
            "Specify your proficiency in Kotlin vs. Java.",
            "Mention modern Android development practices (Jetpack Compose, MVVM, Coroutines).",
            "Provide links to your apps on the Google Play Store, if available."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/the-complete-android-10-developer-course-mastering-android/",
            "coursera": "https://www.coursera.org/professional-certificates/meta-android-developer"
        }
    },
    "iOS Developer": {
        "keywords": [
            "swift", "objective-c", "xcode", "core data", "storyboards", "uikit", "swiftui",
            "cocoapods", "mvvm", "combine", "rxswift", "firebase"
        ],
        "project_keywords": ["ios", "app", "mobile", "swift", "swiftui", "app store"],
        "soft_skills": ["problem solving", "ui/ux", "teamwork", "detail-oriented"], 
        "advice": [
            "Specify your proficiency in Swift vs. Objective-C.",
            "Highlight experience with modern frameworks like SwiftUI and Combine.",
            "Provide links to your apps on the Apple App Store, if available."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/ios-13-app-development-bootcamp/",
            "coursera": "https://www.coursera.org/professional-certificates/meta-ios-developer"
        }
    },
    "Cybersecurity Analyst": {
        "keywords": [
            "security", "firewall", "network", "penetration testing", "siem", "nmap",
            "incident response", "encryption", "vulnerability", "wireshark", "metasploit", "soc"
        ],
        "project_keywords": ["security", "analysis", "pentest", "vulnerability", "incident", "network"],
        "soft_skills": ["analytical", "problem solving", "detail-oriented", "ethical"], 
        "advice": [
            "List any security certifications (Security+, CEH, CISSP) you have or are working on.",
            "Mention specific tools you've used (Wireshark, Nmap, Metasploit).",
            "Describe your understanding of security frameworks like NIST or ISO 27001."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/the-complete-cyber-security-course-end-point-protection/",
            "coursera": "https://www.coursera.org/professional-certificates/google-cybersecurity"
        }
    },
    "Project Manager (IT)": {
        "keywords": [
            "project management", "agile", "scrum", "kanban", "jira", "pmp", "csm",
            "risk management", "leadership", "stakeholder", "budget", "ms project", "sdlc"
        ],
        "project_keywords": ["project", "management", "agile", "scrum", "delivery", "roadmap", "launch"],
        "soft_skills": ["leadership", "communication", "stakeholder management", "organization", "risk management"], 
        "advice": [
            "List your certifications (PMP, Certified ScrumMaster) prominently.",
            "Quantify your projects: 'Managed a team of 10 and a $500k budget'.",
            "Emphasize your experience with specific methodologies (Agile, Waterfall, Hybrid)."
        ],
        "courses": {
            "udemy": "https://www.udemy.com/course/pmp-certification-exam-prep-course-pmbok-6th-edition/",
            "coursera": "https://www.coursera.org/professional-certificates/google-project-management"
        }
    },
    "Embedded Design/IoT Engineer": {
        "keywords": ["C", "C++", "Embedded C", "Microcontrollers", "RTOS",
                     "Linux", "ARM", "STM32", "Raspberry Pi", "Arduino",
                     "IoT Protocols", "MQTT", "Zigbee", "BLE", "Sensors",
                     "Actuators", "Cloud Platforms", "AWS IoT", "Debugging",
                     "Hardware Interfacing", "Firmware", "Device Drivers"],
        "project_keywords": ["RTOS", "Cloud Platforms", "Microcontrollers", "MQTT", "Firmware"],
        "soft_skills": ["problem solving", "detail-oriented", "debugging", "hardware"], 
        "advice": ["Focus on projects that bridge the hardware and cloud layers (e.g., sending sensor data to AWS/Azure).",
                   "Gain experience with Real-Time Operating Systems (RTOS) like FreeRTOS or Zephyr."],
        "courses": {
            "udemy": "https://www.udemy.com/course/mastering-microcontroller-and-embedded-driver-development/",
            "coursera": "https://www.coursera.org/specializations/iot"
        }
    },
    "VLSI Design Engineer": {
        "keywords": ["Verilog", "SystemVerilog", "VHDL", "RTL Design", "Digital Design",
                     "CMOS", "Timing Analysis", "Synthesis", "Place and Route", "DFT",
                     "Static Timing Analysis (STA)", "EDA Tools", "TCL", "Spice",
                     "Functional Verification", "ASIC", "FPGA"],
        "project_keywords": ["Verilog", "SystemVerilog", "RTL Design", "STA", "ASIC/FPGA"],
        "soft_skills": ["analytical", "problem solving", "detail-oriented", "debugging"], 
        "advice": ["Deepen expertise in one specific VLSI domain (e.g., Physical Design, Verification, or DFT).",
                   "Become proficient with industry-standard EDA tools (e.g., Cadence, Synopsys, Mentor Graphics)."],
        "courses": {
            "udemy": "https://www.udemy.com/topic/vlsi/",
            "coursera": "https://www.coursera.org/specializations/chip-based-vlsi-design-for-industrial-applications"
        }
    },
    "Robotics/Automation Engineer": {
        "keywords": ["PLC", "ROS", "Python", "C++", "Control Systems", "Industrial Automation",
                     "Sensors", "Actuators", "Embedded Systems", "Microcontrollers",
                     "HMI", "SCADA", "Ladder Logic", "Machine Vision", "Simulation",
                     "Process Optimization"],
        "project_keywords": ["PLC", "ROS", "Python", "Control Systems", "Simulation"],
        "soft_skills": ["problem solving", "hands-on", "automation", "systems thinking"], 
        "advice": ["Prioritize the specific PLC brands and industrial robot types listed in the job description for exact match.",
                   "Ensure project descriptions quantify results (e.g., 'reduced cycle time by 15%')."],
        "courses": {
            "udemy": "https://www.udemy.com/topic/industrial-automation/",
            "coursera": "https://www.coursera.org/learn/robotics-control-systems"
        }
    },
    "Automotive/Powertrain Engineer": {
        "keywords": ["EV/Electrification", "BMS", "Matlab/Simulink", "FEA", "CAD/CAE",
                     "ICE", "Transmission", "Engine Calibration", "Emissions Control",
                     "Hybrid Systems", "Thermal Management", "CANalyzer",
                     "Power Electronics", "Vehicle Dynamics", "SAE"],
        "project_keywords": ["EV/Electrification", "BMS", "Matlab/Simulink", "Engine Calibration", "FEA"],
        "soft_skills": ["problem solving", "analytical", "hands-on", "simulation"], 
        "advice": ["Use exact names of simulation software (e.g., GT-Power, ANSYS, AVL) if mentioned in the JD.",
                   "Highlight experience with industry standards (e.g., SAE, ISO 26262)."],
        "courses": {
            "udemy": "https://www.udemy.com/course/electric-vehicle-technology/",
            "coursera": "https://www.coursera.org/specializations/electric-vehicle-technology"
        }
    }
}


# 6. Database Helper Functions

def init_db():
    """Initializes the database and creates the tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            ats_score INTEGER NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keyword_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            keyword TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_analysis_to_db(role: str, ats_score: int):
    """Saves the main analysis result to the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now()
        cursor.execute("INSERT INTO analysis_results (role, ats_score, timestamp) VALUES (?, ?, ?)", (role, ats_score, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database save error: {e}")

def save_keyword_details_to_db(role: str, found_keywords: list, missing_keywords: list):
    """Saves the found and missed keywords to the new table."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now()
        found_data = [(role, kw, 'found', timestamp) for kw in found_keywords]
        missing_data = [(role, kw, 'missed', timestamp) for kw in missing_keywords]
        cursor.executemany("INSERT INTO keyword_results (role, keyword, status, timestamp) VALUES (?, ?, ?, ?)", found_data + missing_data)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Keyword DB save error: {e}")


# 7. Run init_db() on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# 8. Helper Functions (File Reading & Scoring)

def extract_text_from_docx(file):
    """Extracts text from a .docx file."""
    try:
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs if para.text])
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def extract_text_from_pdf(file):
    """Extracts text from a .pdf file."""
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def score_resume(role: str, text: str):
    """Scores a resume for a specific role."""
    role_data = ROLES.get(role, {})
    keywords = role_data.get("keywords", [])
    project_keywords = role_data.get("project_keywords", [])
    soft_skills = role_data.get("soft_skills", []) 
    advice = list(role_data.get("advice", [])) 
    courses = role_data.get("courses", {})
    text_low = text.lower()
    
    freq = Counter()
    for kw in keywords:
        count = len(re.findall(r'\b' + re.escape(kw) + r'\b', text_low))
        if count > 0:
            freq[kw] = count
    
    base_points = sum(min(count * 2, 6) for count in freq.values())
    max_points = len(keywords) * 2.5 
    
    if max_points == 0:
        return 0, [], [], ["Role keywords not defined."], {}

    base_score = int((base_points / max_points) * 100)
    
    project_score = 0
    for kw in project_keywords:
        if kw in text_low:
            project_score += 1
    project_boost = min(project_score * 3, 15)

    soft_skill_score = 0
    for skill in soft_skills:
        if skill in text_low:
            soft_skill_score += 1
    soft_skill_boost = min(soft_skill_score, 5)

    ats_score = min(100, base_score + project_boost + soft_skill_boost)

    missing = [kw for kw in keywords if kw not in freq]
    found_keywords = list(freq.keys()) 
    
    if ats_score >= 85:
        advice.insert(0, f"Excellent match! Your resume shows strong alignment with the {role} role.")
    elif 60 <= ats_score < 85:
        advice.insert(0, f"Good match. Your resume aligns well. To improve, focus on these missing keywords: {', '.join(missing[:5])}...")
    elif 40 <= ats_score < 60:
        advice.insert(0, f"Fair match. Your resume has some relevant skills, but is missing many key requirements. Focus on: {', '.join(missing)}")
    else:
        advice.insert(0, f"Poor match. Your resume does not seem to align with the {role} role. You are missing key skills like: {', '.join(missing)}")

    if project_score == 0 and len(project_keywords) > 0:
        advice.append("Consider adding a project section to your resume to showcase hands-on experience.")
        
    if soft_skill_score == 0 and len(soft_skills) > 0: 
        advice.append("Your resume is missing soft skills like 'communication' or 'teamwork', which recruiters look for.")

    return ats_score, missing, found_keywords, advice, courses


# --- NEW: PDF Generation Helper Function ---
def create_pdf_report(data: ReportData):
    """Creates a PDF report from the analysis data."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter # Get page dimensions
    
    styles = getSampleStyleSheet()
    style_body = styles['BodyText']
    style_body.fontSize = 10
    style_body.leading = 14
    
    # --- Start writing the PDF ---
    y_position = height - inch # Start 1 inch from the top
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, y_position, "JobQuest ATS Analysis Report")
    y_position -= inch
    
    # Role
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_position, "Role Analyzed: ")
    c.setFont("Helvetica", 12)
    c.drawString(inch + 1.5*inch, y_position, data.role)
    y_position -= 0.5*inch
    
    # Score
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_position, "ATS Match Score: ")
    c.setFont("Helvetica-Bold", 12)
    # Set color based on score
    if data.ats_score >= 85:
        c.setFillColorRGB(0.1, 0.6, 0.1) # Dark Green
    elif data.ats_score >= 60:
        c.setFillColorRGB(0.9, 0.6, 0) # Orange
    else:
        c.setFillColorRGB(0.8, 0.1, 0.1) # Dark Red
    c.drawString(inch + 1.5*inch, y_position, f"{data.ats_score}%")
    c.setFillColorRGB(0, 0, 0) # Reset color
    y_position -= 0.5*inch

    # --- Improvement Advice ---
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_position, "Improvement Advice:")
    y_position -= 0.25*inch
    
    for advice in data.improvement_advice:
        # Use Paragraph for automatic text wrapping
        p = Paragraph(f"• {advice}", style_body)
        p.wrapOn(c, width - 2*inch, height) # Wrap within page margins
        p_height = p.height
        
        if y_position - p_height < inch: # Check if it fits on page
            c.showPage() # Create new page
            y_position = height - inch
            c.setFont("Helvetica-Bold", 12) # Re-set font for new page
            c.drawString(inch, y_position, "Improvement Advice (Continued):")
            y_position -= 0.25*inch

        p.drawOn(c, inch, y_position - p_height)
        y_position -= (p_height + 10) # Add 10 points of spacing

    # --- Missing Keywords ---
    y_position -= 0.25*inch
    if y_position < 2 * inch: # Check for new page before starting new section
        c.showPage()
        y_position = height - inch
        
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_position, "Missing Keywords:")
    y_position -= 0.25*inch
    
    c.setFont("Helvetica", 10)
    # Join keywords with a comma
    keywords_text = ", ".join(data.missing_keywords)
    
    p = Paragraph(keywords_text, style_body)
    p.wrapOn(c, width - 2*inch, height)
    p_height = p.height
    
    if y_position - p_height < inch:
        c.showPage()
        y_position = height - inch
        
    p.drawOn(c, inch, y_position - p_height)
    
    # --- Finish PDF ---
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer


# 9. API Endpoints

@app.get("/jobs/")
async def get_jobs():
    """Returns a list of all available job roles."""
    return JSONResponse(list(ROLES.keys()))


@app.post("/upload-resume/")
async def upload_resume(
    file: UploadFile = File(...),
    job_role: JobRole = Form(...)
):
    job_role_str = job_role.value
    contents = await file.read()
    
    filename_lower = file.filename.lower()
    
    if filename_lower.endswith(".docx"):
        text = extract_text_from_docx(io.BytesIO(contents))
    elif filename_lower.endswith(".pdf"):
        text = extract_text_from_pdf(io.BytesIO(contents))
    else:
        return JSONResponse({"error": "Unsupported file type. Please upload .pdf or .docx"}, status_code=400)
        
    if not text:
        return JSONResponse({"error": "Could not read text from file."}, status_code=400)

    ats_score, missing, found_keywords, advice, courses = score_resume(job_role_str, text)
    result = "Good Match" if ats_score >= 60 else "Needs Improvement"
    
    save_analysis_to_db(job_role_str, ats_score)
    save_keyword_details_to_db(job_role_str, found_keywords, missing)

    return JSONResponse({
        "filename": file.filename,
        "role": job_role_str,
        "ats_score_percent": ats_score,
        "result": result,
        "missing_keywords": missing,
        "improvement_advice": advice,
        "suggested_courses": courses
    })


@app.post("/auto-match-role/")
async def auto_match_role(file: UploadFile = File(...)):
    contents = await file.read()
    
    filename_lower = file.filename.lower()
    
    if filename_lower.endswith(".docx"):
        text = extract_text_from_docx(io.BytesIO(contents))
    elif filename_lower.endswith(".pdf"):
        text = extract_text_from_pdf(io.BytesIO(contents))
    else:
        return JSONResponse({"error": "Unsupported file type. Please upload .pdf or .docx"}, status_code=400)

    if not text:
        return JSONResponse({"error": "Could not read text from file."}, status_code=400)

    best_score = -1
    best_role = "No Match Found"
    best_missing = []
    best_found = [] 
    best_advice = []
    best_courses = {}

    for role in ROLES.keys():
        ats_score, missing, found_keywords, advice, courses = score_resume(role, text)
        if ats_score > best_score:
            best_score = ats_score
            best_role = role
            best_missing = missing
            best_found = found_keywords 
            best_advice = advice
            best_courses = courses

    result = "Good Match" if best_score >= 60 else "Needs Improvement"
    
    save_analysis_to_db(f"Auto-Match ({best_role})", best_score)
    save_keyword_details_to_db(best_role, best_found, best_missing) 

    return JSONResponse({
        "filename": file.filename,
        "best_matched_role": best_role,
        "ats_score_percent": best_score,
        "result": result,
        "missing_keywords": best_missing,
        "improvement_advice": best_advice,
        "suggested_courses": best_courses
    })
    
# --- 10. UPDATED DASHBOARD DATA ENDPOINT ---
@app.get("/dashboard-data/")
async def get_dashboard_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        cursor.execute("SELECT AVG(ats_score) FROM analysis_results")
        avg_score_row = cursor.fetchone()
        average_score = round(avg_score_row[0], 1) if avg_score_row[0] else 0

        cursor.execute("SELECT role, COUNT(*) as count FROM analysis_results GROUP BY role ORDER BY count DESC")
        role_rows = cursor.fetchall()
        role_counts = {row['role']: row['count'] for row in role_rows}
        
        cursor.execute("""
            SELECT role, AVG(ats_score) as avg_score 
            FROM analysis_results 
            WHERE role NOT LIKE 'Auto-Match%'
            GROUP BY role 
            ORDER BY avg_score DESC
        """)
        avg_score_rows = cursor.fetchall()
        average_score_by_role = {row['role']: round(row['avg_score'], 1) for row in avg_score_rows}
        
        cursor.execute("""
            SELECT ats_score, timestamp 
            FROM analysis_results 
            ORDER BY timestamp ASC 
            LIMIT 15
        """)
        trend_rows = cursor.fetchall()
        score_trend = [
            {"score": row['ats_score'], "time": row['timestamp']}
            for row in trend_rows
        ]

        conn.close()
        
        return JSONResponse({
            "average_score": average_score,
            "total_analyses": sum(role_counts.values()),
            "role_counts": role_counts,
            "average_score_by_role": average_score_by_role,
            "score_trend": score_trend 
        })

    except Exception as e:
        print(f"Database read error: {e}")
        return JSONResponse({"error": "Could not read dashboard data"}, status_code=500)

# --- 11. NEW KEYWORD DASHBOARD ENDPOINT ---
@app.get("/keyword-data/")
async def get_keyword_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT keyword, COUNT(*) as count 
            FROM keyword_results 
            WHERE status = 'missed' 
            GROUP BY keyword 
            ORDER BY count DESC 
            LIMIT 10
        """)
        missed_rows = cursor.fetchall()
        top_missed = {row['keyword']: row['count'] for row in missed_rows}
        
        cursor.execute("""
            SELECT keyword, COUNT(*) as count 
            FROM keyword_results 
            WHERE status = 'found' 
            GROUP BY keyword 
            ORDER BY count DESC 
            LIMIT 10
        """)
        found_rows = cursor.fetchall()
        top_found = {row['keyword']: row['count'] for row in found_rows}
        
        conn.close()
        
        return JSONResponse({
            "top_missed_keywords": top_missed,
            "top_found_keywords": top_found
        })
    except Exception as e:
        print(f"Keyword data read error: {e}")
        return JSONResponse({"error": "Could not read keyword data"}, status_code=500)


# --- 12. NEW PDF REPORT ENDPOINT ---
@app.post("/generate-report/")
async def generate_report(data: ReportData):
    """Generates a PDF report from the analysis data and sends it as a file."""
    
    pdf_buffer = create_pdf_report(data)
    
    headers = {
        'Content-Disposition': 'attachment; filename="JobQuest_Report.pdf"'
    }
    # Return the PDF as a streaming response
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)