# Darwin Agent - Intelligent E-commerce Data Extraction Framework

🤖 **Advanced Agentic Web Scraping System for Darwin.md**

A sophisticated, AI-powered web scraping framework that implements agentic principles for intelligent, adaptive data extraction from Darwin.md. Built with multiple specialized agents, comprehensive memory systems, and production-ready reliability patterns.

## � Darwin Agent Framework

### Agentic Architecture
- **4-Mode Agent System**
  - **Planner Agent**: Strategic extraction planning and URL analysis
  - **Meta-Controller**: Orchestration and workflow management
  - **Executor Agent**: Adaptive scraping with method selection
  - **Judge Agent**: Quality evaluation and data validation

- **Specialized Chat Modes**
  - Individual agent specialists with clear boundaries
  - Context-aware responses and domain expertise
  - Quality scoring and threshold-based feedback

### Intelligence & Memory
- **Persistent Memory System** (`.memory.md`)
  - Method success rates and performance tracking
  - Failed URL history with pattern analysis
  - Site structure learnings and optimization insights
  - Best-performing configurations and timing

- **Pattern Intelligence** (`docs/darwin-patterns.md`)
  - Comprehensive site structure documentation
  - JavaScript behavior analysis and AJAX endpoints
  - Rate limiting guidelines and polite scraping
  - Currency format patterns and category taxonomy

## 🌟 Key Features

### Multi-Method Scraping Engine
- **DrissionPage** (85% success) - Dynamic content and AJAX handling
- **Selenium** (75% success) - Complex interactions and JavaScript
- **BeautifulSoup** (65% success) - Fast static content parsing
- **Auto Method** (80% success) - Intelligent fallback chains

### Advanced Data Extraction
- **Comprehensive Product Intelligence**
  - Full specifications with fallback selectors
  - MDL currency format parsing with regex patterns
  - Lazy-loaded image extraction from data-src attributes
  - Stock status and rating information
  - Product variants and configuration options

- **Smart Content Handling**
  - JavaScript behavior prediction and waiting
  - Dynamic price loading with AJAX detection
  - Category hierarchy extraction and validation
  - Brand recognition and model identification

### Production-Ready Reliability
- **Adaptive Rate Limiting**
  - 1.2-1.5 second optimal delays between requests
  - Peak traffic avoidance (9-17 UTC Moldova time)
  - Exponential backoff with circuit breaker patterns
  - User-Agent rotation and header randomization

- **Error Recovery Systems**
  - Multi-level selector fallback chains
  - Method switching on failure detection
  - Temporary cooling periods for rate limiting
  - Statistical success rate tracking and optimization

### Agentic Workflow Orchestration
- **6-Phase Processing Pipeline**
  - Context Analysis → Planning → Routing → Execution → Evaluation → Learning
  - Validation gates between each phase
  - Memory persistence and pattern recognition
  - Adaptive strategy selection based on success rates

## 📁 Project Architecture

