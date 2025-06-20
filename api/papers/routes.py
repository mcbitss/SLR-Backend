"""
Optimized API Routes - Reduced redundancy
"""
from fastapi import APIRouter, HTTPException, Query
import logging
import math
from typing import Optional, Dict, Any
from api.papers.models import FilterRequest, PaperSummary, PaperDetail, PaginatedResponse, FilterOptions
from services.papers.data_service import DataService
from services.papers.filter_service import FilterService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/papers", tags=["papers"])

# Initialize services
data_service = DataService()
filter_service = FilterService()

def _get_papers_data():
    """Helper: Get all papers with error handling"""
    try:
        return data_service.get_all_papers()
    except Exception as e:
        logger.error(f"Error getting papers data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch papers data")

def _create_paginated_response(papers_df, page: int, limit: int, filters_applied: Dict[str, Any] = None):
    """Helper: Create paginated response from papers dataframe"""
    if papers_df.empty:
        return PaginatedResponse(
            data=[], 
            pagination={
                "page": page, "limit": limit, "total": 0, "total_pages": 0, 
                "has_next": False, "has_previous": False
            },
            filters_applied=filters_applied or {}
        )
    
    # Apply pagination
    total = len(papers_df)
    total_pages = math.ceil(total / limit)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_data = papers_df.iloc[start_idx:end_idx]
    
    # Format papers for list view
    papers = []
    for _, row in page_data.iterrows():
        paper_data = data_service.format_paper(row, detail_view=False)
        papers.append(PaperSummary(**paper_data))
    
    return PaginatedResponse(
        data=papers,
        pagination={
            "page": page, "limit": limit, "total": total, "total_pages": total_pages,
            "has_next": page < total_pages, "has_previous": page > 1
        },
        filters_applied=filters_applied or {}
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        is_connected, message = data_service.test_connection()
        return {
            "status": "healthy" if is_connected else "unhealthy", 
            "database": message
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/filter-options", response_model=FilterOptions)
async def get_filter_options():
    """Get available filter options - dynamically extracted from data"""
    try:
        all_papers = _get_papers_data()
        options = filter_service.get_filter_options(all_papers)
        return FilterOptions(**options)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting filter options: {e}")
        raise HTTPException(status_code=500, detail="Failed to get filter options")

@router.get("/", response_model=PaginatedResponse)
async def get_papers(
    page: int = Query(1, ge=1), 
    limit: int = Query(15, ge=1, le=100)
):
    """Get papers with pagination"""
    all_papers = _get_papers_data()
    return _create_paginated_response(all_papers, page, limit)

@router.post("/filter", response_model=PaginatedResponse)
async def filter_papers(request: FilterRequest):
    """Filter papers with pagination"""
    try:
        all_papers = _get_papers_data()
        
        # Prepare filters (exclude pagination fields)
        filters = {
            k: v for k, v in request.dict().items() 
            if k not in ['page', 'limit'] and v
        }
        
        # Apply filters
        filtered_papers = filter_service.apply_filters(all_papers, filters)
        
        return _create_paginated_response(filtered_papers, request.page, request.limit, filters)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering papers: {e}")
        raise HTTPException(status_code=500, detail="Failed to filter papers")

@router.get("/count", response_model=dict)
async def get_papers_count(
    study_types: Optional[list] = Query(None),
    phases: Optional[list] = Query(None), 
    pharma_groups: Optional[list] = Query(None)
):
    """Get count of papers (total or filtered)"""
    try:
        all_papers = _get_papers_data()
        
        # If no filters provided, return total count
        if not any([study_types, phases, pharma_groups]):
            return {"total": len(all_papers)}
        
        # Apply filters and return filtered count
        filters = {}
        if study_types:
            filters['study_types'] = study_types
        if phases:
            filters['phases'] = phases
        if pharma_groups:
            filters['pharma_groups'] = pharma_groups
            
        filtered_papers = filter_service.apply_filters(all_papers, filters)
        return {
            "total": len(filtered_papers),
            "filters_applied": filters
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting papers count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get papers count")

@router.get("/{work_id}", response_model=PaperDetail)
async def get_paper_by_id(work_id: str):
    """Get paper details by ID"""
    try:
        paper_row = data_service.get_paper_by_id(work_id)
        
        if paper_row is None:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Format paper for detail view
        paper_data = data_service.format_paper(paper_row, detail_view=True)
        return PaperDetail(**paper_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting paper: {e}")
        raise HTTPException(status_code=500, detail="Failed to get paper")