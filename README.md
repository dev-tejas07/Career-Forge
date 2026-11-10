# Career Forge
### Smart Resume Analyzer and Interview Preparation System

Career Forge is a web-based application developed to help job seekers analyze their resumes, identify technical skills, understand skill gaps, and prepare for job interviews.

The application provides resume analysis and career preparation tools through a simple and user-friendly web interface.

## Key Features

- **User Authentication:** Secure user registration and login.
- **Resume Upload:** Upload resumes in PDF format.
- **PDF Text Extraction:** Extract text from uploaded resumes.
- **Skill Detection:** Identify technical skills mentioned in resumes.
- **ATS Score Analysis:** Calculate a resume compatibility score.
- **Missing Skills Analysis:** Identify skills that may improve a candidate's profile.
- **Job Role Analysis:** Analyze resume skills against different job roles.
- **Resume Improvement Suggestions:** Help users identify areas for improvement.
- **Interview Preparation:** Practice role-based technical interview questions.

## Technologies Used

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python |
| Web Framework | Flask |
| Database | MySQL |
| Database Connector | PyMySQL |
| PDF Processing | PyPDF2 |
| Password Security | Werkzeug |
| Environment Variables | python-dotenv |
| Production Server | Gunicorn |

## Project Structure

Career-Forge/
│
├── app.py
├── career_db.sql
├── requirements.txt
├── Procfile
├── .gitignore
├── README.md
│
├── templates/
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── uploads/
```

**Note:** The `.env` file, virtual environment, test database scripts, and uploaded user resumes are excluded from the public repository for security reasons.

## Installation and Setup

Follow these steps to run Career Forge locally.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Career-Forge
```

### 2. Create a Virtual Environment

```bash
python -m venv career_env
```

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\career_env\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure MySQL Database

- Install and start MySQL Server.
- Open MySQL Workbench.
- Import or execute the `career_db.sql` file.
- Ensure the database named `career_forge` is created successfully.

### 6. Configure Environment Variables

Create a `.env` file in the project root directory.

Add the following configuration:

```env
FLASK_SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=career_forge
```

Replace the placeholder values with your own credentials.

**Important:** Never upload your `.env` file, database password, or secret key to GitHub.

### 7. Run the Application

Start the Flask application:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## Deployment

The application is prepared for deployment using Gunicorn through the included `Procfile`.

The deployment configuration and database hosting requirements must be configured separately.

## Future Enhancements

- AI-powered resume analysis and feedback.
- Advanced job matching and recommendations.
- Personalized interview preparation.
- Enhanced resume optimization tools.
- Cloud-based resume storage.

## Security

- Sensitive environment variables are stored separately in `.env`.
- Database credentials should never be committed to the repository.
- User-uploaded resumes and local development files are excluded from version control.

## Author

**Tejas Gupta**

B.Voc. Software Development

---

**Career Forge — Build Your Career with Confidence.**