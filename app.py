from flask import Flask, render_template, request, redirect, session
import pymysql
import os
from PyPDF2 import PdfReader
import re
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is missing. Configure it in your environment."
    )
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database Connection
def get_db_connection():
    required = ["DB_USER", "DB_PASSWORD"]

    missing = [
        key for key in required
        if not os.getenv(key)
    ]

    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
        )

    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "career_forge"),
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )

# Password Validation
def validate_password(password):

    if not password:
        return False, "Password is required."

    if len(password) < 9:
        return False, "Password must contain at least 9 characters."

    if len(password) > 128:
        return False, "Password must not exceed 128 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain at least one special character."

    return True, "Password meets the requirements."

# Skills that Career Forge can detect
SKILLS = [
    "Python",
    "Java",
    "C",
    "C++",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "Flask",
    "Django",
    "MySQL",
    "MongoDB",
    "SQL",
    "Git",
    "GitHub",
    "PHP",
    "Bootstrap",
    "Machine Learning",
    "Data Science",
    "Data Structures",
    "OOP",
    "AWS",
    "Docker"
]

# Job roles and their required skills
JOB_ROLES = {
    "Python Developer": [
        "Python",
        "Flask",
        "Django"
    ],

    "Java Developer": [
        "Java",
        "OOP",
        "SQL"
    ],

    "Web Developer": [
        "HTML",
        "CSS",
        "JavaScript"
    ],

    "Frontend Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React"
    ],

    "Backend Developer": [
        "Python",
        "Flask",
        "SQL",
        "MySQL"
    ],

    "Full Stack Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "Python",
        "Flask",
        "MySQL"
    ],

    "Data Scientist": [
        "Python",
        "SQL",
        "Machine Learning",
        "Data Science"
    ],

    "Software Developer": [
        "Python",
        "Java",
        "OOP",
        "SQL"
    ]
}

