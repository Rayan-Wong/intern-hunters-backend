from jinja2 import Environment, FileSystemLoader
import subprocess
from pathlib import Path
import os

def test_template():
    try:
        current_dir = Path(__file__).resolve().parent

        env = Environment(loader=FileSystemLoader(current_dir / "templates"))
        template = env.get_template("resume_template.tex.jinja2")

        context = {
          "name": "Admin",
          "email": "admin@gmail.com",
          "linkedin_link": "linkedin.com/in/admin",
          "education": [
            {
              "institution": "National University of Singapore (NUS)",
              "location": "Singapore",
              "degree": "Bachelor of Science in Skibidilogy",
              "start_date": "2024",
              "end_date": "2027",
            }
          ],
          "skills": [
            {
              "category": "Programming Languages",
              "items": [
                "Python",
                "C",
                "C++",
                "SQL",
                "JavaScript",
                "TypeScript"
              ]
            }
          ]
        }
        rendered_tex = template.render(context)
        output_path = "resume.tex"

        with open(output_path, "w") as f:
            f.write(rendered_tex)

        subprocess.run(["pdflatex", "-interaction=nonstopmode", output_path], check=True)
    finally:
        os.remove("resume.tex")
        os.remove("resume.aux")
        os.remove("resume.log")
        os.remove("resume.out")

test_template()