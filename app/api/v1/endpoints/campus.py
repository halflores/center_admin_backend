from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.campus import CampusCreate, CampusUpdate, CampusResponse
from app.services import campus as campus_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=CampusResponse)
def create_campus(campus: CampusCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return campus_service.create_campus(db=db, campus=campus)

@router.get("/", response_model=List[CampusResponse])
def read_campuses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return campus_service.get_campuses(db, skip=skip, limit=limit)

@router.get("/{campus_id}", response_model=CampusResponse)
def read_campus(campus_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_campus = campus_service.get_campus(db, campus_id=campus_id)
    if db_campus is None:
        raise HTTPException(status_code=404, detail="Campus not found")
    return db_campus

@router.put("/{campus_id}", response_model=CampusResponse)
def update_campus(campus_id: int, campus: CampusUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_campus = campus_service.update_campus(db, campus_id=campus_id, campus=campus)
    if db_campus is None:
        raise HTTPException(status_code=404, detail="Campus not found")
    return db_campus

@router.delete("/{campus_id}", response_model=CampusResponse)
def delete_campus(campus_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_campus = campus_service.delete_campus(db, campus_id=campus_id)
    if db_campus is None:
        raise HTTPException(status_code=404, detail="Campus not found")
    return db_campus
