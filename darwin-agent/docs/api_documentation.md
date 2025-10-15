# Darwin Agent - API Documentation

## Main API Classes

### DarwinAgent

The main orchestrator class that implements the agentic framework for Darwin.md product extraction.

#### Constructor

```python
DarwinAgent(config: Optional[Dict] = None)
```

**Parameters:**
- `config` (Optional[Dict]): Configuration dictionary for agent behavior

**Example:**
```python
# Basic initialization
agent = DarwinAgent()

# With custom configuration
config = {"workers": 8, "timeout": 30}
agent = DarwinAgent(config)
```

#### Primary Methods

##### execute_workflow()

```python
execute_workflow(target_products: int = 100) -> Dict[str, Any]
```

Executes the complete four-phase agentic workflow.

**Parameters:**
- `target_products` (int): Number of products to extract (default: 100)

**Returns:**
- `Dict[str, Any]`: Comprehensive execution results

**Response Structure:**
```json
{
  "status": "completed|failed|initiated",
  "timestamp": "2024-01-15T10:30:00",
  "target_products": 100,
  "phases": {
    "planning": {...},
    "meta_control": {...},
    "execution": {...},
    "judgment": {...}
  }
}
```

**Example:**
```python
agent = DarwinAgent()
result = agent.execute_workflow(target_products=50)

if result["status"] == "completed":
    print(f"Successfully extracted {result['phases']['execution']['successful']} products")
else:
    print(f"Extraction failed: {result.get('error', 'Unknown error')}")
```

##### Individual Mode Execution

```python
_execute_mode(mode_name: str, context: Dict) -> Dict[str, Any]
```

Executes a specific agent mode (internal method, primarily for testing).

**Parameters:**
- `mode_name` (str): Mode to execute ("planner", "meta-controller", "executor", "judge")
- `context` (Dict): Context data for the mode

**Returns:**
- `Dict[str, Any]`: Mode-specific execution results

### PrimitiveLoader

Manages loading and interpolation of agent primitives.

#### Constructor

```python
PrimitiveLoader(primitives_dir: Optional[str] = None)
```

**Parameters:**
- `primitives_dir` (Optional[str]): Directory containing agent primitives

#### Methods

##### load_mode()

```python
load_mode(mode_name: str) -> Optional[str]
```

Load a mode prompt from the modes directory.

**Parameters:**
- `mode_name` (str): Name of the mode to load

**Returns:**
- `Optional[str]`: Mode prompt content or None if not found

**Example:**
```python
loader = PrimitiveLoader()
planner_prompt = loader.load_mode("planner")
```

##### load_memory()

```python
load_memory() -> Dict[str, Any]
```

Load persistent agent memory from disk.

**Returns:**
- `Dict[str, Any]`: Memory structure with historical data

**Memory Structure:**
```json
{
  "last_run": {
    "timestamp": "2024-01-15T10:30:00",
    "status": "completed",
    "target_products": 100,
    "verdict": "PASS"
  },
  "patterns": ["Pattern 1", "Pattern 2"],
  "insights": ["Insight 1", "Insight 2"],
  "performance_history": [...]
}
```

##### save_memory()

```python
save_memory(memory: Dict[str, Any]) -> None
```

Save agent memory to disk for persistence.

**Parameters:**
- `memory` (Dict[str, Any]): Memory data to persist

##### interpolate_template()

```python
interpolate_template(template: str, context: Dict[str, Any]) -> str
```

Interpolate template placeholders with context values.

**Parameters:**
- `template` (str): Template string with {placeholder} markers
- `context` (Dict[str, Any]): Values to interpolate

**Returns:**
- `str`: Interpolated template

**Example:**
```python
template = "Extracting {target_products} products in {current_mode} mode"
context = {"target_products": 100, "current_mode": "planner"}
result = loader.interpolate_template(template, context)
# Result: "Extracting 100 products in planner mode"
```

### ModeManager

Manages execution modes and transitions.

#### Constructor

```python
ModeManager(primitive_loader: PrimitiveLoader)
```

#### Methods

##### get_next_mode()

```python
get_next_mode(current_mode: str, context: Optional[Dict] = None) -> Optional[str]
```