```
AI-webagent_extractor/
├── darwin-agent/                    # 🤖 Darwin Agent Framework
│   ├── darwin_agent.py            # Main agentic orchestrator (502 lines)
│   ├── utils/
│   │   └── primitive_loader.py     # Primitive management & memory system
│   ├── modes/                      # Agent workflow definitions
│   │   ├── workflow.md             # Main workflow orchestration
│   │   ├── planner.md              # Strategic planning agent
│   │   ├── meta-controller.md      # Orchestration control
│   │   ├── executor.md             # Execution specialist
│   │   ├── judge.md                # Quality evaluation agent
│   │   ├── planner.chatmode.md     # Planner chat specialist (243 lines)
│   │   ├── executor.chatmode.md    # Executor chat specialist (364 lines)
│   │   └── judge.chatmode.md       # Judge chat specialist (396 lines)
│   ├── specs/                      # Technical specifications
│   │   ├── extraction_spec.yaml    # Data extraction requirements
│   │   └── performance_spec.yaml   # Performance benchmarks
│   ├── docs/                       # Agent documentation
│   │   ├── user_guide.md           # User documentation
│   │   ├── technical_architecture.md # Technical details
│   │   └── api_documentation.md    # API reference
│   └── agent_instructions.yaml     # Agent configuration
├── src/                            # Core scraping engine
│   ├── darwin_scraper_complete.py  # Multi-method scraper with Gemini/OpenAI
│   ├── darwin_sitemap_processor_v2.py # Sitemap analysis
│   ├── darwin_product_analyzer.py  # Product intelligence
│   └── process_products.py         # Batch processing orchestrator
├── docs/                           # 📚 Intelligence Documentation
│   └── darwin-patterns.md          # Comprehensive site patterns (500+ lines)
├── .instructions.md                # 🧠 GitHub Copilot domain knowledge (290+ lines)
├── .memory.md                      # 🔄 Persistent agent memory across sessions
├── scraping-workflow.prompt.md     # 🔀 Agentic workflow orchestration (6-phase)
├── data/                           # Data storage
│   ├── raw/                        # Raw extraction results
│   ├── processed/                  # Cleaned and validated data
│   └── analytics/                  # Analysis outputs
└── logs/                          # Comprehensive logging system
```

### Key Components

#### 🤖 Darwin Agent Framework
- **Main Orchestrator** (`darwin-agent/darwin_agent.py`) - 502-line agentic system
- **4 Workflow Modes** - Planner, Meta-Controller, Executor, Judge
- **3 Chat Mode Specialists** - Individual agent roles with clear boundaries
- **Memory & Primitive Management** - Persistent learning and template systems

#### 📚 Intelligence Systems
- **Pattern Documentation** (`docs/darwin-patterns.md`) - Complete site intelligence
- **Memory System** (`.memory.md`) - Performance tracking and learning insights
- **Workflow Orchestration** (`scraping-workflow.prompt.md`) - 6-phase agentic process
- **GitHub Copilot Instructions** (`.instructions.md`) - Domain knowledge integration

## 🔧 Technical Requirements

### System Requirements
- **Python**: 3.8+ (3.10+ recommended for optimal performance)
- **Memory**: 4GB RAM minimum (8GB recommended for large batches)
- **Network**: Stable internet connection with 1.2-1.5s delay capability
- **Platform**: Windows/Linux/macOS compatible
- **Storage**: 1GB+ for data, logs, and memory persistence

### Core Dependencies
```python
# Web Scraping Engine
beautifulsoup4>=4.9.3      # Static HTML parsing
requests>=2.26.0           # HTTP client
lxml>=4.6.3               # XML/HTML processing
drissionpage>=4.0.0       # Dynamic content handling
selenium>=4.0.0           # Browser automation

# AI Integration
openai>=1.0.0             # OpenAI API client
google-generativeai>=0.3.0 # Gemini API client

# Data Processing
pandas>=1.3.0             # Data manipulation
pyyaml>=6.0               # Configuration files
```

### Optional Dependencies
```python
# Enhanced Performance
aiohttp>=3.8.1            # Async HTTP requests  
uvloop>=0.17.0            # Fast async event loop (Unix only)
ujson>=5.0.0              # Faster JSON processing

# Monitoring & Analysis
psutil>=5.8.0             # System monitoring
matplotlib>=3.5.0         # Data visualization
```

## 🚀 Installation & Setup

### 1. Clone & Environment Setup
```bash
# Clone the repository
git clone https://github.com/Nasalciuc/AI-WebAgent-Extractor.git
cd AI-webagent_extractor

# Set up Python environment (Conda recommended)
conda create -n py310 python=3.10
conda activate py310

# Alternative: Using venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

### 2. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install optional performance packages
pip install aiohttp uvloop ujson psutil matplotlib
```

### 3. Configure API Keys
```bash
# Create environment file
cp .env.example .env

# Edit .env with your API keys:
# OPENAI_API_KEY=your_openai_key_here
# GEMINI_API_KEY=your_gemini_key_here
```

