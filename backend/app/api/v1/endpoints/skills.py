from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.models.skill import Skill, SkillCategory, SkillAlias
from app.schemas.skill import SkillSchema, SkillCategorySchema, ExtractedSkillItem, SkillExtractionResult
from ai_engine.extraction.extractor import extractor
from ai_engine.normalization.canonical_skills import normalize_skill_name

router = APIRouter(prefix="/skills", tags=["Skills"])

class TextExtractionRequest(BaseModel):
    text: str
    source_type: Optional[str] = "manual_input"

@router.get("/", response_model=List[SkillSchema])
def list_skills(
    query: Optional[str] = None,
    category_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    stmt = select(Skill)
    if query:
        stmt = stmt.where(Skill.name.ilike(f"%{query}%"))
    if category_id:
        stmt = stmt.where(Skill.category_id == category_id)
    stmt = stmt.offset(skip).limit(limit)
    skills = db.scalars(stmt).all()
    return skills

@router.get("/categories", response_model=List[SkillCategorySchema])
def list_categories(db: Session = Depends(get_db)):
    categories = db.scalars(select(SkillCategory)).all()
    return categories

@router.post("/extract", response_model=SkillExtractionResult)
def extract_skills_from_text_endpoint(req: TextExtractionRequest):
    extracted = extractor.extract_skills_from_text(req.text, source_type=req.source_type)
    return SkillExtractionResult(
        source_id="adhoc_request",
        source_type=req.source_type,
        total_skills_extracted=len(extracted),
        skills=[ExtractedSkillItem(**item) for item in extracted]
    )