# Resume Improvement Analyzer
def analyze_resume_improvements(resume_text, detected_skills, selected_role=None):

    resume_text_lower = resume_text.lower()

    # Resume sections to check
    resume_sections = {
        "Education": [
            "education",
            "academic background",
            "educational qualification"
        ],
        "Projects": [
            "projects",
            "personal projects",
            "academic projects"
        ],
        "Experience": [
            "experience",
            "work experience",
            "professional experience",
            "internship"
        ],
        "Certifications": [
            "certifications",
            "certificates",
            "certification"
        ],
        "Contact Information": [
            "email",
            "phone",
            "contact"
        ]
    }

    strengths = []
    missing_sections = []
    suggestions = []

    # Identify strengths from detected skills
    if detected_skills:
        strengths.append(
            f"Your resume contains {len(detected_skills)} detectable technical skills."
        )

        strengths.append(
            "Detected skills: " + ", ".join(detected_skills) + "."
        )
    else:
        suggestions.append(
            "Add relevant technical skills that you have genuinely learned or used."
        )

    # Check for resume sections
    for section, keywords in resume_sections.items():

        section_found = any(
            keyword in resume_text_lower
            for keyword in keywords
        )

        if not section_found:
            missing_sections.append(section)

    # Generate suggestions for missing sections
    section_suggestions = {
        "Education": (
            "Add an Education section with your course, institution, "
            "and relevant academic details."
        ),
        "Projects": (
            "Add a Projects section describing projects you have completed, "
            "the technologies used, and your contribution."
        ),
        "Experience": (
            "If applicable, include internships, work experience, "
            "or relevant practical experience."
        ),
        "Certifications": (
            "If you have relevant certifications, list their names and "
            "issuing organisations."
        ),
        "Contact Information": (
            "Make sure your resume includes accurate contact information."
        )
    }

    for section in missing_sections:
        suggestions.append(section_suggestions[section])

    # Generate job-specific recommendations
    role_recommendations = []

    if selected_role and selected_role in JOB_ROLES:

        required_skills = JOB_ROLES[selected_role]

        detected_skill_set = {
            skill.casefold()
            for skill in detected_skills
        }

        missing_role_skills = [
            skill
            for skill in required_skills
            if skill.casefold() not in detected_skill_set
        ]

        if missing_role_skills:

            role_recommendations.append(
                f"For the {selected_role} role, consider learning "
                "and demonstrating these skills where relevant: "
                + ", ".join(missing_role_skills)
                + "."
            )

        else:

            role_recommendations.append(
                f"Your resume contains all the skills currently listed "
                f"in Career Forge's checklist for {selected_role}. "
                "Make sure your projects demonstrate these skills."
            )

    # General resume improvement suggestions
    if "project" in resume_text_lower:
        suggestions.append(
            "Describe your projects with clear details about your "
            "contribution, technologies, and results."
        )

    if not any(
        word in resume_text_lower
        for word in ["developed", "created", "built", "implemented"]
    ):
        suggestions.append(
            "Where accurate, use action verbs such as developed, "
            "created, built, and implemented to describe your work."
        )

    if not strengths:
        strengths.append(
            "Upload a resume containing readable text to receive "
            "more useful feedback."
        )

    if not suggestions:
        suggestions.append(
            "Continue improving your resume with relevant projects, "
            "measurable achievements, and role-specific skills."
        )

    return {
        "strengths": strengths,
        "missing_sections": missing_sections,
        "suggestions": suggestions,
        "role_recommendations": role_recommendations
    }

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        # Validate required fields
        if not name or not email or not password:
            return (
                "Name, email, and password are required.",
                400
            )

        # Validate required fields
        if not name or not email or not password or not confirm_password:
            return "All fields are required.", 400

        # Confirm passwords match on the server
        if password != confirm_password:
            return "Passwords do not match.", 400

        # Validate password strength
        is_valid, message = validate_password(password)

        if not is_valid:
            return message, 400

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (name, email, hashed_password)
            )

            conn.commit()

        except pymysql.IntegrityError:

            conn.rollback()
            return "Email Already Exists!", 409

        except Exception:

            conn.rollback()
            app.logger.exception("Registration failed.")
            return "Registration failed. Please try again.", 500

        finally:
            cursor.close()
            conn.close()

        return redirect("/login")

    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            return "Email and password are required.", 400

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            user = cursor.fetchone()

        except Exception:

            app.logger.exception("Login database query failed.")
            return "Unable to log in right now. Please try again.", 500

        finally:
            cursor.close()
            conn.close()

        if not user:
            return "Invalid Email or Password", 401

        stored_password = user["password"]

        # Verify the hashed password
        try:
            password_is_valid = check_password_hash(
                stored_password,
                password
            )
        except (ValueError, TypeError):
            password_is_valid = False

        if password_is_valid:

            # Clear any previous session data
            session.clear()

            session["user_name"] = user["name"]
            session["user_id"] = user["id"]

            return redirect("/dashboard")

        return "Invalid Email or Password", 401

    return render_template("login.html")

# Dashboard
@app.route("/dashboard")
def dashboard():

    # Check if user is logged in
    if "user_name" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",

        # User Information
        name=session["user_name"],

        # Resume Analysis
        ats_score=session.get("ats_score"),
        detected_skills=session.get("detected_skills", []),
        missing_skills=session.get("missing_skills", []),

        # Job Role Analysis
        job_analysis=session.get("job_analysis", []),

        # Resume Improvement Suggestions
        resume_improvements=session.get("resume_improvements", {}),

        # Selected Target Job Role
        selected_role=session.get("selected_role"),
        selected_role_match=session.get("selected_role_match"),
        selected_role_matched=session.get("selected_role_matched", []),
        selected_role_missing=session.get("selected_role_missing", [])

    )
# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Upload Resume
@app.route("/upload_resume", methods=["POST"])
def upload_resume():

    if "user_name" not in session:
        return redirect("/login")

    file = request.files.get("resume")
    selected_role = request.form.get("target_role", "").strip()

    # Validate selected role
    if selected_role not in JOB_ROLES:
        session["upload_error"] = "Please select a valid job role."
        return redirect("/dashboard")

    if file and file.filename:

        # Save the uploaded resume
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(file_path)

        # Read PDF
        try:
            reader = PdfReader(file_path)

            # Extract text
            resume_text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    resume_text += page_text + "\n"

        except Exception:
            session["upload_error"] = (
                "Unable to read this PDF. Please upload a valid PDF resume."
            )
            return redirect("/dashboard")

        # Detect skills
        detected_skills = []

        resume_text_lower = resume_text.casefold()

        for skill in SKILLS:
            if skill.casefold() in resume_text_lower:
                detected_skills.append(skill)

        # Normalize detected skills for comparison
        detected_skill_set = {
            skill.strip().casefold()
            for skill in detected_skills
        }

        # Find general missing skills
        missing_skills = [
            skill
            for skill in SKILLS
            if skill.casefold() not in detected_skill_set
        ]

        # Analyze all job roles
        job_analysis = []

        for role, required_skills in JOB_ROLES.items():

            matched_skills = [
                skill for skill in required_skills
                if skill.strip().casefold() in detected_skill_set
            ]

            missing_role_skills = [
                skill for skill in required_skills
                if skill.strip().casefold() not in detected_skill_set
            ]

            if required_skills:
                match_percentage = round(
                    len(matched_skills) / len(required_skills) * 100
                )
            else:
                match_percentage = 0

            if matched_skills:
                job_analysis.append({
                    "role": role,
                    "match": match_percentage,
                    "matched": matched_skills,
                    "missing": missing_role_skills
                })

        # Show best-matching roles first
        job_analysis.sort(
            key=lambda job: job["match"],
            reverse=True
        )

        # Analyze the selected role
        selected_role_skills = JOB_ROLES[selected_role]

        selected_role_matched = [
            skill for skill in selected_role_skills
            if skill.strip().casefold() in detected_skill_set
        ]

        selected_role_missing = [
            skill for skill in selected_role_skills
            if skill.strip().casefold() not in detected_skill_set
        ]

        if selected_role_skills:
            selected_role_match = round(
                len(selected_role_matched)
                / len(selected_role_skills) * 100
            )
        else:
            selected_role_match = 0

        # Calculate ATS score
        total_skills = len(SKILLS)
        detected_count = len(detected_skills)

        if total_skills > 0:
            ats_score = int(
                (detected_count / total_skills) * 100
            )
        else:
            ats_score = 0

        # Analyze resume improvements for selected role
        resume_improvements = analyze_resume_improvements(
            resume_text,
            detected_skills,
            selected_role
        )

        # Save analysis results in session
        session["ats_score"] = ats_score
        session["detected_skills"] = detected_skills
        session["missing_skills"] = missing_skills
        session["job_analysis"] = job_analysis
        session["resume_text"] = resume_text
        session["resume_uploaded"] = True

        # Save selected role analysis
        session["selected_role"] = selected_role
        session["selected_role_match"] = selected_role_match
        session["selected_role_matched"] = selected_role_matched
        session["selected_role_missing"] = selected_role_missing

        # Save resume improvement analysis
        session["resume_improvements"] = resume_improvements

        # Clear previous upload errors
        session.pop("upload_error", None)

        return redirect("/dashboard")

    session["upload_error"] = "Please select a resume file."
    return redirect("/dashboard")

    return "Please select a file."

# Interview Preparation Questions

