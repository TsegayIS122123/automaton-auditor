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
        """Extract commit history for forensic analysis with progression pattern detection"""
        try:
            repo = git.Repo(self.repo_path)
            commits = list(repo.iter_commits())
            
            history = {
                "total_commits": len(commits),
                "commits": [],
                "progression_pattern": "unknown",  # NEW: setup_to_tools_to_graph, bulk_upload, mixed
                "has_progression": False,
                "first_commit": None,
                "last_commit": None,
                "timestamps": []  # NEW: store timestamps for analysis
            }
            
            # Analyze commits (up to 20 for better pattern detection)
            for i, commit in enumerate(reversed(commits[:20])):
                commit_data = {
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "timestamp": datetime.fromtimestamp(commit.committed_date).isoformat(),
                    "timestamp_epoch": commit.committed_date,  # NEW: for time analysis
                    "files_changed": len(commit.stats.files)
                }
                history["commits"].append(commit_data)
                history["timestamps"].append(commit.committed_date)
            
            # NEW: Detect progression pattern
            messages = " ".join([c["message"].lower() for c in history["commits"]])
            
            # Check for setup → tools → graph progression
            setup_keywords = ["setup", "env", "init", "initial", "bootstrap"]
            tool_keywords = ["tool", "repo_tools", "doc_tools", "ast", "parser", "git"]
            graph_keywords = ["graph", "stategraph", "orchestration", "node", "edge", "parallel"]
            
            has_setup = any(kw in messages for kw in setup_keywords)
            has_tools = any(kw in messages for kw in tool_keywords)
            has_graph = any(kw in messages for kw in graph_keywords)
            
            if has_setup and has_tools and has_graph:
                history["progression_pattern"] = "setup_to_tools_to_graph"
                history["has_progression"] = True
            elif len(commits) < 3:
                history["progression_pattern"] = "bulk_upload"
            else:
                history["progression_pattern"] = "mixed"
            
            # NEW: Check timestamp clustering (bulk upload detection)
            if len(history["timestamps"]) > 1:
                time_diffs = [history["timestamps"][i+1] - history["timestamps"][i] 
                            for i in range(len(history["timestamps"])-1)]
                avg_diff = sum(time_diffs) / len(time_diffs)
                
                # If average time between commits < 5 minutes, likely bulk upload
                if avg_diff < 300:  # 5 minutes in seconds
                    history["bulk_upload_detected"] = True
                else:
                    history["bulk_upload_detected"] = False
            
            if commits:
                history["first_commit"] = commits[-1].hexsha[:8]
                history["last_commit"] = commits[0].hexsha[:8]
                
            return history
        except Exception as e:
            return {"error": str(e), "total_commits": 0, "progression_pattern": "error"}
    
    def analyze_graph_structure(self) -> Dict[str, Any]:
        """AST parsing to detect graph architecture - detects structural patterns, not just existence"""
        graph_file = self.repo_path / "src" / "graph.py"
        
        if not graph_file.exists():
            return {"exists": False, "error": "graph.py not found"}
        
        try:
            with open(graph_file) as f:
                content = f.read()
                tree = ast.parse(content)
            
            analysis = {
                "exists": True,
                "has_stategraph": False,
                "has_parallel": False,
                "has_fan_out": False,
                "has_fan_in": False,
                "has_reducers": False,  # NEW: check for operator.add/ior
                "add_edge_patterns": [],  # NEW: store actual edge patterns
                "nodes": [],
                "edges": [],
                "conditional_edges": [],  # NEW: detect conditional routing
                "state_reducers": []  # NEW: what reducers are used
            }
            
            for node in ast.walk(tree):
                # Look for StateGraph instantiation
                if isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == "StateGraph":
                    analysis["has_stategraph"] = True
                
                # Look for add_edge calls with pattern detection
                if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == "add_edge":
                    edge_pattern = ast.unparse(node)  # NEW: capture full pattern
                    analysis["add_edge_patterns"].append(edge_pattern)
                    analysis["edges"].append("add_edge")
                    
                    # Detect fan-out: multiple edges from START
                    if len(node.args) >= 2:
                        first_arg = node.args[0]
                        if isinstance(first_arg, ast.Name) and first_arg.id == "START":
                            analysis["has_fan_out"] = True
                
                # NEW: Look for add_conditional_edges
                if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == "add_conditional_edges":
                    analysis["conditional_edges"].append(ast.unparse(node))
                
                # NEW: Detect reducer usage in Annotated types
                if isinstance(node, ast.AnnAssign) and hasattr(node.annotation, 'slice'):
                    annotation_str = ast.unparse(node.annotation)
                    if 'Annotated' in annotation_str:
                        if 'operator.add' in annotation_str:
                            analysis["has_reducers"] = True
                            analysis["state_reducers"].append("operator.add")
                        if 'operator.ior' in annotation_str:
                            analysis["has_reducers"] = True
                            analysis["state_reducers"].append("operator.ior")
                
                # NEW: Detect node definitions
                if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == "add_node":
                    if len(node.args) >= 1:
                        node_name = ast.unparse(node.args[0]).strip('"\'')
                        analysis["nodes"].append(node_name)
            
            # Determine parallel execution based on multiple nodes
            if len(analysis["nodes"]) >= 3:
                analysis["has_parallel"] = True
            
            # Check for fan-in pattern (multiple edges to same target)
            edge_targets = []
            for pattern in analysis["add_edge_patterns"]:
                if "evidence_aggregator" in pattern:
                    edge_targets.append("aggregator")
            if edge_targets.count("aggregator") >= 2:
                analysis["has_fan_in"] = True
            
            return analysis
            
        except Exception as e:
            return {"exists": True, "error": str(e), "has_stategraph": False}
    
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
    def detect_state_reducers(self) -> Dict[str, Any]:
        """Specifically check for operator.add and operator.ior in state definitions"""
        state_file = self.repo_path / "src" / "state.py"
        
        if not state_file.exists():
            return {"has_reducers": False, "reducers_found": []}
        
        try:
            with open(state_file) as f:
                content = f.read()
                tree = ast.parse(content)
            
            result = {
                "has_reducers": False,
                "reducers_found": [],
                "evidence_class": False,
                "judicial_opinion_class": False,
                "agent_state": False
            }
            
            # Check for Evidence class
            if "class Evidence(BaseModel)" in content:
                result["evidence_class"] = True
            
            # Check for JudicialOpinion class
            if "class JudicialOpinion(BaseModel)" in content:
                result["judicial_opinion_class"] = True
            
            # Check for AgentState with reducers
            if "class AgentState(TypedDict)" in content or "AgentState = TypedDict" in content:
                result["agent_state"] = True
            
            # Look for Annotated with reducers
            for node in ast.walk(tree):
                if isinstance(node, ast.AnnAssign) and hasattr(node.annotation, 'slice'):
                    annotation_str = ast.unparse(node.annotation)
                    if 'Annotated' in annotation_str:
                        if 'operator.add' in annotation_str:
                            result["has_reducers"] = True
                            result["reducers_found"].append("operator.add")
                        if 'operator.ior' in annotation_str:
                            result["has_reducers"] = True
                            result["reducers_found"].append("operator.ior")
            
            return result
        except Exception as e:
            return {"has_reducers": False, "error": str(e)}