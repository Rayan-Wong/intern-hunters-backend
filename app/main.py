"""Modules for FastAPI dependencies, setting up routers and db connection"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from .api import routes_auth, routes_applications
from .openapi import tags_metadata

app = FastAPI(openapi_tags=tags_metadata)

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
app.include_router(routes_applications.router)

init_db()

@app.get("/")
async def root():
    """Endpoint to check if server is alive"""
    return {"message": "ur mum"}
