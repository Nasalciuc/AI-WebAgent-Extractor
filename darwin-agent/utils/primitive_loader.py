import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

class PrimitiveLoader:
    """Loads and manages agent primitives (prompts, instructions, memory)"""
    
    def __init__(self, primitives_dir: Optional[str] = None):
        if primitives_dir is None:
            self.primitives_dir = Path(__file__).parent.parent
        else:
            self.primitives_dir = Path(primitives_dir)
        
        self.modes_dir = self.primitives_dir / "modes"
        self.specs_dir = self.primitives_dir / "specs"
        self.docs_dir = self.primitives_dir / "docs"
        self.memory_file = self.primitives_dir / "agent_memory.json"
        self.instructions_file = self.primitives_dir / "agent_instructions.yaml"
    
    def load_mode(self, mode_name: str) -> Optional[str]:
        """Load a mode prompt from modes directory"""
        mode_file = self.modes_dir / f"{mode_name}.md"
        if mode_file.exists():
            return mode_file.read_text(encoding='utf-8')
        return None
    
    def load_workflow_prompt(self) -> str:
        """Load the main workflow prompt"""
        workflow_file = self.modes_dir / "workflow.md"
        if workflow_file.exists():
            return workflow_file.read_text(encoding='utf-8')
        return "# Darwin Agent Workflow\n\nExecuting agentic extraction workflow..."
    
    def load_memory(self) -> Dict[str, Any]:
        """Load persistent agent memory"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Return default memory structure
        return {
            "last_run": {},
            "patterns": [],
            "insights": [],
            "performance_history": []
        }
    
    def save_memory(self, memory: Dict[str, Any]):
        """Save agent memory to disk"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")
    
    def load_instructions(self) -> Dict[str, Any]:
        """Load agent instructions"""
        if self.instructions_file.exists():
            try:
                with open(self.instructions_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        
        # Return default instructions
        return {
            "general": {
                "mission": "Extract product data from Darwin.md efficiently and accurately",
                "principles": [
                    "Quality over quantity",
                    "Adaptive strategy based on results",
                    "Continuous learning from patterns"
                ]
            }
        }
    
    def load_spec(self, spec_name: str) -> Optional[Dict]:
        """Load a specification file"""
        spec_file = self.specs_dir / f"{spec_name}.yaml"
        if spec_file.exists():
            try:
                with open(spec_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception:
                pass
        return None
    
    def interpolate_template(self, template: str, context: Dict[str, Any]) -> str:
        """Simple template interpolation"""
        result = template
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result


class ModeManager:
    """Manages execution modes and transitions"""
    
    def __init__(self, primitive_loader: PrimitiveLoader):
        self.loader = primitive_loader
        self.modes = ["planner", "meta-controller", "executor", "judge"]
        self.current_mode = "planner"
        self.mode_history = []
    
    def get_next_mode(self, current_mode: str, context: Optional[Dict] = None) -> Optional[str]:
        """Determine the next mode based on current state"""
        try:
            current_index = self.modes.index(current_mode)
            if current_index < len(self.modes) - 1:
                return self.modes[current_index + 1]
        except ValueError:
            pass
        return None
    
    def transition_to(self, mode: str):
        """Transition to a specific mode"""
        if mode in self.modes:
            self.mode_history.append(self.current_mode)
            self.current_mode = mode
            return True
        return False
    
    def get_mode_context(self, mode: str) -> Dict[str, Any]:
        """Get context information for a specific mode"""
        mode_contexts = {
            "planner": {
                "purpose": "Analyze target and create extraction strategy",
                "inputs": ["target_products", "historical_data"],
                "outputs": ["extraction_plan", "url_list", "strategy"]
            },
            "meta-controller": {
                "purpose": "Evaluate and adjust plans based on constraints",
                "inputs": ["extraction_plan", "resource_constraints"],
                "outputs": ["adjusted_plan", "execution_parameters"]
            },
            "executor": {
                "purpose": "Execute the extraction plan",
                "inputs": ["adjusted_plan", "url_list"],
                "outputs": ["extracted_data", "performance_metrics"]
            },
            "judge": {
                "purpose": "Evaluate results and provide recommendations",
                "inputs": ["extracted_data", "performance_metrics"],
                "outputs": ["quality_assessment", "recommendations"]
            }
        }
        return mode_contexts.get(mode, {})