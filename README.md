# intern-hunters-backend

A backend service for **Intern Hunters** — a full-stack application that helps students track internship applications and discover new opportunities, featuring intelligent resume parsing, job scraping, and performance-optimised infrastructure.

## Features

- **RESTful API** built with FastAPI for CRUD operations
- **Authentication** system with JWTs and refresh tokens for secure access
- **Redis caching** with pagination and partial cache hits to reduce response times
- **Asynchronous endpoints** with CPU-bound task offloading for scalability
- **AI-driven resume parsing** using Google Gemini for structured data extraction
- **AWS deployment**: ECR, ECS, RDS, ElastiCache in a custom VPC with security groups
- **CI/CD pipeline** via GitHub Actions with OIDC role assumption for automated testing and deployment
- **Dockerised development** environment using Docker Compose for consistency across machines
- **Structured logging** and execution timing instrumentation for performance diagnostics
- **Database migrations** managed by Alembic for version control

## Tech Stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Object Storage:** Cloudflare R2
- **Cache:** Redis, ElastiCache
- **AI Services:** Google Gemini
- **DevOps:** Docker, Docker Compose, GitHub Actions, AWS ECR/ECS/RDS/VPC/IAM
- **Migrations:** Alembic

## 🚀 How to Run

0. Generate the following secret and store it in a `.env` file:
   - `GEMINI_API_KEY`: Your Google Gemini API key
1. Place the `.env` file in the same folder as `dev.py`.
2. Build and start the container:
   ```bash
   docker compose up --build -d