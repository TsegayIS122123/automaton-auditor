"""PDF forensic tools with RAG-lite approach - chunked querying"""

import pypdf
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
import re

class DocAnalyst:
    """PDF detective with chunked text extraction - RAG-lite approach"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.full_text = None
        self.chunks = []
        
    def extract_text(self) -> str:
        """Extract all text from PDF"""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")
        
        reader = pypdf.PdfReader(self.pdf_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
        
        self.full_text = text
        return text
    
    def chunk_text(self, text: str = None, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """Split text into overlapping chunks (RAG-lite approach)"""
        if text is None:
            if self.full_text is None:
                text = self.extract_text()
            else:
                text = self.full_text
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "start_idx": i,
                "end_idx": i + len(chunk_words),
                "chunk_id": hashlib.md5(chunk_text.encode()).hexdigest()[:8],
                "word_count": len(chunk_words)
            })
            
            if i + chunk_size >= len(words):
                break
        
        self.chunks = chunks
        return chunks
    
    def query_concept(self, concept: str, case_sensitive: bool = False) -> List[Dict]:
        """Simple text search for concepts (no vector DB needed for interim)"""
        if not self.chunks:
            self.extract_text()
            self.chunk_text()
        
        concept_lower = concept.lower() if not case_sensitive else concept
        matches = []
        
        for chunk in self.chunks:
            chunk_text = chunk["text"]
            search_text = chunk_text.lower() if not case_sensitive else chunk_text
            
            if concept_lower in search_text:
                # Get surrounding context
                matches.append({
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk_text,
                    "word_count": chunk["word_count"],
                    "relevance": "exact_match"
                })
        
        return matches
    
    def extract_file_paths(self) -> List[str]:
        """Extract file paths mentioned in PDF"""
        if self.full_text is None:
            self.extract_text()
        
        # Look for file paths (src/...py, tests/...py, etc.)
        patterns = [
            r'src/[a-zA-Z0-9_/]+\.py',
            r'tests/[a-zA-Z0-9_/]+\.py',
            r'[a-zA-Z0-9_]+\.py',
            r'[a-zA-Z0-9_/]+\.md',
            r'\./[a-zA-Z0-9_/]+\.py'
        ]
        
        paths = []
        for pattern in patterns:
            matches = re.findall(pattern, self.full_text)
            paths.extend(matches)
        
        return list(set(paths))  # Remove duplicates
    
    def check_concept_depth(self, concept: str) -> Dict[str, Any]:
        """Check if concept is explained deeply or just keyword-dropped"""
        matches = self.query_concept(concept)
        
        analysis = {
            "concept": concept,
            "mentioned": len(matches) > 0,
            "depth": "none",
            "explanations": []
        }
        
        if matches:
            # Check if explanation is substantial (>50 words)
            for match in matches[:3]:  # Top 3 matches
                if match["word_count"] > 50:
                    analysis["depth"] = "deep"
                    analysis["explanations"].append(match["text"][:200] + "...")
                elif match["word_count"] > 20:
                    if analysis["depth"] != "deep":
                        analysis["depth"] = "moderate"
                    analysis["explanations"].append(match["text"][:200] + "...")
            
            if not analysis["explanations"]:
                analysis["depth"] = "superficial"
                analysis["explanations"] = [m["text"][:100] for m in matches[:2]]
        
        return analysis