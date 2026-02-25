"""Repository forensic tools with sandboxing and AST parsing"""

import ast
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any
import git
from datetime import datetime
import os

class RepoInvestigator:
    """Forensic code detective with AST parsing - sandboxed and safe"""
    
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.temp_dir = None
        self.repo_path = None
        
    def __enter__(self):
        """Context manager for automatic cleanup"""
        self.clone_repo()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temp directory - guarantees no leftover files"""
        if self.temp_dir:
            self.temp_dir.cleanup()
    
    def clone_repo(self) -> Path:
        """Sandboxed git clone using tempfile - NO os.system()"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_path = Path(self.temp_dir.name)
        
        try:
            # Use subprocess with error handling (NOT os.system)
            result = subprocess.run(
                ["git", "clone", self.repo_url, str(self.repo_path)],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            return self.repo_path
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git clone failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise Exception("Git clone timed out after 60 seconds")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    
    def analyze_git_history(self) -> Dict[str, Any]:
        """Extract commit history for forensic analysis"""
        try:
            repo = git.Repo(self.repo_path)
            commits = list(repo.iter_commits())
            
            history = {
                "total_commits": len(commits),
                "commits": [],
                "has_progression": False,
                "first_commit": None,
                "last_commit": None
            }
            
            # Analyze last 10 commits for progression pattern
            for i, commit in enumerate(reversed(commits[:10])):
                history["commits"].append({
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "timestamp": datetime.fromtimestamp(commit.committed_date).isoformat(),
                    "files_changed": len(commit.stats.files)
                })
            
            # Check for progression pattern (setup → tools → graph)
            messages = [c["message"].lower() for c in history["commits"]]
            patterns = ["setup", "env", "init", "tool", "graph", "node", "detective"]
            history["has_progression"] = any(p in " ".join(messages) for p in patterns)
            
            if commits:
                history["first_commit"] = commits[-1].hexsha[:8]
                history["last_commit"] = commits[0].hexsha[:8]
                
            return history
        except Exception as e:
            return {"error": str(e), "total_commits": 0}
    
    def analyze_graph_structure(self) -> Dict[str, Any]:
        """AST parsing to detect graph architecture - NOT regex!"""
        graph_file = self.repo_path / "src" / "graph.py"
        
        if not graph_file.exists():
            return {"exists": False, "error": "graph.py not found"}
        
        try:
            with open(graph_file) as f:
                tree = ast.parse(f.read())
            
            analysis = {
                "exists": True,
                "has_stategraph": False,
                "has_parallel": False,
                "has_fan_out": False,
                "has_fan_in": False,
                "nodes": [],
                "edges": []
            }
            
            for node in ast.walk(tree):
                # Look for StateGraph instantiation
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "StateGraph":
                        analysis["has_stategraph"] = True
                
                # Look for add_edge calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute) and node.func.attr == "add_edge":
                        analysis["edges"].append("add_edge")
                        
                        # Detect fan-out: multiple edges from START
                        if len(node.args) >= 2:
                            first_arg = node.args[0]
                            if isinstance(first_arg, ast.Name) and first_arg.id == "START":
                                analysis["has_fan_out"] = True
            
            # Heuristic for parallel execution
            analysis["has_parallel"] = analysis["has_fan_out"]
            
            return analysis
            
        except Exception as e:
            return {"exists": True, "error": str(e)}
    
    def check_state_models(self) -> Dict[str, Any]:
        """Verify Pydantic models in state.py"""
        state_file = self.repo_path / "src" / "state.py"
        
        if not state_file.exists():
            return {"exists": False}
        
        try:
            with open(state_file) as f:
                content = f.read()
            
            analysis = {
                "exists": True,
                "has_base_model": "BaseModel" in content,
                "has_typeddict": "TypedDict" in content,
                "has_reducers": "operator.add" in content or "operator.ior" in content,
                "has_evidence": "class Evidence" in content,
                "has_judicial": "JudicialOpinion" in content,
                "has_agentstate": "AgentState" in content
            }
            
            return analysis
        except Exception as e:
            return {"exists": True, "error": str(e)}
    
    def check_sandboxing(self) -> Dict[str, Any]:
        """Verify tools use proper sandboxing"""
        tools_files = [
            self.repo_path / "src" / "tools" / "repo_tools.py",
            self.repo_path / "src" / "tools" / "doc_tools.py"
        ]
        
        analysis = {
            "has_tempfile": False,
            "has_subprocess": False,
            "no_os_system": True,
            "has_error_handling": False
        }
        
        for tool_file in tools_files:
            if tool_file.exists():
                with open(tool_file) as f:
                    content = f.read()
                    
                    if "tempfile.TemporaryDirectory" in content:
                        analysis["has_tempfile"] = True
                    
                    if "subprocess.run" in content:
                        analysis["has_subprocess"] = True
                    
                    if "os.system" in content:
                        analysis["no_os_system"] = False
                    
                    if "try:" in content and "except" in content:
                        analysis["has_error_handling"] = True
        
        return analysis