### 4. Verify Installation
```bash
# Test Darwin Agent framework
python darwin-agent/darwin_agent.py --help

# Test legacy scraper
python src/darwin_scraper_complete.py --help
```

## 💻 Usage

### 🤖 Darwin Agent Framework (Recommended)

#### Basic Agentic Extraction
```bash
# Run complete agentic workflow
python darwin-agent/darwin_agent.py

# Specify mode and target URLs
python darwin-agent/darwin_agent.py --mode executor --urls https://darwin.md/category/smartphones

# Use specific scraping method
python darwin-agent/darwin_agent.py --method drissionpage --batch-size 50
```

#### Agent Modes
```bash
# Strategic planning mode
python darwin-agent/darwin_agent.py --mode planner --analyze-sitemap

# Execution with quality monitoring  
python darwin-agent/darwin_agent.py --mode executor --enable-judge

# Meta-controller for complex workflows
python darwin-agent/darwin_agent.py --mode meta-controller --multi-category
```

#### Advanced Configuration
```bash
# High-performance batch processing
python darwin-agent/darwin_agent.py \
  --mode executor \
  --method auto \
  --workers 8 \
  --batch-size 25 \
  --delay-range 1.2 1.5 \
  --enable-memory

# Quality-focused extraction
python darwin-agent/darwin_agent.py \
  --mode judge \
  --quality-threshold 8.0 \
  --validation-strict \
  --retry-failed
```

### 🔧 Legacy Scraper (Production Use)

#### Basic Usage
```bash
# Standard batch processing
python src/process_products.py

# Multi-method extraction
python src/darwin_scraper_complete.py --method auto --workers 5
```

#### Parameters
- `--workers`: Parallel workers (1-10, default: 5)
- `--batch-size`: Products per batch (10-100, default: 50)  
- `--method`: Scraping method (`auto`, `drissionpage`, `selenium`, `beautifulsoup`)
- `--delay-range`: Request delays in seconds (default: 1.2-1.5)
- `--retry-count`: Failed request retries (default: 3)
- `--output-dir`: Custom output directory
- `--log-level`: Logging detail (`DEBUG`, `INFO`, `WARNING`, `ERROR`)

## 📊 Data Output & Intelligence

### Enhanced JSON Format
```json
{
  "extraction_metadata": {
    "agent_mode": "executor",
    "method_used": "drissionpage", 
    "success_rate": 0.92,
    "quality_score": 8.7,
    "extraction_time": 2.3
  },
  "product_data": {
    "url": "https://darwin.md/product/iphone-15-pro-max-256gb-12345",
    "title": "iPhone 15 Pro Max 256GB Natural Titanium",
    "price": 28999.00,
    "currency": "MDL",  
    "price_formatted": "28,999 MDL",
    "brand": "Apple",
    "model": "iPhone 15 Pro Max",
    "category": "Smartphones",
    "subcategory": "Premium Smartphones",
    "stock_status": "available",
    "rating": 4.8,
    "specs": {
      "storage": "256GB",
      "color": "Natural Titanium", 
      "screen_size": "6.7 inch",
      "ram": "8GB"
    },
    "images": [
      "https://cdn.darwin.md/images/products/large/12345/front.jpg",
      "https://cdn.darwin.md/images/products/large/12345/back.jpg"
    ],
    "extracted_at": "2025-10-15T14:32:00Z",
    "validation_status": "passed"
  }
}
```

### Memory & Analytics Output
```json
{
  "session_summary": {
    "total_products": 150,
    "success_rate": 0.87,
    "avg_quality_score": 8.2,
    "method_performance": {
      "drissionpage": 0.85,
      "selenium": 0.75, 
      "beautifulsoup": 0.65
    }
  },
  "learnings_captured": [
    "Category smartphones has best selector stability",
    "Peak hours 9-17 UTC show 23% slower response times",
    "Image lazy loading requires 2s wait for data-src population"
  ]
}
```