INTERVIEW_QUESTIONS = {
    "Python Developer": {
        "Beginner": [
            "What is Python?",
            "What are variables in Python?",
            "What are Python data types?",
            "What is the difference between a list and a tuple?",
            "Why is indentation important in Python?"
        ],
        "Intermediate": [
            "What is the difference between == and is?",
            "Explain exception handling in Python.",
            "What are *args and **kwargs?",
            "What is the difference between a list and a dictionary?",
            "What are Python modules and packages?"
        ],
        "Advanced": [
            "What are generators in Python?",
            "Explain the Global Interpreter Lock (GIL).",
            "What is the difference between multithreading and multiprocessing?",
            "How does memory management work in Python?",
            "What are decorators in Python?"
        ]
    },

    "Frontend Developer": {
        "Beginner": [
            "What is HTML?",
            "What is CSS?",
            "What is JavaScript?",
            "What are HTML tags and attributes?",
            "What is the CSS box model?"
        ],
        "Intermediate": [
            "What is the difference between let, const, and var?",
            "What is the DOM in JavaScript?",
            "What is Flexbox in CSS?",
            "What are JavaScript promises?",
            "What is responsive web design?"
        ],
        "Advanced": [
            "Explain event delegation in JavaScript.",
            "What is the virtual DOM in React?",
            "What are React hooks?",
            "How do you optimize frontend performance?",
            "Explain lazy loading in web applications."
        ]
    },

    "Web Developer": {
        "Beginner": [
            "What is the difference between HTML and CSS?",
            "What is JavaScript used for?",
            "What is a hyperlink?",
            "What is a web browser?",
            "What is responsive web design?"
        ],
        "Intermediate": [
            "What is the difference between GET and POST?",
            "What is the DOM?",
            "What is the purpose of CSS Flexbox?",
            "What is an API?",
            "What is the difference between frontend and backend?"
        ],
        "Advanced": [
            "Explain REST API architecture.",
            "How does browser caching work?",
            "What is cross-origin resource sharing (CORS)?",
            "How do you improve website performance?",
            "How would you secure a web application?"
        ]
    },

    "Backend Developer": {
        "Beginner": [
            "What is backend development?",
            "What is a server?",
            "What is a database?",
            "What is an API?",
            "What is SQL?"
        ],
        "Intermediate": [
            "What is REST API?",
            "What is the difference between GET and POST?",
            "What is database normalization?",
            "What is authentication?",
            "What is the difference between SQL and NoSQL?"
        ],
        "Advanced": [
            "How do you design a scalable backend?",
            "Explain database indexing.",
            "What is caching and why is it useful?",
            "How do you handle concurrent requests?",
            "How do you secure backend APIs?"
        ]
    },

    "Java Developer": {
        "Beginner": [
            "What is Java?",
            "What is a class in Java?",
            "What is an object?",
            "What is inheritance?",
            "What is the JVM?"
        ],
        "Intermediate": [
            "What is method overloading?",
            "What is method overriding?",
            "What is exception handling?",
            "What is the difference between an interface and an abstract class?",
            "What is the Java Collections Framework?"
        ],
        "Advanced": [
            "Explain multithreading in Java.",
            "What is garbage collection?",
            "Explain the Java memory model.",
            "What are Java streams?",
            "How does HashMap work internally?"
        ]
    },

    "Full Stack Developer": {
        "Beginner": [
            "What is full stack development?",
            "What is HTML?",
            "What is CSS?",
            "What is JavaScript?",
            "What is a database?"
        ],
        "Intermediate": [
            "How does the frontend communicate with the backend?",
            "What is REST API?",
            "What is CRUD?",
            "What is session management?",
            "How does a web application connect to a database?"
        ],
        "Advanced": [
            "How would you design a full stack application?",
            "How do you secure user authentication?",
            "How would you improve application performance?",
            "How do you handle errors between frontend and backend?",
            "How would you deploy a full stack application?"
        ]
    },

    "Data Scientist": {
        "Beginner": [
            "What is data science?",
            "What is a dataset?",
            "What is the difference between mean and median?",
            "What is Python used for in data science?",
            "What is data visualization?"
        ],
        "Intermediate": [
            "What is data preprocessing?",
            "What is the difference between supervised and unsupervised learning?",
            "What is overfitting?",
            "What is a confusion matrix?",
            "What is feature engineering?"
        ],
        "Advanced": [
            "Explain the bias-variance trade-off.",
            "How do you handle imbalanced datasets?",
            "What is cross-validation?",
            "How do you evaluate a classification model?",
            "How would you select features for a machine learning model?"
        ]
    },

    "Software Developer": {
        "Beginner": [
            "What is software development?",
            "What is a programming language?",
            "What is object-oriented programming?",
            "What is an algorithm?",
            "What is a data structure?"
        ],
        "Intermediate": [
            "What are the four pillars of OOP?",
            "What is the difference between a stack and a queue?",
            "What is version control?",
            "What is the software development life cycle?",
            "What is unit testing?"
        ],
        "Advanced": [
            "Explain common software design patterns.",
            "What is time complexity?",
            "What is the difference between monolithic and microservices architecture?",
            "How do you debug a complex application?",
            "How do you design maintainable software?"
        ]
    }
}

