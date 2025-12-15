from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
import logging

from models import User, BiomarkerUpload, BiomarkerData, AnalysisResult
from dependencies import get_db, get_current_user
from utils import calculate_health_analysis


router = APIRouter(prefix="/biomarkers", tags=["Biomarkers"])




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


@router.get("/analysis/{upload_id}")
def get_analysis(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analysis for a specific upload"""
    
    upload = db.query(BiomarkerUpload).filter(BiomarkerUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    if upload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    biomarkers = db.query(BiomarkerData).filter(
        BiomarkerData.upload_id == upload_id
    ).order_by(BiomarkerData.date).all()
    
    analysis = db.query(AnalysisResult).filter(
        AnalysisResult.upload_id == upload_id
    ).first()
    
    return {
        "upload": {
            "id": upload.id,
            "filename": upload.filename,
            "upload_date": upload.upload_date.isoformat(),
            "status": upload.status
        },
        "biomarkers": [
            {
                "date": b.date.isoformat(),
                "cholesterol_total": b.cholesterol_total,
                "hdl": b.hdl,
                "ldl": b.ldl,
                "triglycerides": b.triglycerides,
                "glucose": b.glucose,
                "crp": b.crp,
                "vitamin_d": b.vitamin_d
            }
            for b in biomarkers
        ],
        "analysis": {
            "biological_age": analysis.biological_age,
            "chronological_age": analysis.chronological_age,
            "age_difference": analysis.chronological_age - analysis.biological_age,
            "inflammation_score": analysis.inflammation_score,
            "metabolic_health_score": analysis.metabolic_health_score,
            "cardiovascular_risk": analysis.cardiovascular_risk,
            "calculated_at": analysis.calculated_at.isoformat()
        } if analysis else None
    }


@router.delete("/{upload_id}")
def delete_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an upload and all associated data"""
    
    upload = db.query(BiomarkerUpload).filter(BiomarkerUpload.id == upload_id).first()
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found"
        )
    
    if upload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(upload)
    db.commit()
    
    return {"message": "Upload deleted successfully"}


