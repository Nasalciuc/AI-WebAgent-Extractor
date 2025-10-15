# Darwin Agent - Technical Architecture

## System Overview

Darwin Agent implements GitHub's Agentic Primitives framework to create an intelligent, adaptive web scraping system for Darwin.md product extraction. The architecture follows a multi-mode approach with each mode having specific responsibilities and capabilities.

## Core Architecture

### Agent Framework Structure

```
Darwin Agent
├── Main Orchestrator (darwin_agent.py)
├── Primitive Loader (utils/primitive_loader.py)
├── Mode Manager (embedded in primitive_loader.py)
├── Mode Definitions (modes/)
├── Specifications (specs/)
├── Documentation (docs/)
└── Memory System (agent_memory.json)
```

### Agentic Primitives Implementation

#### 1. Planning Primitive
- **File**: `modes/planner.md`
- **Class**: `DarwinAgent._plan_extraction()`
- **Purpose**: Strategic analysis and extraction planning
- **Inputs**: Target requirements, historical data
- **Outputs**: URL inventory, resource plan, strategy

#### 2. Meta-Control Primitive
- **File**: `modes/meta-controller.md`
- **Class**: `DarwinAgent._meta_control()`
- **Purpose**: Plan evaluation and optimization
- **Inputs**: Extraction plan, constraints
- **Outputs**: Approved plan, adjustments, risk assessment

#### 3. Execution Primitive
- **File**: `modes/executor.md`
- **Class**: `DarwinAgent._execute_extraction()`
- **Purpose**: Primary extraction engine
- **Inputs**: Approved plan parameters
- **Outputs**: Extracted data, performance metrics

#### 4. Judgment Primitive
- **File**: `modes/judge.md`
- **Class**: `DarwinAgent._judge_results()`
- **Purpose**: Quality assessment and validation
- **Inputs**: Extraction results, quality metrics
- **Outputs**: Final verdict, recommendations

## Component Architecture

### Main Orchestrator (`darwin_agent.py`)

The main orchestrator coordinates the entire extraction workflow:

```python
class DarwinAgent:
    def __init__(self):
        # Initialize primitive loader and mode manager
        # Setup logging and configuration
        # Load existing scraper components
    
    def execute_workflow(self, target_products):
        # Phase 1: Planning
        # Phase 2: Meta-controller evaluation
        # Phase 3: Execution
        # Phase 4: Judgment
        # Update persistent memory
```

**Key Responsibilities:**
- Workflow coordination
- Mode transition management
- Error handling and recovery
- Memory persistence
- Integration with existing scraper

### Primitive Loader (`utils/primitive_loader.py`)

Manages loading and interpolation of agent primitives:

```python
class PrimitiveLoader:
    def load_mode(self, mode_name)         # Load mode prompts
    def load_workflow_prompt()             # Load workflow template
    def load_memory()                      # Load persistent memory
    def save_memory(memory)                # Persist memory updates
    def interpolate_template(template, context)  # Template processing
```

**Key Features:**
- Template interpolation system
- Memory persistence management
- Configuration loading
- Mode prompt management

### Mode Manager

Handles mode transitions and context:

```python
class ModeManager:
    def get_next_mode(current_mode, context)    # Determine next mode
    def transition_to(mode)                     # Execute mode transition
    def get_mode_context(mode)                  # Get mode-specific context
```

## Data Flow Architecture

### Workflow Data Flow

```
Input Parameters
    ↓
Planning Mode
    ↓ (URL list, strategy)
Meta-Controller Mode
    ↓ (Approved plan, adjustments)
Execution Mode
    ↓ (Extracted data, metrics)
Judgment Mode
    ↓ (Verdict, recommendations)
Output Files & Memory Update
```

### Inter-Mode Communication

**Planning → Meta-Controller:**
```json
{
  "selected_urls": ["url1", "url2", ...],
  "url_analysis": {"category_distribution": {...}},
  "strategy": "batch_parallel",
  "estimated_time_minutes": 30,
  "recommended_workers": 8
}
```

**Meta-Controller → Executor:**
```json
{
  "decisions": ["Large batch detected"],
  "adjustments": {"workers": 6, "batch_size": 100},
  "approved": true,
  "confidence": 0.85
}
```

**Executor → Judge:**
```json
{
  "processed": 100,
  "successful": 87,
  "failed": 13,
  "success_rate": 0.87,
  "output_files": {"json": "path", "csv": "path"}
}
```

## Integration Architecture

### Existing Component Integration

**Darwin Scraper Integration:**
```python
# Seamless integration with existing scraper
if SCRAPER_AVAILABLE:
    from darwin_scraper_complete import DarwinProductScraper
    from env_config import get_environment_config
    
    # Initialize with existing configuration system
    env_config = get_environment_config()
    provider, api_key = env_config.select_ai_provider()
    self.scraper = DarwinProductScraper(...)
```

**Configuration System Integration:**
- Uses existing `env_config.py` for API key management
- Maintains compatibility with existing environment setup
- Leverages centralized configuration approach

### AI Provider Integration

**Multi-Provider Support:**
```python
# Automatic provider selection
provider, api_key = env_config.select_ai_provider()

# Provider-specific initialization
if provider == "openai":
    self.scraper = DarwinProductScraper(openai_api_key=api_key)
elif provider == "gemini":
    self.scraper = DarwinProductScraper(gemini_api_key=api_key)
```

