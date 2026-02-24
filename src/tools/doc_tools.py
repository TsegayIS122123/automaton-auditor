"""PDF forensic tools with RAG-lite architecture"""

import pypdf
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions
import hashlib

class DocAnalyst:
    """PDF detective with RAG-lite for targeted queries"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.chunks = []
        self.chroma_client = None
        self.collection = None
        
    def extract_text(self) -> str:
        """Extract all text from PDF"""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")
        
        reader = pypdf.PdfReader(self.pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
        """Split text into overlapping chunks (RAG-lite)"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "start_idx": i,
                "chunk_id": hashlib.md5(chunk_text.encode()).hexdigest()[:8]
            })
            
            if i + chunk_size >= len(words):
                break
        
        self.chunks = chunks
        return chunks
    
    def setup_vector_store(self):
        """Initialize ChromaDB for semantic search"""
        self.chroma_client = chromadb.Client()
        
        # Use sentence-transformers for embeddings
        embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection
        collection_name = "pdf_chunks"
        try:
            self.chroma_client.delete_collection(collection_name)
        except:
            pass
            
        self.collection = self.chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_func
        )
        
        # Add chunks to vector store
        if self.chunks:
            self.collection.add(
                documents=[c["text"] for c in self.chunks],
                metadatas=[{"chunk_id": c["chunk_id"]} for c in self.chunks],
                ids=[c["chunk_id"] for c in self.chunks]
            )
    
    def query_concept(self, concept: str, n_results: int = 3) -> List[Dict]:
        """Query PDF for specific concept (RAG-lite)"""
        if not self.collection:
            self.extract_text()
            self.chunk_text(self.extract_text())
            self.setup_vector_store()
        
        results = self.collection.query(
            query_texts=[concept],
            n_results=n_results
        )
        
        matches = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                matches.append({
                    "text": doc,
                    "relevance": results['distances'][0][i] if results['distances'] else 0,
                    "chunk_id": results['ids'][0][i] if results['ids'] else None
                })
        
        return matches
    
    def extract_file_paths(self) -> List[str]:
        """Extract file paths mentioned in PDF"""
        text = self.extract_text()
        import re
        
        # Look for file paths (src/...py, tests/...py, etc.)
        patterns = [
            r'src/[a-zA-Z0-9_/]+\.py',
            r'tests/[a-zA-Z0-9_/]+\.py',
            r'[a-zA-Z0-9_]+\.py',
            r'[a-zA-Z0-9_/]+\.md'
        ]
        
        paths = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            paths.extend(matches)
        
        return list(set(paths))  # Remove duplicates
    
    def check_concept_depth(self, concept: str) -> Dict:
        """Check if concept is explained deeply or just keyword-dropped"""
        matches = self.query_concept(concept, n_results=5)
        
        analysis = {
            "concept": concept,
            "mentioned": len(matches) > 0,
            "depth": "none",
            "explanations": []
        }
        
        if matches:
            # Check if explanation is substantial (>50 words)
            for match in matches:
                word_count = len(match["text"].split())
                if word_count > 50:
                    analysis["depth"] = "deep"
                    analysis["explanations"].append(match["text"][:200] + "...")
                elif word_count > 20:
                    if analysis["depth"] != "deep":
                        analysis["depth"] = "moderate"
                    analysis["explanations"].append(match["text"][:200] + "...")
            
            if not analysis["explanations"]:
                analysis["depth"] = "superficial"
                analysis["explanations"] = [m["text"][:100] for m in matches[:2]]
        
        return analysis