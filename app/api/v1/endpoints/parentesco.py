from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.parentesco import ParentescoCreate, ParentescoUpdate, ParentescoResponse
from app.services import parentesco as parentesco_service
from app.api import deps
from app.models.models import Usuario

router = APIRouter()

@router.post("/", response_model=ParentescoResponse)
def create_parentesco(parentesco: ParentescoCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return parentesco_service.create_parentesco(db=db, parentesco=parentesco)

@router.get("/", response_model=List[ParentescoResponse])
def read_parentescos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    return parentesco_service.get_parentescos(db, skip=skip, limit=limit)

@router.get("/{parentesco_id}", response_model=ParentescoResponse)
def read_parentesco(parentesco_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_parentesco = parentesco_service.get_parentesco(db, parentesco_id=parentesco_id)
    if db_parentesco is None:
        raise HTTPException(status_code=404, detail="Parentesco not found")
    return db_parentesco

@router.put("/{parentesco_id}", response_model=ParentescoResponse)
def update_parentesco(parentesco_id: int, parentesco: ParentescoUpdate, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_parentesco = parentesco_service.update_parentesco(db, parentesco_id=parentesco_id, parentesco=parentesco)
    if db_parentesco is None:
        raise HTTPException(status_code=404, detail="Parentesco not found")
    return db_parentesco

@router.delete("/{parentesco_id}", response_model=ParentescoResponse)
def delete_parentesco(parentesco_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(deps.get_current_user)):
    db_parentesco = parentesco_service.delete_parentesco(db, parentesco_id=parentesco_id)
    if db_parentesco is None:
        raise HTTPException(status_code=404, detail="Parentesco not found")
    return db_parentesco