### CSV Structure (Enhanced)
- `agent_mode`, `method_used`, `quality_score`
- `product_id`, `url`, `title`, `price_mdl`, `currency`  
- `brand`, `model`, `category`, `subcategory`
- `stock_status`, `rating`, `specifications_json`
- `image_count`, `extraction_time_seconds`
- `validation_status`, `retry_count`, `extracted_at`

## 🔍 Monitoring & Intelligence

### Agentic Memory System
- **Persistent Learning** (`.memory.md`) - Method success rates, failed URL patterns, site learnings
- **Pattern Intelligence** (`docs/darwin-patterns.md`) - Site structure, selectors, JavaScript behavior
- **Performance Tracking** - Real-time success rates, timing optimization, error pattern analysis

### Advanced Logging
```
logs/
├── darwin_agent_YYYYMMDD_HHMMSS.log      # Agentic workflow logs
├── method_performance_YYYYMMDD.log        # Scraping method analytics  
├── quality_assessment_YYYYMMDD.log        # Judge agent evaluations
├── memory_updates_YYYYMMDD.log            # Learning and adaptation logs
└── error_analysis_YYYYMMDD.log           # Detailed error patterns
```

### Log Categories
- **AGENT**: Agentic workflow events and decisions
- **EXTRACTION**: Scraping operations and method selection
- **QUALITY**: Data validation and scoring events  
- **MEMORY**: Learning updates and pattern recognition
- **PERFORMANCE**: Timing, throughput, and optimization metrics

### Real-Time Monitoring
```python
# Access current session statistics
from darwin_agent import DarwinAgent
agent = DarwinAgent()
stats = agent.get_session_stats()

print(f"Success Rate: {stats.success_rate:.1%}")
print(f"Avg Quality Score: {stats.avg_quality_score:.1f}/10")
print(f"Best Method: {stats.best_method} ({stats.best_method_rate:.1%})")
```

## 🛠 Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/
```

### Code Style
- Following PEP 8 guidelines
- Type hints for all functions
- Comprehensive docstrings
- Maximum line length: 100 characters

## 🔄 Development Status & Roadmap

### ✅ Phase 1 - Core Framework (Completed)
- [x] **Darwin Agent Framework** - Complete 4-mode agentic system (502 lines)
- [x] **Multi-Method Scraping** - DrissionPage, Selenium, BeautifulSoup, Auto selection
- [x] **Persistent Memory System** - Learning and performance tracking across sessions
- [x] **Pattern Intelligence** - Comprehensive Darwin.md site documentation (500+ lines)
- [x] **Specialized Chat Modes** - Individual agent specialists (Planner, Executor, Judge)
- [x] **Quality Assessment** - 3-dimensional scoring with threshold validation
- [x] **Agentic Workflow** - 6-phase orchestration with validation gates

### ✅ Phase 2 - Intelligence Systems (Completed)  
- [x] **GitHub Copilot Integration** - Domain knowledge loading (290+ lines)
- [x] **Memory Persistence** - Failed URL tracking, success rate analysis
- [x] **Adaptive Method Selection** - Real-time performance optimization
- [x] **Rate Limiting Intelligence** - Moldova timezone awareness, peak avoidance
- [x] **Currency Format Handling** - MDL parsing with regex patterns
- [x] **JavaScript Behavior Analysis** - AJAX endpoints, lazy loading patterns

### 🚧 Phase 3 - Production Optimization (In Progress)
- [ ] **Gemini API Integration** - Complete .env configuration refactoring  
- [ ] **AI-Powered Sitemap Analysis** - Semantic URL categorization and understanding
- [ ] **Enhanced Error Recovery** - Predictive failure detection and prevention
- [ ] **Performance Benchmarking** - Automated A/B testing of extraction methods
- [ ] **Multi-Site Expansion** - Framework adaptation for other e-commerce platforms

### 🎯 Phase 4 - Advanced Features (Planned)
- [ ] **Real-Time Price Monitoring** - Change detection and alerting system
- [ ] **Competitive Intelligence** - Cross-platform price comparison
- [ ] **API Gateway** - RESTful endpoints for external integration  
- [ ] **Web Dashboard** - Real-time monitoring and control interface
- [ ] **Machine Learning Models** - Predictive success rate optimization

## � Testing & Validation

### Automated Testing
```bash
# Run complete test suite
python -m pytest tests/ -v

