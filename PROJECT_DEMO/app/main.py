# -*- coding: utf-8 -*-
"""Application FastAPI — SOUMISSION.DZ v5.0."""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app import __version__
from app.config import get_settings
from app.routers import admin as admin_router
from app.routers import assistance as assistance_router
from app.routers import billing as billing_router
from app.routers import conformite as conformite_router
from app.routers import parrainage_hotline as ph_router
from app.routers import auth as auth_router
from app.routers import signup as signup_router
from app.routers import team as team_router
from app.routers import coffre as coffre_router
from app.routers import references as references_router
from app.routers import ao as ao_router
from app.routers import prix as prix_router
from app.routers import templates as templates_router
from app.routers import memoire as memoire_router
from app.routers import dossiers as dossiers_router
from app.routers import cabinet as cabinet_router


def _configure_logging() -> None:
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level,
        serialize=True,
        backtrace=False,
        diagnose=False,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    settings = get_settings()
    logger.info(
        "startup",
        version=__version__,
        env=settings.env,
        db=settings.database_url.split("@")[-1],
    )
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    """Factory FastAPI. Utilisée par uvicorn et les tests."""
    app = FastAPI(
        title="SOUMISSION.DZ",
        description="Plateforme SaaS d'aide aux soumissions marches publics algeriens.",
        version=__version__,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(signup_router.router)
    app.include_router(auth_router.router)
    app.include_router(team_router.router)
    app.include_router(coffre_router.router)
    app.include_router(references_router.router)
    app.include_router(ao_router.router)
    app.include_router(prix_router.router)
    app.include_router(templates_router.router)
    app.include_router(memoire_router.router_memoire)
    app.include_router(memoire_router.router_formulaires)
    app.include_router(dossiers_router.router_dossiers)
    app.include_router(dossiers_router.router_cautions)
    app.include_router(dossiers_router.router_soumissions)
    app.include_router(cabinet_router.router)
    app.include_router(assistance_router.router_catalogue)
    app.include_router(assistance_router.router_missions)
    app.include_router(assistance_router.router_mandat_journal)
    app.include_router(assistance_router.router_messages)
    app.include_router(admin_router.router)
    app.include_router(billing_router.router_plans)
    app.include_router(billing_router.router_abos)
    app.include_router(billing_router.router_factures)
    app.include_router(ph_router.router_parrainage)
    app.include_router(ph_router.router_hotline)
    app.include_router(conformite_router.router)

    @app.get("/health", tags=["system"])
    def health() -> dict:
        return {"status": "ok", "version": __version__}

    @app.get("/", include_in_schema=False)
    def root():
        from fastapi.responses import FileResponse
        from pathlib import Path
        idx = Path("static/index.html")
        if idx.exists():
            return FileResponse(idx)
        return {"app": "SOUMISSION.DZ", "version": __version__, "docs": "/docs"}

    # Front statique minimal
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except RuntimeError:
        pass

    return app


app = create_app()
