"""Modules relevant for resume creator service. Uses subprocess to execute in background"""
import subprocess
import uuid
from io import BytesIO
from tempfile import TemporaryDirectory

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.schemas.resume_editor import Resume
from app.exceptions.resume_creator_exceptions import ResumeCreatorDown
from app.core.timer import timed
from app.core.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

@timed("Resume Creating")
def create_from_template(details: Resume, user_id: uuid.UUID):
    """Creates a new resume pdf given resume details by spawning a subprocess to call pdflatex."""
    try:
        logger.info(f"Beginning resume creation for {user_id}.")
        current_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(current_dir / "templates"))
        template = env.get_template("resume_template.tex.jinja2")
        rendered_tex = template.render(details)
        with TemporaryDirectory() as tempdir:
            output_path = Path(tempdir) / f"{user_id}_resume.tex"
            with open(output_path, "w") as f:
                f.write(rendered_tex)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", output_path], cwd=tempdir)
            pdf_path = Path(tempdir) / f"{user_id}_resume.pdf"
            result = BytesIO()
            with open(pdf_path, "rb") as f:
                result.write(f.read())
            result.seek(0)
        logger.info(f"Resume created for {user_id}.")
        return result
    except Exception as e:
        logger.error(f"Failed to create resume for {user_id}.")
        raise ResumeCreatorDown from e
