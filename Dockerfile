# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

EXPOSE 8080

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install apt and texlive
RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    gnupg \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    texlive-latex-extra \
    git \
 && apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy alembic related stuff
COPY /alembic alembic/
COPY alembic.ini .

# Copy my tests
COPY /tests tests/

COPY app app/

# Copy start script for use in dev environment (overrides CMD line below)
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "-k", "uvicorn_worker.UvicornWorker", "app.main:app"]
