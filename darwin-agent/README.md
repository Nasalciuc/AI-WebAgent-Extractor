# Darwin Agent - README

![Darwin Agent](https://img.shields.io/badge/Darwin-Agent-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![Framework](https://img.shields.io/badge/Framework-Agentic_Primitives-orange?style=for-the-badge)

An advanced agentic framework for intelligent web scraping of Darwin.md product data, implementing GitHub's Agentic Primitives architecture for reliable, adaptive, and high-quality data extraction.

## 🚀 Features

- **🤖 Agentic Architecture**: Four-mode system (Planner, Meta-Controller, Executor, Judge) for intelligent decision-making
- **🔄 Adaptive Strategy**: Self-optimizing extraction parameters based on real-time performance
- **📊 Quality Assurance**: Built-in data quality assessment and validation
- **🛡️ Robust Error Handling**: Multi-level error recovery with circuit breaker patterns
- **📈 Performance Monitoring**: Real-time metrics and historical trend analysis
- **🧠 Learning Memory**: Persistent memory system for continuous improvement
- **⚡ High Performance**: Parallel processing with dynamic worker scaling
- **🔧 Easy Integration**: Seamless integration with existing Darwin scraper components

## 🏗️ Architecture Overview

Darwin Agent implements GitHub's Agentic Primitives framework:

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐    ┌─────────────┐
│   PLANNER   │───▶│ META-CONTROLLER  │───▶│  EXECUTOR   │───▶│    JUDGE    │
│             │    │                  │    │             │    │             │
│ • Analyze   │    │ • Evaluate plan  │    │ • Extract   │    │ • Assess    │
│ • Discover  │    │ • Optimize       │    │ • Monitor   │    │ • Validate  │
│ • Strategy  │    │ • Adjust         │    │ • Handle    │    │ • Recommend │
└─────────────┘    └──────────────────┘    └─────────────┘    └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Valid OpenAI or Google Gemini API key
- Existing Darwin scraper components (from AI-webagent_extractor project)

### Installation

1. **Navigate to the Darwin Agent directory:**
   ```bash
   cd AI-webagent_extractor/darwin-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install requests beautifulsoup4 pandas pyyaml python-dotenv
   ```

3. **Configure environment:**
   ```bash
   # Create .env file in project root
   echo "OPENAI_API_KEY=your_key_here" > ../.env
   # or
   echo "GEMINI_API_KEY=your_key_here" > ../.env
   ```

### Basic Usage

```bash
# Extract 100 products (default)
python darwin_agent.py

# Extract specific number of products
python darwin_agent.py --target 50

# Verbose mode for detailed logging
python darwin_agent.py --target 200 --verbose
```

### Python Integration

```python
from darwin_agent import DarwinAgent

# Initialize and run extraction
agent = DarwinAgent()
result = agent.execute_workflow(target_products=100)

# Check results
if result["status"] == "completed":
    verdict = result["phases"]["judgment"]["verdict"]
    print(f"Extraction {verdict}: {result['phases']['execution']['successful']} products")
```

## 📋 Workflow Phases

### 1. 🎯 Planning Phase
- **Purpose**: Strategic analysis and extraction planning
- **Duration**: 30-60 seconds
- **Actions**: URL discovery, category analysis, resource planning
- **Output**: Extraction strategy with optimized parameters

### 2. 🎛️ Meta-Controller Phase
- **Purpose**: Plan evaluation and strategic optimization
- **Duration**: 15-30 seconds
- **Actions**: Risk assessment, parameter adjustment, plan approval
- **Output**: Optimized execution parameters

### 3. ⚡ Execution Phase
- **Purpose**: Parallel product data extraction
- **Duration**: Variable (depends on batch size)
- **Actions**: Multi-threaded extraction, real-time monitoring, error handling
- **Output**: Structured product data (JSON/CSV)

### 4. ⚖️ Judgment Phase
- **Purpose**: Quality assessment and results validation
- **Duration**: 30-60 seconds
- **Actions**: Data quality analysis, performance evaluation, recommendations
- **Output**: Quality verdict and improvement suggestions

## 📊 Performance Benchmarks

| Batch Size | Expected Time | Success Rate | Quality Score |
|------------|---------------|--------------|---------------|
| 1-50       | 2-5 minutes   | 90-95%       | 90-95%        |
| 51-200     | 10-20 minutes | 85-90%       | 85-90%        |
| 201-500    | 30+ minutes   | 80-85%       | 80-85%        |

## 🎛️ Command Line Options

```bash
python darwin_agent.py [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--target` | 100 | Number of products to extract |
| `--mode` | workflow | Execution mode (workflow/plan/execute/judge) |
| `--config` | None | Path to configuration file |
| `--verbose` | False | Enable detailed logging |

## 📁 Output Files

Darwin Agent generates structured output files:

### Product Data
- **JSON**: `darwin_agent_batch_YYYYMMDD_HHMMSS.json`
- **CSV**: `darwin_agent_batch_YYYYMMDD_HHMMSS.csv`

### Execution Results
- **Results**: `darwin_agent_results_YYYYMMDD_HHMMSS.json`

### Example Product Structure

```json
{
  "name": "iPhone 13 Pro Max 256GB",
  "price": 15999.0,
  "category": "accesorii-smartphone",
  "description": "Latest iPhone with advanced camera system...",
  "image_url": "https://darwin.md/images/iphone13pro.jpg",
  "brand": "Apple",
  "url": "https://darwin.md/accesorii-smartphone/iphone-13-pro-max"
}
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required: At least one AI provider
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Configuration File

Create a JSON configuration file for advanced settings:

```json
{
  "workers": 8,
  "batch_size": 150,
  "timeout": 30,
  "quality_threshold": 0.85,
  "retry_attempts": 3,
  "rate_limit_delay": 1.0
}
```

## 🧠 Adaptive Learning

Darwin Agent learns from each execution:

- **Pattern Recognition**: Identifies successful extraction strategies
- **Performance Optimization**: Adjusts parameters based on historical results
- **Quality Improvement**: Learns from data quality patterns
- **Error Prevention**: Recognizes and avoids recurring failure modes

## 🛡️ Error Handling

Multi-level error handling ensures reliability:

### Network Level
- Automatic retries with exponential backoff
- Connection pooling and keep-alive
- Circuit breaker for overloaded servers

### Application Level
- Graceful degradation for partial failures
- Data integrity validation
- Recovery strategies for common issues

### Workflow Level
- Phase-by-phase error isolation
- Fallback strategies for critical failures
- Comprehensive error reporting

## 📈 Monitoring & Quality

### Real-Time Metrics
- Extraction throughput and success rates
- Error frequency and categorization
- Resource utilization (CPU, memory, network)
- Data quality scores

### Quality Assessment
- Field completeness analysis
- Data consistency validation
- Format standardization
- Duplicate detection

## 🔧 Integration

### Existing Component Integration

Darwin Agent seamlessly integrates with existing project components:

```python
# Automatic integration with existing scraper
from darwin_scraper_complete import DarwinProductScraper
from env_config import get_environment_config

# Uses centralized configuration system
env_config = get_environment_config()
provider, api_key = env_config.select_ai_provider()
```

### AI Provider Support
- **OpenAI**: GPT models for intelligent processing
- **Google Gemini**: Alternative AI provider
- **Automatic Selection**: Based on available API keys

## 📚 Documentation

Comprehensive documentation available:

- **[User Guide](docs/user_guide.md)**: Complete usage instructions
- **[Technical Architecture](docs/technical_architecture.md)**: System design and implementation
- **[API Documentation](docs/api_documentation.md)**: Detailed API reference
- **[Mode Specifications](modes/)**: Individual mode documentation
- **[Technical Specs](specs/)**: Performance and extraction specifications

## 🔍 Project Structure

```
darwin-agent/
├── darwin_agent.py              # Main orchestrator
├── utils/
│   └── primitive_loader.py      # Primitive management
├── modes/
│   ├── workflow.md              # Workflow template
│   ├── planner.md               # Planning mode
│   ├── meta-controller.md       # Meta-control mode
│   ├── executor.md              # Execution mode
│   └── judge.md                 # Judgment mode
├── specs/
│   ├── extraction_spec.yaml     # Extraction specifications
│   └── performance_spec.yaml    # Performance benchmarks
├── docs/
│   ├── user_guide.md            # User documentation
│   ├── technical_architecture.md # Architecture details
│   └── api_documentation.md     # API reference
├── agent_instructions.yaml      # Agent configuration
└── README.md                    # This file
```

## 🚀 Advanced Usage

### Custom Configuration

```python
# Custom agent configuration
config = {
    "workers": 10,
    "quality_threshold": 0.90,
    "batch_size": 200
}

agent = DarwinAgent(config)
result = agent.execute_workflow(target_products=300)
```

### Memory Analysis

```python
from utils.primitive_loader import PrimitiveLoader

# Analyze historical performance
loader = PrimitiveLoader()
memory = loader.load_memory()

patterns = memory.get("patterns", [])
insights = memory.get("insights", [])

print("Performance Patterns:", patterns)
print("Key Insights:", insights)
```

### Individual Mode Execution

```bash
# Run only planning phase
python darwin_agent.py --mode plan --target 100

# Run only execution phase
python darwin_agent.py --mode execute --target 100

# Run only quality assessment
python darwin_agent.py --mode judge --target 100
```

## 📊 Example Results

### Successful Execution

```json
{
  "status": "completed",
  "timestamp": "2024-01-15T10:30:00",
  "target_products": 100,
  "phases": {
    "execution": {
      "processed": 100,
      "successful": 87,
      "success_rate": 0.87
    },
    "judgment": {
      "verdict": "PASS",
      "overall_score": 0.85,
      "approved_for_use": true
    }
  }
}
```

## 🛠️ Troubleshooting

### Common Issues

**Low success rate:**
```bash
# Reduce workers and increase delays
python darwin_agent.py --target 50 --verbose
```

**Memory issues:**
```bash
# Use smaller batches
python darwin_agent.py --target 25
```

**Configuration errors:**
```bash
# Check environment setup
python -c "from config.env_config import validate_environment; print(validate_environment())"
```

## 🤝 Contributing

1. Follow the existing code structure and documentation standards
2. Add tests for new functionality
3. Update documentation for any API changes
4. Ensure compatibility with existing scraper components

## 📄 License

This project is part of the AI-webagent_extractor suite and follows the same licensing terms.

## 🆘 Support

For support and questions:

1. Check the [User Guide](docs/user_guide.md) for common usage patterns
2. Review [Technical Architecture](docs/technical_architecture.md) for implementation details
3. Consult [API Documentation](docs/api_documentation.md) for integration help
4. Enable verbose logging (`--verbose`) for detailed troubleshooting

---

**Darwin Agent** - Intelligent, adaptive, and reliable web scraping powered by agentic architecture. 🤖✨