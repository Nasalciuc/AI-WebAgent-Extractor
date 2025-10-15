#!/usr/bin/env python3
"""
Darwin Agent - Main Orchestrator
Agentic framework for Darwin.md product extraction following GitHub's Agentic Primitives
"""

import os
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project paths for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "config"))

# Import existing Darwin scraper components
try:
    from darwin_scraper_complete import DarwinProductScraper
    from env_config import get_environment_config, validate_environment
    SCRAPER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import scraper components: {e}")
    SCRAPER_AVAILABLE = False

# Import utility for loading primitives
from utils.primitive_loader import PrimitiveLoader, ModeManager

class DarwinAgent:
    """Main orchestrator implementing agentic primitives for Darwin.md extraction"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.primitive_loader = PrimitiveLoader()
        self.mode_manager = ModeManager(self.primitive_loader)
        
        # Setup logging first
        self._setup_logging()
        
        # Load agent primitives
        self.memory = self.primitive_loader.load_memory()
        self.instructions = self.primitive_loader.load_instructions()
        self.current_mode = "planner"
        self.workflow_state = {}
        
        # Initialize core components if available
        if SCRAPER_AVAILABLE:
            env_config = get_environment_config()
            validation = validate_environment()
            
            if validation['valid']:
                provider, api_key = env_config.select_ai_provider()
                self.scraper = DarwinProductScraper(
                    openai_api_key=api_key if provider == "openai" else None,
                    gemini_api_key=api_key if provider == "gemini" else None,
                    ai_provider=provider
                )
                self.logger.info(f"Initialized with AI provider: {provider}")
            else:
                self.scraper = None
                self.logger.warning("No valid AI configuration found")
        else:
            self.scraper = None
    
    def _setup_logging(self):
        """Configure logging for the agent"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - Darwin Agent - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def execute_workflow(self, target_products: int = 100) -> Dict[str, Any]:
        """Execute the main scraping workflow using agentic primitives"""
        self.logger.info(f"Starting Darwin Agent workflow - Target: {target_products} products")
        
        # Load and interpolate workflow prompt
        workflow_template = self.primitive_loader.load_workflow_prompt()
        workflow_context = {
            "target_products": target_products,
            "current_mode": self.current_mode,
            "previous_results": self.memory.get("last_run", {})
        }
        
        workflow_prompt = self.primitive_loader.interpolate_template(
            workflow_template, workflow_context
        )
        
        result = {
            "status": "initiated",
            "timestamp": datetime.now().isoformat(),
            "target_products": target_products,
            "workflow_prompt": workflow_prompt[:500] + "..." if len(workflow_prompt) > 500 else workflow_prompt
        }
        
        if not self.scraper:
            result.update({
                "status": "failed", 
                "error": "Scraper not available - check configuration"
            })
            return result
        
        try:
            # Phase 1: Planning mode
            self.logger.info("Entering Planning mode")
            self.current_mode = "planner"
            planning_result = self._execute_mode("planner", {"target": target_products})
            
            # Phase 2: Meta-controller decision
            self.logger.info("Meta-controller evaluation")
            meta_result = self._execute_mode("meta-controller", planning_result)
            
            # Phase 3: Execution mode  
            self.logger.info("Entering Execution mode")
            self.current_mode = "executor"
            execution_result = self._execute_mode("executor", meta_result or planning_result)
            
            # Phase 4: Judge mode
            self.logger.info("Entering Judge mode")
            self.current_mode = "judge"
            judgment_result = self._execute_mode("judge", execution_result)
            
            result.update({
                "status": "completed",
                "phases": {
                    "planning": planning_result,
                    "meta_control": meta_result,
                    "execution": execution_result,
                    "judgment": judgment_result
                }
            })
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            result.update({"status": "failed", "error": str(e)})
        
        # Update persistent memory
        self._update_memory(result)
        
        return result
    
    def _execute_mode(self, mode_name: str, context: Dict) -> Dict[str, Any]:
        """Execute a specific agent mode"""
        mode_prompt = self.primitive_loader.load_mode(mode_name)
        
        if not mode_prompt:
            raise FileNotFoundError(f"Mode prompt not found: {mode_name}")
        
        # Interpolate mode template with context
        interpolated_prompt = self.primitive_loader.interpolate_template(
            mode_prompt, context
        )
        
        self.logger.info(f"Executing mode: {mode_name}")
        
        # Mode-specific logic
        if mode_name == "planner":
            return self._plan_extraction(context)
        elif mode_name == "meta-controller":
            return self._meta_control(context)
        elif mode_name == "executor":
            return self._execute_extraction(context)
        elif mode_name == "judge":
            return self._judge_results(context)
        else:
            raise ValueError(f"Unknown mode: {mode_name}")
    
    def _plan_extraction(self, context: Dict) -> Dict[str, Any]:
        """Planning phase - discover and categorize URLs"""
        self.logger.info("Planning extraction strategy")
        
        target = context.get("target", 100)
        
        # Discover all product URLs using existing scraper
        try:
            discovery_result = self.scraper.discover_all_products()
            
            if not discovery_result.get("success"):
                raise Exception("Failed to discover product URLs")
            
            all_urls = discovery_result.get("product_urls", [])
            selected_urls = all_urls[:target]
            
            # Analyze URL patterns for strategic planning
            url_analysis = self._analyze_url_patterns(selected_urls)
            
            return {
                "phase": "planning",
                "status": "completed",
                "total_discovered": len(all_urls),
                "selected_urls": selected_urls,
                "url_analysis": url_analysis,
                "strategy": "batch_parallel",
                "estimated_time_minutes": len(selected_urls) * 2 / 60,  # 2 seconds per product
                "recommended_workers": min(10, max(5, len(selected_urls) // 20))
            }
            
        except Exception as e:
            return {
                "phase": "planning",
                "status": "failed", 
                "error": str(e)
            }
    
    def _meta_control(self, context: Dict) -> Dict[str, Any]:
        """Meta-controller - evaluate plan and make adjustments"""
        self.logger.info("Meta-controller evaluation")
        
        if context.get("status") != "completed":
            return {
                "phase": "meta_control",
                "status": "planning_failed",
                "decision": "abort",
                "reason": "Planning phase failed"
            }
        
        # Evaluate plan quality
        total_urls = len(context.get("selected_urls", []))
        estimated_time = context.get("estimated_time_minutes", 0)
        
        # Make strategic decisions
        decisions = []
        adjustments = {}
        
        if total_urls > 500:
            decisions.append("Large batch detected - recommend splitting")
            adjustments["batch_size"] = 100
        
        if estimated_time > 30:  # More than 30 minutes
            decisions.append("Long execution time - reduce parallelism for stability")
            adjustments["workers"] = max(5, context.get("recommended_workers", 10) - 2)
        
        return {
            "phase": "meta_control",
            "status": "completed",
            "decisions": decisions,
            "adjustments": adjustments,
            "approved": True,
            "confidence": 0.85
        }
    
    def _execute_extraction(self, context: Dict) -> Dict[str, Any]:
        """Execution phase - extract product data"""
        self.logger.info("Executing product extraction")
        
        # Get URLs from planning phase
        planning_data = context
        if "selected_urls" not in planning_data:
            return {"phase": "execution", "status": "failed", "error": "No URLs to extract"}
        
        urls = planning_data["selected_urls"]
        
        # Apply meta-controller adjustments
        adjustments = context.get("adjustments", {})
        workers = adjustments.get("workers", 10)
        batch_size = adjustments.get("batch_size", len(urls))
        
        try:
            # Run batch extraction using existing scraper
            extraction_result = self.scraper.run_batch_local_extraction(
                urls=urls[:batch_size],
                workers=workers,
                max_urls=batch_size,
                output_prefix="darwin_agent_batch"
            )
            
            return {
                "phase": "execution",
                "status": "completed",
                "processed": extraction_result.get("processed", 0),
                "successful": extraction_result.get("successful", 0),
                "failed": extraction_result.get("failed", 0),
                "success_rate": extraction_result.get("success_rate", 0),
                "workers_used": workers,
                "output_files": {
                    "json": extraction_result.get("final_json"),
                    "csv": extraction_result.get("final_csv")
                }
            }
            
        except Exception as e:
            return {
                "phase": "execution",
                "status": "failed",
                "error": str(e)
            }
    
    def _judge_results(self, context: Dict) -> Dict[str, Any]:
        """Judgment phase - validate and analyze results"""
        self.logger.info("Judging extraction results")
        
        if context.get("status") != "completed":
            return {
                "phase": "judgment",
                "verdict": "FAIL",
                "reason": "Execution phase failed"
            }
        
        # Analyze extraction metrics
        processed = context.get("processed", 0)
        successful = context.get("successful", 0)
        success_rate = context.get("success_rate", 0)
        
        # Load and analyze extracted data if available
        json_file = context.get("output_files", {}).get("json")
        quality_analysis = {}
        
        if json_file and os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                quality_analysis = self._analyze_data_quality(products)
            except Exception as e:
                self.logger.error(f"Could not analyze output file: {e}")
        
        # Make judgment
        verdict = "PASS"
        recommendations = []
        
        if success_rate < 0.7:
            verdict = "CONDITIONAL"
            recommendations.append("Low success rate - consider strategy adjustment")
        
        if success_rate < 0.5:
            verdict = "FAIL"
            recommendations.append("Very low success rate - requires re-extraction")
        
        if quality_analysis.get("completeness", 0) < 0.8:
            recommendations.append("Data completeness below target - improve field extraction")
        
        return {
            "phase": "judgment",
            "verdict": verdict,
            "overall_score": (success_rate * 0.7 + quality_analysis.get("completeness", 0.5) * 0.3),
            "metrics": {
                "processed": processed,
                "successful": successful,
                "success_rate": success_rate,
                "data_quality": quality_analysis
            },
            "recommendations": recommendations,
            "approved_for_use": verdict in ["PASS", "CONDITIONAL"]
        }
    
    def _analyze_url_patterns(self, urls: List[str]) -> Dict[str, Any]:
        """Analyze URL patterns for strategic insights"""
        categories = {}
        patterns = {}
        
        for url in urls:
            # Extract category from URL
            path_parts = url.replace("https://darwin.md/", "").split("/")
            if path_parts:
                category = path_parts[0]
                categories[category] = categories.get(category, 0) + 1
        
        return {
            "category_distribution": categories,
            "total_categories": len(categories),
            "most_common_category": max(categories.items(), key=lambda x: x[1]) if categories else None
        }
    
    def _analyze_data_quality(self, products: List[Dict]) -> Dict[str, Any]:
        """Analyze the quality of extracted products"""
        if not products:
            return {"completeness": 0, "issues": ["No products extracted"]}
        
        required_fields = ["name", "price", "category"]
        optional_fields = ["description", "image_url", "brand"]
        
        complete_products = 0
        field_completeness = {}
        issues = []
        
        for field in required_fields + optional_fields:
            field_completeness[field] = 0
        
        for product in products:
            is_complete = True
            for field in required_fields:
                if product.get(field):
                    field_completeness[field] += 1
                else:
                    is_complete = False
            
            for field in optional_fields:
                if product.get(field):
                    field_completeness[field] += 1
            
            if is_complete:
                complete_products += 1
        
        # Calculate percentages
        total = len(products)
        for field in field_completeness:
            field_completeness[field] = (field_completeness[field] / total) * 100
        
        completeness = (complete_products / total) * 100
        
        # Identify issues
        if completeness < 80:
            issues.append(f"Only {completeness:.1f}% of products have all required fields")
        
        for field in required_fields:
            if field_completeness[field] < 70:
                issues.append(f"Field '{field}' missing in {100-field_completeness[field]:.1f}% of products")
        
        return {
            "completeness": completeness / 100,  # Return as ratio
            "field_completeness": field_completeness,
            "complete_products": complete_products,
            "total_products": total,
            "issues": issues
        }
    
    def _update_memory(self, result: Dict):
        """Update persistent agent memory"""
        # Update memory with latest execution results
        memory_update = {
            "last_run": {
                "timestamp": result.get("timestamp"),
                "status": result.get("status"),
                "target_products": result.get("target_products"),
                "verdict": result.get("phases", {}).get("judgment", {}).get("verdict")
            },
            "patterns": self.memory.get("patterns", []),
            "insights": self.memory.get("insights", [])
        }
        
        # Add new insights based on results
        if result.get("status") == "completed":
            phases = result.get("phases", {})
            execution = phases.get("execution", {})
            
            if execution.get("success_rate", 0) > 0.9:
                memory_update["insights"].append(f"High success rate achieved: {execution.get('success_rate', 0):.1%}")
            
            planning = phases.get("planning", {})
            if planning.get("url_analysis", {}).get("most_common_category"):
                category, count = planning["url_analysis"]["most_common_category"]
                memory_update["patterns"].append(f"Category '{category}' most common with {count} products")
        
        # Save updated memory
        self.primitive_loader.save_memory(memory_update)
        self.memory = memory_update


def main():
    """Main entry point for Darwin Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Darwin Agent - Agentic Web Scraping")
    parser.add_argument("--target", type=int, default=100, help="Target number of products to extract")
    parser.add_argument("--mode", type=str, choices=["workflow", "plan", "execute", "judge"], 
                        default="workflow", help="Execution mode")
    parser.add_argument("--config", type=str, help="Configuration file path")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize agent
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    agent = DarwinAgent(config)
    
    # Execute based on mode
    if args.mode == "workflow":
        result = agent.execute_workflow(target_products=args.target)
    else:
        # Individual mode execution
        context = {"target": args.target}
        result = agent._execute_mode(args.mode, context)
    
    # Output results
    print("=" * 60)
    print("DARWIN AGENT EXECUTION RESULTS")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"darwin_agent_results_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {results_file}")
    
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    exit(main())