# Interview Answers

INTERVIEW_ANSWERS = {
    "Python Developer": {
        "Beginner": [
            "Python is a high-level, interpreted programming language known for its simple syntax and readability. It is used in web development, automation, data science, and artificial intelligence.",
            "Variables are names used to store data values. For example, name = 'Rahul' stores the text Rahul in a variable named name.",
            "Python's common data types include int, float, str, bool, list, tuple, set, and dict.",
            "A list is mutable, meaning its elements can be changed. A tuple is immutable, meaning its elements cannot be changed after creation.",
            "Indentation defines code blocks in Python. It is essential for writing valid conditional statements, loops, functions, and classes."
        ],
        "Intermediate": [
            "'==' compares values, whereas 'is' checks whether two references point to the same object.",
            "Exception handling manages runtime errors using try, except, else, and finally blocks.",
            "*args allows a function to accept multiple positional arguments, while **kwargs allows it to accept multiple keyword arguments.",
            "A list stores an ordered collection of items and allows duplicates. A dictionary stores key-value pairs, with unique keys.",
            "A module is a Python file containing reusable code. A package organizes related modules into a directory structure."
        ],
        "Advanced": [
            "Generators produce values one at a time using yield. They can save memory when processing large sequences.",
            "The Global Interpreter Lock (GIL) in traditional CPython builds allows only one thread at a time to execute Python bytecode within an interpreter. This affects CPU-bound multithreading.",
            "Multithreading uses multiple threads within a process, while multiprocessing uses separate processes. Multiprocessing can use multiple CPU cores for CPU-bound work.",
            "Python manages memory through mechanisms such as reference counting and garbage collection. Exact implementation details can vary by Python implementation.",
            "Decorators wrap functions or classes to add behavior without directly modifying their original code."
        ]
    },

    "Frontend Developer": {
        "Beginner": [
            "HTML stands for HyperText Markup Language. It defines the structure and content of a web page.",
            "CSS stands for Cascading Style Sheets. It controls the appearance and layout of web pages.",
            "JavaScript is a programming language used to add interactivity and dynamic behavior to websites.",
            "HTML tags define elements, while attributes provide additional information or configuration for those elements.",
            "The CSS box model consists of content, padding, border, and margin."
        ],
        "Intermediate": [
            "var is function-scoped, while let and const are block-scoped. A const binding cannot be reassigned.",
            "The DOM, or Document Object Model, represents a web page as objects that JavaScript can access and modify.",
            "Flexbox is a CSS layout system that helps arrange elements in rows or columns and align them efficiently.",
            "A Promise represents the eventual success or failure of an asynchronous operation.",
            "Responsive web design makes websites adapt to different screen sizes using flexible layouts, media queries, and responsive units."
        ],
        "Advanced": [
            "Event delegation attaches a handler to a parent element to handle events from its descendants through event bubbling.",
            "React's virtual DOM is an in-memory representation of the UI that React uses to calculate and apply necessary updates to the actual DOM.",
            "React hooks, such as useState and useEffect, allow function components to manage state and interact with component lifecycle behavior.",
            "Frontend performance can be improved through code splitting, lazy loading, image optimization, caching, and reducing unnecessary rendering.",
            "Lazy loading delays loading resources until they are needed, reducing initial loading work."
        ]
    },

    "Web Developer": {
        "Beginner": [
            "HTML defines webpage structure, while CSS controls its visual appearance.",
            "JavaScript adds dynamic behavior and interactivity to web pages.",
            "A hyperlink connects one webpage or resource to another using an anchor element.",
            "A web browser is software that retrieves and displays web content, such as HTML, CSS, and JavaScript.",
            "Responsive web design allows websites to work well on different devices and screen sizes."
        ],
        "Intermediate": [
            "GET is generally used to retrieve data, while POST is commonly used to submit data or request resource creation. Their exact behavior depends on the API.",
            "The DOM represents an HTML document as a tree of objects that scripts can inspect and modify.",
            "Flexbox is a CSS layout model used to align and distribute space among elements.",
            "An API defines how different software systems communicate with each other.",
            "Frontend code handles the user interface, while backend code handles server-side logic, processing, and data operations."
        ],
        "Advanced": [
            "REST is an architectural style for networked applications that commonly uses resources and HTTP methods.",
            "Browser caching stores reusable resources locally so they may load faster on later visits.",
            "CORS is a browser security mechanism that controls whether a webpage can access resources from another origin.",
            "Website performance can be improved with optimized images, caching, minified assets, efficient queries, and reduced network requests.",
            "Web applications can be secured using HTTPS, input validation, secure authentication, authorization, and appropriate protection against common web vulnerabilities."
        ]
    },

    "Backend Developer": {
        "Beginner": [
            "Backend development involves server-side logic, application processing, and database operations.",
            "A server receives requests from clients and sends responses or provides services.",
            "A database organizes and stores information so applications can retrieve and update it.",
            "An API defines how applications or software components exchange information.",
            "SQL is a language used to query and manage relational databases."
        ],
        "Intermediate": [
            "A REST API commonly exposes resources through HTTP endpoints and methods such as GET, POST, PUT, PATCH, and DELETE.",
            "GET typically retrieves information, while POST typically submits data or requests an operation.",
            "Database normalization organizes relational data to reduce unnecessary duplication and improve data integrity.",
            "Authentication verifies who a user is. Authorization determines what that user is allowed to do.",
            "SQL databases use relational tables and schemas, while NoSQL databases use models such as documents, key-value pairs, or graphs."
        ],
        "Advanced": [
            "A scalable backend can use stateless services, caching, load balancing, efficient databases, monitoring, and horizontal scaling.",
            "Database indexes speed up many queries by providing efficient ways to locate records, but they require storage and can slow writes.",
            "Caching stores frequently accessed data for faster retrieval and reduced load on underlying systems.",
            "Concurrent requests can be handled using appropriate server workers, asynchronous processing, transactions, and concurrency controls.",
            "Backend APIs can be secured with authentication, authorization, input validation, HTTPS, rate limiting, and safe secret management."
        ]
    },

    "Java Developer": {
        "Beginner": [
            "Java is a high-level, class-based programming language designed to be portable across supported platforms.",
            "A class is a blueprint that defines the data and behavior of objects.",
            "An object is an instance of a class containing state and behavior.",
            "Inheritance allows a class to acquire accessible properties and methods from another class.",
            "The JVM, or Java Virtual Machine, executes Java bytecode."
        ],
        "Intermediate": [
            "Method overloading means defining methods with the same name but different parameter lists.",
            "Method overriding occurs when a subclass provides its own implementation of an inherited instance method.",
            "Exception handling uses try, catch, finally, throw, and throws to manage exceptional situations.",
            "An interface defines a contract that classes can implement. An abstract class can also contain instance state and implemented methods.",
            "The Java Collections Framework provides data structures and algorithms for working with groups of objects."
        ],
        "Advanced": [
            "Multithreading allows multiple threads to execute concurrently within a program.",
            "Garbage collection automatically reclaims memory occupied by objects that are no longer reachable.",
            "The Java Memory Model defines how threads interact through memory and when writes become visible to other threads.",
            "Java streams support declarative processing of data sequences through operations such as filter, map, and reduce.",
            "HashMap stores key-value pairs and uses hashing to locate entries. Its internal implementation and collision handling depend on the Java version."
        ]
    },

    "Full Stack Developer": {
        "Beginner": [
            "Full stack development involves working with both frontend interfaces and backend systems.",
            "HTML defines the structure of a web page.",
            "CSS controls the design and layout of a web page.",
            "JavaScript adds interactive behavior to web applications.",
            "A database stores application data in an organized form."
        ],
        "Intermediate": [
            "The frontend communicates with the backend through HTTP requests, commonly using APIs.",
            "A REST API allows clients to interact with server-side resources using HTTP methods.",
            "CRUD stands for Create, Read, Update, and Delete—the four common data operations.",
            "Session management maintains information about a user's interaction across multiple requests.",
            "A web application connects to a database through backend code and a database driver or ORM."
        ],
        "Advanced": [
            "A full stack application can be designed using separate UI, application logic, and data layers with clearly defined interfaces.",
            "Secure authentication requires safe password hashing, secure session handling, HTTPS, and appropriate access controls.",
            "Performance can be improved through caching, optimized database queries, efficient frontend assets, and suitable scaling.",
            "Errors should be handled with validation, consistent API responses, logging, and appropriate user-facing messages.",
            "Deployment typically involves configuring the production server, environment variables, database, HTTPS, logging, and monitoring."
        ]
    },

    "Data Scientist": {
        "Beginner": [
            "Data science combines statistics, programming, and domain knowledge to extract useful insights from data.",
            "A dataset is a collection of related observations and variables.",
            "The mean is the arithmetic average, while the median is the middle value after sorting the data.",
            "Python is used for data cleaning, analysis, visualization, and machine learning.",
            "Data visualization presents information graphically to help people understand patterns and trends."
        ],
        "Intermediate": [
            "Data preprocessing prepares raw data by handling missing values, inconsistent formats, duplicates, and other quality issues.",
            "Supervised learning uses labeled examples, while unsupervised learning looks for patterns in data without target labels.",
            "Overfitting occurs when a model learns training data too closely and performs poorly on unseen data.",
            "A confusion matrix compares predicted classes with actual classes to summarize classification performance.",
            "Feature engineering creates or transforms input variables to help a model learn useful patterns."
        ],
        "Advanced": [
            "The bias-variance trade-off describes balancing errors from overly simple models against sensitivity to training data.",
            "Imbalanced datasets can be handled using suitable metrics, class weights, resampling, and careful validation.",
            "Cross-validation evaluates a model across multiple data splits to estimate its ability to generalize.",
            "Classification models can be evaluated using metrics such as precision, recall, F1-score, ROC-AUC, and accuracy when appropriate.",
            "Feature selection can use domain knowledge, statistical tests, regularization, or model-based importance while avoiding data leakage."
        ]
    },

    "Software Developer": {
        "Beginner": [
            "Software development is the process of designing, building, testing, and maintaining software.",
            "A programming language provides rules and syntax for writing instructions that a computer can execute.",
            "Object-oriented programming organizes software around objects that combine data and behavior.",
            "An algorithm is a sequence of steps for solving a problem.",
            "A data structure organizes data so it can be accessed and modified efficiently."
        ],
        "Intermediate": [
            "The four commonly taught OOP principles are encapsulation, abstraction, inheritance, and polymorphism.",
            "A stack follows Last In, First Out (LIFO), while a queue generally follows First In, First Out (FIFO).",
            "Version control tracks changes to files and helps developers collaborate. Git is a widely used example.",
            "The Software Development Life Cycle includes activities such as planning, analysis, design, implementation, testing, deployment, and maintenance.",
            "Unit testing checks small, isolated parts of a program, such as individual functions or methods."
        ],
        "Advanced": [
            "Design patterns are reusable approaches to common software design problems, such as Factory, Strategy, and Observer.",
            "Time complexity describes how an algorithm's running time grows with input size, commonly expressed using Big O notation.",
            "A monolithic application is organized as a single deployable unit, while microservices split functionality into independently deployable services.",
            "Complex bugs can be investigated using reproducible test cases, debugging tools, logs, and systematic isolation of possible causes.",
            "Maintainable software benefits from modular design, readable code, automated tests, documentation, and consistent coding standards."
        ]
    }
}

