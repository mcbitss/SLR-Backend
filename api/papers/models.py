"""
Simple API Models - Request and Response models
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Request Models
class FilterRequest(BaseModel):
    """Request model for filtering papers"""
    study_types: Optional[List[str]] = []
    phases: Optional[List[str]] = []
    pharma_groups: Optional[List[str]] = []
    page: int = 1
    limit: int = 15

# Response Models
class PaperSummary(BaseModel):
    """Paper model for list view"""
    work_id: str
    title: str
    abstract: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[str] = None
    publication_year: Optional[int] = None

class PaperDetail(BaseModel):
    """Paper model for detail view"""
    work_id: str
    title: str
    abstract: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[str] = None
    publication_year: Optional[int] = None
    authorships: Optional[str] = None
    output: Optional[str] = None

class FilterOptions(BaseModel):
    """Available filter options"""
    study_types: List[str]
    phases: List[str]
    pharma_groups: List[str]

class PaginatedResponse(BaseModel):
    """Paginated response for papers"""
    data: List[PaperSummary]
    pagination: Dict[str, Any]
    filters_applied: Dict[str, Any]