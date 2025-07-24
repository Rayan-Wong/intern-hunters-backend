"""Modules for FastAPI dependencies, setting up routers and db connection"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_auth, routes_applications, routes_internship_listings, routes_resume_creator
from .openapi import TAGS_METADATA, DESCRIPTION

# currently not in use since we are not using spaCy anymore
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Creates process pool for spacy since it is CPU intensive"""
#     pool.create_process_pool()
#     if pool.executor is None:
#         raise RuntimeError("Process pool failed to start")
#     yield

app = FastAPI(
    openapi_tags=TAGS_METADATA,
    # lifespan=lifespan, not in use, see above
    description=DESCRIPTION
)

origins = ["http://localhost:5173", "https://intern-hunters-lmewkotim-ophelia-neos-projects.vercel.app/"]
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
app.include_router(routes_internship_listings.router)
app.include_router(routes_resume_creator.router)

@app.get("/")
async def root():
    """Endpoint to check if server is alive"""
    return {"message": "I LIVE!"}