## Memory Architecture

### Persistent Memory System

**Memory Structure:**
```json
{
  "last_run": {
    "timestamp": "2024-01-15T10:30:00",
    "status": "completed",
    "target_products": 100,
    "verdict": "PASS"
  },
  "patterns": [
    "Category 'smartphone' most common with 45 products",
    "High success rate achieved: 89.2%"
  ],
  "insights": [
    "Optimal worker count for medium batches: 6",
    "Best extraction time: 14:00-16:00 UTC"
  ],
  "performance_history": [...]
}
```

**Memory Operations:**
- Load previous execution results
- Store patterns and insights
- Track performance trends
- Enable adaptive behavior

### Learning and Adaptation

**Pattern Recognition:**
- Identify successful extraction strategies
- Recognize error patterns and solutions
- Learn optimal resource allocation
- Adapt to site structure changes

**Performance Optimization:**
- Track success rates by batch size
- Optimize worker allocation based on history
- Adjust strategies based on results
- Improve quality prediction

## Error Handling Architecture

### Multi-Level Error Handling

**1. Network Level:**
```python
# Retry with exponential backoff
max_retries = 3
for attempt in range(max_retries):
    try:
        response = request_with_timeout(url)
        break
    except (RequestException, Timeout) as e:
        wait_time = (2 ** attempt) * base_delay
        time.sleep(wait_time)
```

**2. Mode Level:**
```python
# Mode-specific error handling
def _execute_mode(self, mode_name, context):
    try:
        return mode_execution(context)
    except Exception as e:
        return {
            "phase": mode_name,
            "status": "failed",
            "error": str(e),
            "recovery_suggestions": [...]
        }
```

**3. Workflow Level:**
```python
# Graceful workflow degradation
if planning_result.get("status") != "completed":
    return {"status": "failed", "reason": "Planning failed"}
```

### Circuit Breaker Pattern

**Implementation:**
- Monitor error rates in real-time
- Open circuit when error threshold exceeded
- Implement fallback strategies
- Automatic recovery after cooldown period

## Performance Architecture

### Concurrency Model

**Thread Pool Execution:**
```python
# Adaptive worker allocation
workers = min(max_workers, max(min_workers, optimal_for_batch_size))

# Parallel extraction with proper resource management
with ThreadPoolExecutor(max_workers=workers) as executor:
    futures = [executor.submit(extract_product, url) for url in urls]
    results = [future.result() for future in futures]
```

**Resource Management:**
- Dynamic worker scaling based on performance
- Memory usage monitoring and optimization
- CPU utilization balancing
- Network bandwidth management

### Caching and Optimization

**CSS Selector Caching:**
```python
# Compiled selector caching for performance
selector_cache = {}

def get_cached_selector(selector_string):
    if selector_string not in selector_cache:
        selector_cache[selector_string] = compile_selector(selector_string)
    return selector_cache[selector_string]
```

**Connection Pooling:**
- Reuse HTTP connections
- Maintain session state
- Implement keep-alive connections
- Optimize SSL handshakes

## Monitoring Architecture

### Real-Time Monitoring

**Metrics Collection:**
```python
class MetricsCollector:
    def track_extraction_rate(self, rate)
    def track_success_percentage(self, percentage)
    def track_error_frequency(self, errors)
    def track_resource_usage(self, cpu, memory)
```

**Performance Tracking:**
- Extraction throughput monitoring
- Success rate calculation
- Error pattern analysis
- Resource utilization tracking

### Quality Monitoring

**Data Quality Metrics:**
```python
def analyze_data_quality(products):
    completeness = calculate_field_completeness(products)
    consistency = check_format_consistency(products)
    accuracy = validate_data_accuracy(products)
    
    return {
        "completeness": completeness,
        "consistency": consistency,
        "accuracy": accuracy,
        "overall_score": weighted_average(...)
    }
```

## Security Architecture

### Data Protection

**API Key Security:**
- Integration with existing secure configuration system
- No hardcoded credentials
- Environment variable isolation
- Configuration encryption support

**Data Privacy:**
- No personal data collection
- Respect for site privacy policies
- Secure temporary data handling
- Automatic cleanup of sensitive data

### Access Control

**Rate Limiting:**
- Respectful request rates
- Adaptive throttling based on server response
- Circuit breaker for overload protection
- Compliance with robots.txt

## Deployment Architecture

### Modular Deployment

**Component Independence:**
```
darwin-agent/
├── darwin_agent.py          # Main executable
├── utils/                   # Utility modules
├── modes/                   # Mode definitions
├── specs/                   # Technical specifications
└── docs/                    # Documentation
```

**Deployment Options:**
- Standalone execution
- Integration with existing projects
- Container deployment support
- Scalable worker deployment

### Configuration Management

**Multi-Level Configuration:**
1. Environment variables (`.env`)
2. Configuration files (`config.json`)
3. Command-line arguments
4. Runtime dynamic configuration

**Configuration Hierarchy:**
```
Command Line Args > Config File > Environment Variables > Defaults
```

This architecture ensures Darwin Agent is robust, scalable, maintainable, and seamlessly integrates with existing project components while providing advanced agentic capabilities for intelligent web scraping.