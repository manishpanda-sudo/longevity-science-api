from fastapi import APIRouter
from routes.biomarkers.upload import router as upload_router
from routes.biomarkers.analysis import router as analysis_router
from routes.biomarkers.management import router as management_router

router = APIRouter(prefix="/biomarkers", tags=["Biomarkers"])

# Include all sub-routers
router.include_router(upload_router)
router.include_router(analysis_router)
router.include_router(management_router)

__all__ = ["router"]