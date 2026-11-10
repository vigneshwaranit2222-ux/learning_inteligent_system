from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class SkillCategorySchema(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class SkillCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class SkillAliasSchema(BaseModel):
    id: str
    alias: str
    normalized_alias: str

    class Config:
        from_attributes = True

class SkillSchema(BaseModel):
    id: str
    category_id: str
    name: str
    slug: str
    description: Optional[str] = None
    popularity_score: float = 1.0
    is_verified: bool = True
    category: Optional[SkillCategorySchema] = None
    aliases: List[SkillAliasSchema] = []

    class Config:
        from_attributes = True

class SkillCreate(BaseModel):
    name: str
    category_id: str
    description: Optional[str] = None
    aliases: List[str] = []

class SkillEvidenceResponse(BaseModel):
    id: str
    source_type: str
    source_id: Optional[str] = None
    text_snippet: str
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True

class LearnerSkillResponse(BaseModel):
    id: str
    skill_id: str
    skill: SkillSchema
    proficiency_level: int # 1: Beginner, 2: Intermediate, 3: Advanced, 4: Expert
    confidence_score: float
    years_experience: float
    last_used_date: Optional[str] = None
    evidence_summary: Optional[str] = None
    evidence_list: List[SkillEvidenceResponse] = []

    class Config:
        from_attributes = True

class ExtractedSkillItem(BaseModel):
    canonical_name: str
    category: str
    evidence_snippet: str
    confidence: float
    extraction_method: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None

class SkillExtractionResult(BaseModel):
    source_id: str
    source_type: str
    total_skills_extracted: int
    skills: List[ExtractedSkillItem]
