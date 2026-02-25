"""Dynamically load the rubric.json constitution"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class RubricLoader:
    """Load and serve the constitution (rubric.json) - dynamic loading"""
    
    def __init__(self, rubric_path: str = "rubric.json"):
        self.rubric_path = Path(rubric_path)
        self.rubric = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load rubric from JSON file"""
        if not self.rubric_path.exists():
            raise FileNotFoundError(
                f"Rubric not found: {self.rubric_path}. "
                "Please ensure rubric.json is in the project root."
            )
        
        with open(self.rubric_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_dimensions(self) -> List[Dict]:
        """Get all rubric dimensions"""
        return self.rubric.get("dimensions", [])
    
    def get_dimension(self, dimension_id: str) -> Dict:
        """Get specific dimension by ID"""
        for dim in self.get_dimensions():
            if dim["id"] == dimension_id:
                return dim
        return {}
    
    def get_forensic_instruction(self, dimension_id: str) -> str:
        """Get forensic instruction for a detective"""
        dim = self.get_dimension(dimension_id)
        return dim.get("forensic_instruction", "")
    
    def get_synthesis_rules(self) -> Dict:
        """Get synthesis rules for Chief Justice (for final)"""
        return self.rubric.get("synthesis_rules", {})
    
    def get_dimensions_by_artifact(self, artifact: str) -> List[Dict]:
        """Get dimensions targeting specific artifact (github_repo or pdf_report)"""
        return [
            dim for dim in self.get_dimensions()
            if dim.get("target_artifact") == artifact
        ]
    
    def get_dimension_names(self) -> List[str]:
        """Get list of dimension names"""
        return [dim["name"] for dim in self.get_dimensions()]
    
    def get_rubric_metadata(self) -> Dict:
        """Get rubric metadata"""
        return self.rubric.get("rubric_metadata", {})