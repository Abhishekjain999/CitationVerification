from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from sqlalchemy import update, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse
import logging
from app.api.papers import router as papers_router
from app.api.references import router as references_router
from app.api.demo import router as demo_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    try:
        await init_db()
        from app.models.paper import Paper
        async with AsyncSessionLocal() as db:
            await db.execute(update(Paper).where(Paper.processing_status == 'processing').values(processing_status='failed', error_message='Analysis interrupted by server restart. Retry the analysis.', progress_stage='Interrupted'))
            await db.commit()
    except SQLAlchemyError:
        logging.exception('Database initialization failed. Check DATABASE_URL and database availability.')
    yield
    # Shutdown: cleanups if necessary

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ResearchGuard - AI/NLP Research Paper & Reference Verification System",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(papers_router, prefix=settings.API_V1_STR)
app.include_router(references_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "documentation": "/docs",
        "endpoints": {
            "upload": "/api/papers/upload",
            "papers": "/api/papers",
            "demo": "/api/demo/load"
        }
    }

@app.get("/api/health")
async def health_check():
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text('SELECT 1'))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={'status': 'unavailable', 'detail': 'Database unavailable. Check DATABASE_URL and connectivity.'})
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request, exc):
    logging.exception('Database request failed', exc_info=exc)
    return JSONResponse(status_code=503, content={'detail': 'Database unavailable. Check DATABASE_URL and connectivity.'})
