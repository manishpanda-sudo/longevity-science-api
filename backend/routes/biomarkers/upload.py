from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io

from models import User, BiomarkerUpload, BiomarkerData, AnalysisResult
from dependencies import get_db, get_current_user
from utils import calculate_health_analysis

router = APIRouter()


@router.post("/upload")
async def upload_biomarkers(
    file: UploadFile = File(...),
    chronological_age: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload CSV file with biomarker data"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        required_columns = ['date', 'cholesterol_total', 'hdl', 'ldl', 'triglycerides', 'glucose', 'crp', 'vitamin_d']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        upload = BiomarkerUpload(
            user_id=current_user.id,
            filename=file.filename,
            status="processing"
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        
        biomarker_records = []
        for _, row in df.iterrows():
            biomarker = BiomarkerData(
                upload_id=upload.id,
                date=pd.to_datetime(row['date']),
                cholesterol_total=float(row['cholesterol_total']),
                hdl=float(row['hdl']),
                ldl=float(row['ldl']),
                triglycerides=float(row['triglycerides']),
                glucose=float(row['glucose']),
                crp=float(row['crp']),
                vitamin_d=float(row['vitamin_d'])
            )
            biomarker_records.append(biomarker)
        
        db.bulk_save_objects(biomarker_records)
        db.commit()
        
        latest_data = df.iloc[-1]
        analysis = calculate_health_analysis(latest_data, chronological_age)
        
        analysis_result = AnalysisResult(
            upload_id=upload.id,
            biological_age=analysis['biological_age'],
            chronological_age=chronological_age,
            inflammation_score=analysis['inflammation_score'],
            metabolic_health_score=analysis['metabolic_health_score'],
            cardiovascular_risk=analysis['cardiovascular_risk']
        )
        db.add(analysis_result)
        
        upload.status = "completed"
        db.commit()
        db.refresh(analysis_result)
        
        return {
            "message": "Biomarkers uploaded and analyzed successfully",
            "upload_id": upload.id,
            "records_processed": len(df),
            "analysis": {
                "biological_age": analysis_result.biological_age,
                "chronological_age": analysis_result.chronological_age,
                "age_difference": chronological_age - analysis_result.biological_age,
                "inflammation_score": analysis_result.inflammation_score,
                "metabolic_health_score": analysis_result.metabolic_health_score,
                "cardiovascular_risk": analysis_result.cardiovascular_risk,
                "calculated_at": analysis_result.calculated_at.isoformat()
            }
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty"
        )
    except Exception as e:
        db.rollback()
        if 'upload' in locals():
            upload.status = "failed"
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/uploads")
def get_user_uploads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all uploads for current user"""
    uploads = db.query(BiomarkerUpload).filter(
        BiomarkerUpload.user_id == current_user.id
    ).order_by(BiomarkerUpload.upload_date.desc()).all()
    
    return {
        "total_uploads": len(uploads),
        "uploads": [
            {
                "id": upload.id,
                "filename": upload.filename,
                "upload_date": upload.upload_date.isoformat(),
                "status": upload.status
            }
            for upload in uploads
        ]
    }