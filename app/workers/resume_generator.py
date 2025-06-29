"""Modules relevant for resume creator service. Uses subprocess to execute in background"""
import subprocess
import os
import uuid
from io import BytesIO

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.schemas.resume_editor import Resume
from app.exceptions.resume_creator_exceptions import ResumeCreatorDown

def create_from_template(details: Resume, user_id: uuid.UUID):
    """Creates a new resume pdf given resume details by spawning a subprocess to call pdflatex."""
    try:
        current_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(current_dir / "templates"))
        template = env.get_template("resume_template.tex.jinja2")
        rendered_tex = template.render(details)
        output_path = f"{user_id}_resume.tex"
        with open(output_path, "w") as f:
            f.write(rendered_tex)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", output_path])
        pdf_path = f"{user_id}_resume.pdf"
        result = BytesIO()
        with open(pdf_path, "rb") as f:
            result.write(f.read())
        result.seek(0)
        return result
    except Exception as e:
        raise ResumeCreatorDown from e
    finally:
        os.remove(f"{user_id}_resume.tex")
        os.remove(f"{user_id}_resume.aux")
        os.remove(f"{user_id}_resume.log")
        os.remove(f"{user_id}_resume.out")
        os.remove(f"{user_id}_resume.pdf")
