from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_auth

from app.db.init_db import init_db

app = FastAPI()

# or wherever frontend is
origins = ["http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# principle: main composes routers
# api routes expose endpoints
# services do the actual logic
app.include_router(routes_auth.router)

init_db()

@app.get("/")
async def root():
    return {"message": "ur mum"}