# Test Darwin Agent framework
python -m pytest tests/test_darwin_agent.py

# Test method performance
python -m pytest tests/test_scraping_methods.py

# Integration testing with real URLs
python -m pytest tests/integration/ --slow
```

### Manual Validation
```bash
# Test single product extraction
python darwin-agent/darwin_agent.py --mode executor --test-url https://darwin.md/product/test-item

# Validate memory system
python darwin-agent/darwin_agent.py --mode planner --analyze-memory

# Quality assessment check
python darwin-agent/darwin_agent.py --mode judge --validate-recent
```

## 🤝 Contributing

### Quick Start for Contributors
1. **Fork & Clone**
   ```bash
   git fork https://github.com/Nasalciuc/AI-WebAgent-Extractor.git
   git clone your-fork-url
   cd AI-webagent_extractor
   ```

2. **Set Up Development Environment**
   ```bash
   conda create -n darwin-dev python=3.10
   conda activate darwin-dev
   pip install -r requirements.txt -r requirements-dev.txt
   ```

3. **Run Pre-commit Checks**
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

### Contribution Areas
- 🤖 **Agent Development** - New modes, improved prompts, chat mode specialists
- 🔍 **Scraping Methods** - New extraction techniques, selector improvements
- 📊 **Intelligence Systems** - Memory enhancements, pattern recognition
- 🧪 **Testing** - Test coverage, integration scenarios, performance benchmarks
- 📚 **Documentation** - API docs, usage examples, pattern updates

### Code Standards
- **Python Style**: PEP 8 with Black formatting (line length: 100)
- **Type Hints**: Required for all public functions and methods
- **Documentation**: Comprehensive docstrings with examples
- **Testing**: Minimum 80% code coverage for new features
- **Agentic Patterns**: Follow GitHub's Agentic Primitives guidelines

## 📝 License & Legal

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Darwin.md Terms Compliance
- Respects robots.txt and rate limiting guidelines
- Implements polite scraping with 1.2-1.5s delays
- Avoids peak traffic hours (9-17 UTC Moldova time)  
- Uses proper User-Agent headers and accepts Moldova locale
- Educational and research use case alignment

## 📧 Contact & Support

### Project Maintainer
**@Nasalciuc** - [GitHub Profile](https://github.com/Nasalciuc)

### Community & Support
- **Project Repository**: [AI-WebAgent-Extractor](https://github.com/Nasalciuc/AI-WebAgent-Extractor)
- **Issues & Bug Reports**: [GitHub Issues](https://github.com/Nasalciuc/AI-WebAgent-Extractor/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/Nasalciuc/AI-WebAgent-Extractor/discussions)
- **Documentation**: [Project Wiki](https://github.com/Nasalciuc/AI-WebAgent-Extractor/wiki)

## 🙏 Acknowledgments & Credits

### Core Technologies
- **DrissionPage** - Dynamic content extraction capabilities
- **Selenium** - Browser automation and JavaScript handling  
- **BeautifulSoup4** - Fast HTML parsing and selector engine
- **OpenAI/Gemini APIs** - AI-powered analysis and categorization

### Agentic Framework Inspiration
- **GitHub's Agentic Primitives** - Framework design principles
- **LangChain Community** - Agent orchestration patterns
- **Microsoft Semantic Kernel** - Multi-modal AI integration approaches

### Darwin.md Ecosystem
- **Darwin.md Platform** - Well-structured e-commerce site enabling reliable extraction
- **Moldova E-commerce Community** - Providing excellent MDL currency and Romanian language examples

---

*Built with ❤️ for intelligent, ethical web data extraction*