Determine the next mode in the workflow sequence.

**Parameters:**
- `current_mode` (str): Current execution mode
- `context` (Optional[Dict]): Additional context for decision making

**Returns:**
- `Optional[str]`: Next mode name or None if at end of sequence

##### transition_to()

```python
transition_to(mode: str) -> bool
```

Transition to a specific mode.

**Parameters:**
- `mode` (str): Target mode name

**Returns:**
- `bool`: True if transition successful, False otherwise

##### get_mode_context()

```python
get_mode_context(mode: str) -> Dict[str, Any]
```

Get context information for a specific mode.

**Parameters:**
- `mode` (str): Mode name

**Returns:**
- `Dict[str, Any]`: Mode context with purpose, inputs, and outputs

## Data Structures

### Execution Result Structure

#### Planning Phase Result

```json
{
  "phase": "planning",
  "status": "completed",
  "total_discovered": 1500,
  "selected_urls": ["url1", "url2", ...],
  "url_analysis": {
    "category_distribution": {
      "smartphones": 45,
      "laptops": 30,
      "accessories": 25
    },
    "total_categories": 3,
    "most_common_category": ["smartphones", 45]
  },
  "strategy": "batch_parallel",
  "estimated_time_minutes": 15.5,
  "recommended_workers": 6
}
```

#### Meta-Controller Result

```json
{
  "phase": "meta_control",
  "status": "completed",
  "decisions": [
    "Large batch detected - recommend splitting",
    "Long execution time - reduce parallelism for stability"
  ],
  "adjustments": {
    "batch_size": 100,
    "workers": 5
  },
  "approved": true,
  "confidence": 0.85
}
```

#### Execution Result

```json
{
  "phase": "execution",
  "status": "completed",
  "processed": 100,
  "successful": 87,
  "failed": 13,
  "success_rate": 0.87,
  "workers_used": 5,
  "output_files": {
    "json": "darwin_agent_batch_20240115_103000.json",
    "csv": "darwin_agent_batch_20240115_103000.csv"
  }
}
```

#### Judgment Result

```json
{
  "phase": "judgment",
  "verdict": "PASS",
  "overall_score": 0.85,
  "metrics": {
    "processed": 100,
    "successful": 87,
    "success_rate": 0.87,
    "data_quality": {
      "completeness": 0.92,
      "field_completeness": {
        "name": 98.5,
        "price": 95.2,
        "category": 100.0,
        "description": 78.3
      },
      "complete_products": 80,
      "total_products": 87,
      "issues": []
    }
  },
  "recommendations": [
    "Good performance - maintain current strategy",
    "Consider improving description extraction"
  ],
  "approved_for_use": true
}
```

### Product Data Structure

```json
{
  "name": "iPhone 13 Pro Max 256GB",
  "price": 15999.0,
  "category": "accesorii-smartphone",
  "description": "Latest iPhone with advanced camera system...",
  "image_url": "https://darwin.md/images/iphone13pro.jpg",
  "brand": "Apple",
  "specifications": {
    "storage": "256GB",
    "color": "Sierra Blue",
    "display": "6.7 inch"
  },
  "availability": "in_stock",
  "url": "https://darwin.md/accesorii-smartphone/iphone-13-pro-max-256gb"
}
```

## Command Line Interface

### Main Script Usage

```bash
python darwin_agent.py [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--target` | int | 100 | Number of products to extract |
| `--mode` | str | "workflow" | Execution mode (workflow/plan/execute/judge) |
| `--config` | str | None | Path to configuration file |
| `--verbose` | flag | False | Enable verbose logging |

**Examples:**

```bash
# Basic extraction
python darwin_agent.py --target 50

# Verbose mode with custom config
python darwin_agent.py --target 200 --verbose --config my_config.json

# Planning mode only
python darwin_agent.py --mode plan --target 100
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - execution completed successfully |
| 1 | Failure - execution failed or results unacceptable |

## Configuration API

### Environment Configuration

**Required Environment Variables:**
```bash
# At least one AI provider key required
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Configuration File Format

