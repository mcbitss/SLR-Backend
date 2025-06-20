"""
Fixed Filter Service - Handles both single and double quotes
"""
import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

class FilterService:
    def get_filter_options(self, df):
        """Get available filter options from data"""
        if df.empty or 'output' not in df.columns:
            return {"study_types": [], "phases": [], "pharma_groups": []}
        
        study_types = set()
        phases = set()
        pharma_groups = set()
        
        for _, row in df.iterrows():
            output = str(row.get('output', ''))
            if output:
                study_types.update(self._extract_study_types(output))
                phases.update(self._extract_phases(output))
                pharma_groups.update(self._extract_pharma_groups(output))
        
        return {
            "study_types": sorted(list(study_types)),
            "phases": sorted(list(phases)),
            "pharma_groups": sorted(list(pharma_groups))
        }
    
    def apply_filters(self, df, filters):
        """Apply filters to papers"""
        if df.empty or not filters:
            return df
        
        filtered_indices = []
        
        for idx, row in df.iterrows():
            output = str(row.get('output', ''))
            if output and self._matches_filters(output, filters):
                filtered_indices.append(idx)
        
        result = df.iloc[filtered_indices].copy() if filtered_indices else pd.DataFrame()
        logger.info(f"Filtered {len(result)} papers from {len(df)} total")
        return result
    
    def _extract_study_types(self, output):
        """Extract study types from output - handles both single and double quotes"""
        types = []
        
        # Create patterns that match both single and double quotes
        patterns = [
            (r"['\"]code['\"]:\s*['\"]RCT['\"]", "Randomized Controlled Trial (RCT)"),
            (r"['\"]code['\"]:\s*['\"]CR['\"]", "Case Report (CR)"),
            (r"['\"]code['\"]:\s*['\"]CS['\"]", "Case Series (CS)"),
            (r"['\"]code['\"]:\s*['\"]XS['\"]", "Cross-Sectional Study (XS)"),
            (r"['\"]code['\"]:\s*['\"]CCS['\"]", "Case-Control Study (CCS)"),
            (r"['\"]code['\"]:\s*['\"]COH['\"]", "Cohort Study (COH)"),
            (r"['\"]code['\"]:\s*['\"]SR['\"]", "Systematic Review (SR)"),
            (r"['\"]code['\"]:\s*['\"]MA['\"]", "Meta-Analysis (MA)")
        ]
        
        for pattern, study_type in patterns:
            if re.search(pattern, output):
                types.append(study_type)
        
        return types
    
    def _extract_phases(self, output):
        """Extract phases from output - handles both single and double quotes"""
        phases = []
        
        patterns = [
            (r"['\"]code['\"]:\s*['\"]P1['\"]", "Phase I (P1)"),
            (r"['\"]code['\"]:\s*['\"]P2['\"]", "Phase II (P2)"),
            (r"['\"]code['\"]:\s*['\"]P3['\"]", "Phase III (P3)"),
            (r"['\"]code['\"]:\s*['\"]P4['\"]", "Phase IV (P4)")
        ]
        
        for pattern, phase in patterns:
            if re.search(pattern, output):
                phases.append(phase)
        
        return phases
    
    def _extract_pharma_groups(self, output):
        """Extract pharma groups from output - handles both single and double quotes"""
        groups = []
        
        patterns = [
            (r"['\"]group['\"]:\s*['\"]Medical Affairs['\"]", "Medical Affairs"),
            (r"['\"]group['\"]:\s*['\"]Commercial/Market Access['\"]", "Commercial/Market Access"),
            (r"['\"]group['\"]:\s*['\"]Pharmacovigilance['\"]", "Pharmacovigilance"),
            (r"['\"]group['\"]:\s*['\"]Clinical Development / R&D['\"]", "Clinical Development / R&D"),
            (r"['\"]group['\"]:\s*['\"]Regulatory Affairs['\"]", "Regulatory Affairs"),
            (r"['\"]group['\"]:\s*['\"]HEOR \(Health Economics\)['\"]", "HEOR (Health Economics)")
        ]
        
        for pattern, group in patterns:
            if re.search(pattern, output):
                groups.append(group)
        
        return groups
    
    def _matches_filters(self, output, filters):
        """Check if output matches all filters"""
        # Check study types
        if filters.get('study_types'):
            if not self._matches_study_types(output, filters['study_types']):
                return False
        
        # Check phases
        if filters.get('phases'):
            if not self._matches_phases(output, filters['phases']):
                return False
        
        # Check pharma groups
        if filters.get('pharma_groups'):
            if not self._matches_pharma_groups(output, filters['pharma_groups']):
                return False
        
        return True
    
    def _matches_study_types(self, output, study_types):
        """Check study type matches using regex"""
        for study_type in study_types:
            if 'RCT' in study_type and re.search(r"['\"]code['\"]:\s*['\"]RCT['\"]", output):
                return True
            if 'Case Report' in study_type and re.search(r"['\"]code['\"]:\s*['\"]CR['\"]", output):
                return True
            if 'Case Series' in study_type and re.search(r"['\"]code['\"]:\s*['\"]CS['\"]", output):
                return True
            if 'Cross-Sectional' in study_type and re.search(r"['\"]code['\"]:\s*['\"]XS['\"]", output):
                return True
            if 'Case-Control' in study_type and re.search(r"['\"]code['\"]:\s*['\"]CCS['\"]", output):
                return True
            if 'Cohort' in study_type and re.search(r"['\"]code['\"]:\s*['\"]COH['\"]", output):
                return True
            if 'Systematic Review' in study_type and re.search(r"['\"]code['\"]:\s*['\"]SR['\"]", output):
                return True
            if 'Meta-Analysis' in study_type and re.search(r"['\"]code['\"]:\s*['\"]MA['\"]", output):
                return True
        return False
    
    def _matches_phases(self, output, phases):
        """Check phase matches using regex"""
        for phase in phases:
            if 'Phase I' in phase and re.search(r"['\"]code['\"]:\s*['\"]P1['\"]", output):
                return True
            if 'Phase II' in phase and re.search(r"['\"]code['\"]:\s*['\"]P2['\"]", output):
                return True
            if 'Phase III' in phase and re.search(r"['\"]code['\"]:\s*['\"]P3['\"]", output):
                return True
            if 'Phase IV' in phase and re.search(r"['\"]code['\"]:\s*['\"]P4['\"]", output):
                return True
        return False
    
    def _matches_pharma_groups(self, output, pharma_groups):
        """Check pharma group matches using regex"""
        for group in pharma_groups:
            pattern = f"['\"]group['\"]:\s*['\"]" + re.escape(group) + "['\"]"
            if re.search(pattern, output):
                return True
        return False