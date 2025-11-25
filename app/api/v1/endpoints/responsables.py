from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.responsable import ResponsableCreate, ResponsableUpdate, ResponsableResponse
from app.services import responsable as responsable_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ResponsableResponse)
def create_responsable(responsable: ResponsableCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return responsable_service.create_responsable(db=db, responsable=responsable)

@router.get("/", response_model=List[ResponsableResponse])
def read_responsables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return responsable_service.get_responsables(db, skip=skip, limit=limit)

@router.get("/{responsable_id}", response_model=ResponsableResponse)
def read_responsable(responsable_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_responsable = responsable_service.get_responsable(db, responsable_id=responsable_id)
    if db_responsable is None:
        raise HTTPException(status_code=404, detail="Responsable not found")
    return db_responsable

@router.put("/{responsable_id}", response_model=ResponsableResponse)
def update_responsable(responsable_id: int, responsable: ResponsableUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_responsable = responsable_service.update_responsable(db, responsable_id=responsable_id, responsable=responsable)
    if db_responsable is None:
        raise HTTPException(status_code=404, detail="Responsable not found")
    return db_responsable

@router.delete("/{responsable_id}", response_model=ResponsableResponse)
def delete_responsable(responsable_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_responsable = responsable_service.delete_responsable(db, responsable_id=responsable_id)
    if db_responsable is None:
        raise HTTPException(status_code=404, detail="Responsable not found")
    return db_responsable