@app.route("/interview", methods=["GET", "POST"])
def interview():
    if "user_name" not in session:
        return redirect("/login")

    selected_role = ""
    selected_level = "Beginner"
    questions = []

    if request.method == "POST":
        selected_role = request.form.get("role", "")
        selected_level = request.form.get("level", "Beginner")

        if selected_role in INTERVIEW_QUESTIONS:
            questions = INTERVIEW_QUESTIONS[selected_role].get(
                selected_level, []
            )

    role_options = ""

    for role in INTERVIEW_QUESTIONS:
        selected = "selected" if role == selected_role else ""
        role_options += (
            f'<option value="{role}" {selected}>{role}</option>'
        )

    level_options = ""

    for level in ["Beginner", "Intermediate", "Advanced"]:
        selected = "selected" if level == selected_level else ""
        level_options += (
            f'<option value="{level}" {selected}>{level}</option>'
        )

    questions_html = ""

    answers = INTERVIEW_ANSWERS.get(
        selected_role, {}
    ).get(selected_level, [])

    for index, question in enumerate(questions, start=1):

        answer = answers[index - 1] if index <= len(answers) else (
            "A suggested answer is not available for this question yet."
        )

        questions_html += f"""
            <li style="margin-bottom: 20px;">
                <strong>{question}</strong>

                <p style="
                    background: #eef4ff;
                    padding: 12px;
                    border-radius: 8px;
                    margin-top: 8px;
                ">
                    <strong>💡 Suggested Answer:</strong><br>
                    {answer}
                </p>
            </li>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Career Forge - Interview Preparation</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                padding: 25px;
            }}

            .container {{
                max-width: 750px;
                margin: auto;
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 3px 12px #cccccc;
            }}

            h1 {{
                color: #243b64;
            }}

            select, button {{
                padding: 10px;
                margin: 8px 0 15px;
                width: 100%;
                border-radius: 6px;
                border: 1px solid #cccccc;
                font-size: 15px;
            }}

            button {{
                background: #243b64;
                color: white;
                cursor: pointer;
            }}

            button:hover {{
                background: #36558a;
            }}

            li {{
                margin: 12px 0;
                line-height: 1.5;
            }}

            .back {{
                display: inline-block;
                margin-top: 20px;
                color: #243b64;
                text-decoration: none;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <h1>🎤 Interview Preparation</h1>

            <p>Practice questions for your target job role.</p>

            <form method="POST" action="/interview">
                <label><strong>Select Job Role:</strong></label>

                <select name="role" required>
                    <option value="">Choose a role</option>
                    {role_options}
                </select>

                <label><strong>Select Difficulty:</strong></label>

                <select name="level">
                    {level_options}
                </select>

                <button type="submit">Generate Questions</button>
            </form>

            <hr>

            <h2>{selected_role} - {selected_level}</h2>

            <ol>
                {questions_html}
            </ol>

            <a class="back" href="/dashboard">← Back to Dashboard</a>
        </div>
    </body>
    </html>
    """

# Run App
if __name__ == "__main__":
    app.run(debug=True)

