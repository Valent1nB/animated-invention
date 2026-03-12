"""
FastAPI application entry point.

This mirrors the structure in the referenced Clean Architecture article:
- imports the API router from the presentation layer
- exposes a single FastAPI `app` instance
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.presentation.api.auth_router import router as auth_router
from app.presentation.api.base_router import router as base_router
from app.presentation.api.employee_router import router as employee_router
from app.presentation.api.health_router import router as health_router
from app.presentation.api.intern_router import router as intern_router
from app.presentation.api.mentor_router import router as mentor_router
from app.presentation.api.request_router import router as request_router
from app.presentation.api.unit_router import router as unit_router

app = FastAPI(title="Project X")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_router.include_router(health_router)
base_router.include_router(auth_router)
base_router.include_router(mentor_router)
base_router.include_router(intern_router)
base_router.include_router(employee_router)
base_router.include_router(request_router)
base_router.include_router(unit_router)

app.include_router(base_router)
