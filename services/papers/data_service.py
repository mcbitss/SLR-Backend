"""
Simple Data Service - Database + Basic Formatting
"""
import pandas as pd
import psycopg2
import logging
import re
from config.database import DatabaseConfig

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self):
        self.config = DatabaseConfig()
    
    def get_all_papers(self):
        """Get all papers from database"""
        try:
            conn = psycopg2.connect(**self.config.get_psycopg2_params())
            
            query = """
                SELECT work_id, title, abstract, doi, 
                       authorships, publication_year, output
                FROM ibd_rcts 
                WHERE title IS NOT NULL AND abstract IS NOT NULL
                ORDER BY publication_year DESC
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            logger.info(f"Fetched {len(df)} papers")
            return df
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            return pd.DataFrame()
    
    def get_paper_by_id(self, work_id: str):
        """Get single paper by ID"""
        try:
            conn = psycopg2.connect(**self.config.get_psycopg2_params())
            
            query = """
                SELECT work_id, title, abstract, doi, 
                       authorships, publication_year, output
                FROM ibd_rcts 
                WHERE work_id = %s
            """
            
            df = pd.read_sql(query, conn, params=[work_id])
            conn.close()
            
            if not df.empty:
                return df.iloc[0]
            return None
            
        except Exception as e:
            logger.error(f"Database error: {e}")
            return None
    
    def format_paper(self, row, detail_view=False):
        """Format paper for both list and detail views"""
        # Base paper data (used for both views)
        paper = {
            "work_id": str(row.get('work_id', '')),
            "title": self._clean_text(str(row.get('title', ''))),
            "doi": str(row.get('doi', '')) if row.get('doi') else None,
            "authors": self._parse_authors(row.get('authorships', '')),
            "publication_year": int(row.get('publication_year')) if row.get('publication_year') else None
        }
        
        # Handle abstract based on view type
        if detail_view:
            # Full abstract for detail view
            paper["abstract"] = self._clean_text(str(row.get('abstract', '')))
            # Extra fields for detail view
            paper["authorships"] = str(row.get('authorships', '')) if row.get('authorships') else None
            paper["output"] = str(row.get('output', '')) if row.get('output') else None
        else:
            # Truncated abstract for list view
            paper["abstract"] = self._truncate_abstract(str(row.get('abstract', '')))
        
        return paper
    
    def _clean_text(self, text):
        """Remove HTML tags and clean text"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', str(text))
        # Clean whitespace
        return ' '.join(text.split()).strip()
    
    def _truncate_abstract(self, abstract):
        """Truncate abstract to 3 sentences for list view"""
        if not abstract:
            return None
        
        clean_abstract = self._clean_text(abstract)
        sentences = re.split(r'(?<=[.!?]) +', clean_abstract)
        
        if len(sentences) <= 3:
            return clean_abstract
        
        return ' '.join(sentences[:3]) + "..."
    
    def _parse_authors(self, raw_auth):
        """Simple author parsing"""
        if not raw_auth:
            return None
        
        try:
            # Handle semicolon-separated format
            if isinstance(raw_auth, str) and ';' in raw_auth:
                authors = [name.strip() for name in raw_auth.split(';') if name.strip()]
                authors_str = ", ".join(authors)
            else:
                authors_str = str(raw_auth)
            
            # Limit length
            if len(authors_str) > 200:
                authors_str = authors_str[:197] + "..."
            
            return authors_str
            
        except Exception:
            return str(raw_auth) if raw_auth else None
    
    def test_connection(self):
        """Test database connection"""
        try:
            conn = psycopg2.connect(**self.config.get_psycopg2_params())
            conn.close()
            return True, "Database connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"