```json
{
  "workers": 8,
  "batch_size": 150,
  "timeout": 30,
  "quality_threshold": 0.85,
  "retry_attempts": 3,
  "rate_limit_delay": 1.0,
  "output_format": "both",
  "log_level": "INFO"
}
```

**Configuration Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `workers` | int | 5 | Number of concurrent extraction workers |
| `batch_size` | int | target_size | Maximum products per batch |
| `timeout` | int | 30 | Request timeout in seconds |
| `quality_threshold` | float | 0.75 | Minimum acceptable quality score |
| `retry_attempts` | int | 3 | Maximum retry attempts for failed requests |
| `rate_limit_delay` | float | 1.0 | Delay between requests in seconds |
| `output_format` | str | "both" | Output format ("json", "csv", "both") |
| `log_level` | str | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Error Handling API

### Exception Types

**Standard Exceptions:**
- `FileNotFoundError`: Mode prompt or configuration file not found
- `ValueError`: Invalid mode name or configuration value
- `Exception`: General extraction or processing errors

### Error Response Structure

```json
{
  "status": "failed",
  "error": "Detailed error message",
  "error_type": "network_error|parsing_error|configuration_error",
  "phase": "planning|meta_control|execution|judgment",
  "timestamp": "2024-01-15T10:30:00",
  "recovery_suggestions": [
    "Check network connection",
    "Verify configuration settings",
    "Retry with smaller batch size"
  ]
}
```

## Integration Examples

### Basic Integration

```python
from darwin_agent import DarwinAgent

# Initialize agent
agent = DarwinAgent()

# Execute extraction
result = agent.execute_workflow(target_products=100)

# Process results
if result["status"] == "completed":
    execution_data = result["phases"]["execution"]
    json_file = execution_data["output_files"]["json"]
    
    # Load extracted products
    import json
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"Extracted {len(products)} products")
    for product in products[:5]:  # Show first 5
        print(f"- {product['name']}: {product['price']} lei")
```

### Advanced Integration with Error Handling

```python
import logging
from darwin_agent import DarwinAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_products_with_retry(target: int, max_attempts: int = 3):
    """Extract products with automatic retry logic"""
    
    agent = DarwinAgent()
    
    for attempt in range(max_attempts):
        try:
            logger.info(f"Extraction attempt {attempt + 1}/{max_attempts}")
            result = agent.execute_workflow(target_products=target)
            
            if result["status"] == "completed":
                judgment = result["phases"]["judgment"]
                
                if judgment["verdict"] in ["PASS", "CONDITIONAL"]:
                    logger.info(f"Extraction successful: {judgment['verdict']}")
                    return result
                else:
                    logger.warning(f"Quality check failed: {judgment['verdict']}")
                    if attempt < max_attempts - 1:
                        continue
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            if attempt < max_attempts - 1:
                logger.info("Retrying...")
                continue
            raise
    
    return {"status": "failed", "error": "Max attempts exceeded"}

# Usage
result = extract_products_with_retry(target=200, max_attempts=3)
```

### Memory Analysis Integration

```python
from darwin_agent import DarwinAgent
from utils.primitive_loader import PrimitiveLoader

def analyze_extraction_history():
    """Analyze historical extraction performance"""
    
    loader = PrimitiveLoader()
    memory = loader.load_memory()
    
    # Analyze patterns
    patterns = memory.get("patterns", [])
    insights = memory.get("insights", [])
    
    print("Historical Patterns:")
    for pattern in patterns[-10:]:  # Last 10 patterns
        print(f"- {pattern}")
    
    print("\nKey Insights:")
    for insight in insights[-5:]:  # Last 5 insights
        print(f"- {insight}")
    
    # Performance trends
    last_run = memory.get("last_run", {})
    if last_run:
        print(f"\nLast Run: {last_run['timestamp']}")
        print(f"Status: {last_run['status']}")
        print(f"Products: {last_run['target_products']}")
        print(f"Verdict: {last_run.get('verdict', 'N/A')}")

# Usage
analyze_extraction_history()

# Run new extraction
agent = DarwinAgent()
result = agent.execute_workflow(target_products=150)
```

This API documentation provides comprehensive coverage of all public interfaces, data structures, and integration patterns for Darwin Agent.