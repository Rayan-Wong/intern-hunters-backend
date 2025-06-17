from jinja2 import Environment, FileSystemLoader
import subprocess
from pathlib import Path
import os

current_dir = Path(__file__).resolve().parent

env = Environment(loader=FileSystemLoader(current_dir / "templates"))
template = env.get_template("resume_template.tex.jinja2")

context = {
    "name": "Jane Doe",
    "phone": "+65 1234 5678",
    "email": "jane@example.com",
    "linkedin_link": "https://linkedin.com/in/janedoe",
    "linkedin_text": "linkedin.com/in/janedoe",
    "education": 
    [
        {
        "institution": "NUS",
        "location": "Singapore",
        "degree": "B.Comp (Computer Engineering)",
        "start_date": "Aug 2023",
        "end_date": "May 2027",
        "gpa": "4.6 / 5.0",
        "relevant_coursework": "Data Structures, Algorithms",
        "activities": "Dean’s List (2024)"
        }
    ],
    "experience": [
        {
            "company": "NTT Data",
            "location": "Singapore",
            "position": "Backend Intern",
            "start_date": "May 2024",
            "end_date": "Aug 2024",
            "bullets": [
                "Built internal tools for tracking microservice performance.",
                "Integrated metrics collection via Prometheus."
            ]
        },
        {
            "company": "Personal Project",
            "location": "Remote",
            "position": "Full Stack Developer",
            "start_date": "Jan 2023",
            "end_date": "Apr 2023",
            "bullets": [
                "Developed a resume parsing app using FastAPI and React.",
                "Deployed to AWS with CI/CD pipelines via GitHub Actions."
            ]
        }
    ],
    "projects": [
        {
            "name": "Resume Parser API",
            "location": "GitHub",
            "description": "A backend service for parsing resumes.",
            "start_date": "2025",
            "end_date": "Present",
            "bullets": [
                "Built a resume parsing backend with spaCy NLP pipeline.",
                "Exposed asynchronous endpoints using FastAPI.",
                "Deployed via Docker and CI with GitHub Actions."
            ]
        },
        {
            "name": "Portfolio Website",
            "location": "Personal",
            "description": "Static site built with Next.js and Tailwind CSS.",
            "start_date": "2024",
            "end_date": "2024",
            "bullets": [
                "Designed responsive UI components with Tailwind CSS.",
                "Implemented SEO-friendly static generation.",
                "Deployed on Vercel with a custom domain."
            ]
        }
    ],
    "skills": [
        {
            "category": "Languages",
            "items": ["Python", "C++", "JavaScript"]
        },
        {
            "category": "Tools",
            "items": ["Docker", "PostgreSQL", "Git"]
        }
    ]
}

rendered_tex = template.render(context)

output_path = "resume.tex"
with open(output_path, "w") as f:
    f.write(rendered_tex)

subprocess.run(["pdflatex", "-interaction=nonstopmode", output_path], check=True)
os.remove("resume.tex")
os.remove("resume.aux")
os.remove("resume.log")
os.remove("resume.out")