@router.get("/summary")
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive summary of user's biomarker data and health trends"""
    
    uploads = db.query(BiomarkerUpload).filter(
        BiomarkerUpload.user_id == current_user.id
    ).order_by(BiomarkerUpload.upload_date.desc()).all()
    
    if not uploads:
        return {
            "message": "No biomarker data uploaded yet",
            "total_uploads": 0,
            "latest_analysis": None,
            "health_trends": None,
            "recommendations": []
        }
    
    latest_upload = uploads[0]
    
    latest_analysis = db.query(AnalysisResult).filter(
        AnalysisResult.upload_id == latest_upload.id
    ).first()
    
    latest_biomarkers = db.query(BiomarkerData).filter(
        BiomarkerData.upload_id == latest_upload.id
    ).order_by(BiomarkerData.date.desc()).first()
    
    # Calculate trends if there are multiple uploads
    trends = None
    if len(uploads) >= 2:
        previous_upload = uploads[1]
        previous_analysis = db.query(AnalysisResult).filter(
            AnalysisResult.upload_id == previous_upload.id
        ).first()
        
        if previous_analysis and latest_analysis:
            trends = {
                "biological_age": {
                    "current": latest_analysis.biological_age,
                    "previous": previous_analysis.biological_age,
                    "change": round(latest_analysis.biological_age - previous_analysis.biological_age, 1),
                    "improving": latest_analysis.biological_age < previous_analysis.biological_age
                },
                "inflammation_score": {
                    "current": latest_analysis.inflammation_score,
                    "previous": previous_analysis.inflammation_score,
                    "change": round(latest_analysis.inflammation_score - previous_analysis.inflammation_score, 1),
                    "improving": latest_analysis.inflammation_score > previous_analysis.inflammation_score
                },
                "metabolic_health_score": {
                    "current": latest_analysis.metabolic_health_score,
                    "previous": previous_analysis.metabolic_health_score,
                    "change": round(latest_analysis.metabolic_health_score - previous_analysis.metabolic_health_score, 1),
                    "improving": latest_analysis.metabolic_health_score > previous_analysis.metabolic_health_score
                }
            }
    
    # Generate personalized recommendations
    recommendations = []
    if latest_biomarkers and latest_analysis:
        # Inflammation recommendations
        if latest_biomarkers.crp > 3.0:
            recommendations.append({
                "category": "inflammation",
                "priority": "high",
                "message": "Your CRP levels indicate high inflammation. Consider anti-inflammatory diet and exercise."
            })
        elif latest_biomarkers.crp > 1.0:
            recommendations.append({
                "category": "inflammation",
                "priority": "medium",
                "message": "Your inflammation markers are moderate. Focus on whole foods and regular movement."
            })
        
        # Metabolic health recommendations
        if latest_biomarkers.glucose >= 126:
            recommendations.append({
                "category": "metabolic",
                "priority": "high",
                "message": "Glucose levels in diabetic range. Please consult with healthcare provider."
            })
        elif latest_biomarkers.glucose >= 100:
            recommendations.append({
                "category": "metabolic",
                "priority": "medium",
                "message": "Pre-diabetic glucose levels. Consider reducing refined carbs and increasing physical activity."
            })
        
        # Cardiovascular recommendations
        if latest_analysis.cardiovascular_risk == "high":
            recommendations.append({
                "category": "cardiovascular",
                "priority": "high",
                "message": "High cardiovascular risk. Focus on improving HDL and reducing LDL cholesterol."
            })
        
        # Vitamin D recommendations
        if latest_biomarkers.vitamin_d < 20:
            recommendations.append({
                "category": "vitamins",
                "priority": "medium",
                "message": "Vitamin D deficiency detected. Consider supplementation and safe sun exposure."
            })
        elif latest_biomarkers.vitamin_d < 30:
            recommendations.append({
                "category": "vitamins",
                "priority": "low",
                "message": "Vitamin D levels are suboptimal. Aim for levels above 40 ng/mL."
            })
        
        # Positive feedback
        if latest_analysis.biological_age < latest_analysis.chronological_age:
            age_diff = abs(round(latest_analysis.chronological_age - latest_analysis.biological_age, 1))
            recommendations.append({
                "category": "positive",
                "priority": "info",
                "message": f"Great job! Your biological age is {age_diff} years younger than your chronological age."
            })
    
    # Determine overall health status
    overall_status = None
    if latest_analysis:
        age_diff = latest_analysis.biological_age - latest_analysis.chronological_age
        
        if age_diff < -2:
            status_label = "excellent"
            status_desc = "Your biomarkers indicate healthy aging"
        elif age_diff <= 0:
            status_label = "good"
            status_desc = "Your biomarkers are within normal ranges"
        elif age_diff <= 3:
            status_label = "fair"
            status_desc = "Your biomarkers are within normal ranges"
        else:
            status_label = "needs_attention"
            status_desc = "Consider lifestyle improvements to optimize health markers"
        
        overall_status = {
            "status": status_label,
            "description": status_desc
        }
    
    return {
        "user": {
            "name": current_user.full_name,
            "email": current_user.email
        },
        "total_uploads": len(uploads),
        "latest_upload": {
            "id": latest_upload.id,
            "filename": latest_upload.filename,
            "date": latest_upload.upload_date.isoformat(),
            "status": latest_upload.status
        },
        "latest_analysis": {
            "biological_age": latest_analysis.biological_age,
            "chronological_age": latest_analysis.chronological_age,
            "age_difference": round(latest_analysis.chronological_age - latest_analysis.biological_age, 1),
            "inflammation_score": latest_analysis.inflammation_score,
            "metabolic_health_score": latest_analysis.metabolic_health_score,
            "cardiovascular_risk": latest_analysis.cardiovascular_risk,
            "calculated_at": latest_analysis.calculated_at.isoformat()
        } if latest_analysis else None,
        "latest_biomarkers": {
            "date": latest_biomarkers.date.isoformat(),
            "cholesterol_total": latest_biomarkers.cholesterol_total,
            "hdl": latest_biomarkers.hdl,
            "ldl": latest_biomarkers.ldl,
            "triglycerides": latest_biomarkers.triglycerides,
            "glucose": latest_biomarkers.glucose,
            "crp": latest_biomarkers.crp,
            "vitamin_d": latest_biomarkers.vitamin_d,
            "cholesterol_hdl_ratio": round(latest_biomarkers.cholesterol_total / latest_biomarkers.hdl, 2)
        } if latest_biomarkers else None,
        "health_trends": trends,
        "recommendations": recommendations,
        "overall_health_status": overall_status
    }