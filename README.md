# intern-hunters-backend
FastAPI on Python 3.12

## 🚀 How to Run

0. Generate the following secrets yourself to put in the .env
    1. DATABASE_URL
        * You MUST supply an async engine to use your db with (app currently works on postgresql and sqlite)
    2. SYNC_DATABASE_URL
        * You MUST supply the sync engine version of the db you are using for alembic
    3. JWT_SECRET_KEY
        * Use a command like `openssl rand -hex 32` on CLI etc
    4. REFRESH_TOKEN_SECRET_KEY
        * See sub point for 3.
    5. AWS_ACCESS_KEY_ID
        * Note this is used for boto3, so you can use other services like R2
    6. AWS_SECRET_ACCESS_KEY
        * See sub point for 5.
    7. R2_BUCKET_URL
        * You can also use S3 bucket urls
    8. R2_BUCKET_NAME
        * See sub point for 7.
    9. R2_REGION
        * See sub point for 7.
1. Put .env in same folder as dev.py
2. Install dependencies with `pip install -r requirements.txt`
3. Run `alembic upgrade head`
4. Start the development server using `python dev.py`. 

