# Darwin Agent - User Guide

## Overview

Darwin Agent is an advanced agentic framework for extracting product data from Darwin.md using GitHub's Agentic Primitives architecture. It implements a four-mode system (Planner, Meta-Controller, Executor, Judge) to ensure reliable, efficient, and high-quality data extraction.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Valid OpenAI or Google Gemini API key
- Stable internet connection

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd AI-webagent_extractor/darwin-agent
   ```

2. **Install required dependencies:**
   ```bash
   pip install requests beautifulsoup4 pandas pyyaml python-dotenv
   ```

3. **Configure environment:**
   - Create a `.env` file in the project root
   - Add your API keys:
     ```
     OPENAI_API_KEY=your_openai_key_here
     GEMINI_API_KEY=your_gemini_key_here
     ```

### Basic Usage

**Extract 100 products (default):**
```bash
python darwin_agent.py
```

**Extract specific number of products:**
```bash
python darwin_agent.py --target 50
```

**Run with verbose logging:**
```bash
python darwin_agent.py --target 200 --verbose
```

**Use configuration file:**
```bash
python darwin_agent.py --config my_config.json --target 150
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--target` | Number of products to extract | 100 |
| `--mode` | Execution mode (workflow/plan/execute/judge) | workflow |
| `--config` | Path to configuration file | None |
| `--verbose` | Enable detailed logging | False |

## Execution Modes

### Workflow Mode (Recommended)
Executes the complete four-phase agentic workflow:
```bash
python darwin_agent.py --mode workflow --target 100
```

### Individual Mode Execution
For testing or debugging specific phases:

**Planning only:**
```bash
python darwin_agent.py --mode plan --target 100
```

**Execution only (requires prior planning):**
```bash
python darwin_agent.py --mode execute --target 100
```

**Quality assessment only:**
```bash
python darwin_agent.py --mode judge --target 100
```

## Understanding the Agent Workflow

### Phase 1: Planning
- **Purpose**: Analyze target and develop extraction strategy
- **Duration**: 30-60 seconds
- **Output**: URL list, category analysis, resource plan

**What happens:**
- Discovers all available product URLs on Darwin.md
- Analyzes URL patterns and product distribution
- Estimates resource requirements and optimal parameters
- Develops extraction strategy based on batch size

### Phase 2: Meta-Controller
- **Purpose**: Evaluate plan and make strategic adjustments
- **Duration**: 15-30 seconds
- **Output**: Approved plan with optimizations

**What happens:**
- Reviews planning results for feasibility
- Assesses resource constraints and risks
- Makes strategic adjustments (worker count, batch sizes)
- Approves or modifies execution parameters

### Phase 3: Execution
- **Purpose**: Extract product data according to approved plan
- **Duration**: Variable (depends on target size)
- **Output**: Product data files (JSON/CSV)

**What happens:**
- Implements parallel extraction with optimized workers
- Monitors performance in real-time
- Handles errors and retries automatically
- Generates structured output files

### Phase 4: Judgment
- **Purpose**: Evaluate results and assess quality
- **Duration**: 30-60 seconds
- **Output**: Quality assessment and recommendations

**What happens:**
- Analyzes extraction metrics and success rates
- Evaluates data quality and completeness
- Provides overall verdict (PASS/CONDITIONAL/FAIL)
- Generates recommendations for future runs

## Output Files

Darwin Agent generates several output files:

### Product Data
- **JSON**: `darwin_agent_batch_YYYYMMDD_HHMMSS.json`
- **CSV**: `darwin_agent_batch_YYYYMMDD_HHMMSS.csv`

### Execution Results
- **Results**: `darwin_agent_results_YYYYMMDD_HHMMSS.json`
- **Logs**: Console output with detailed execution information

### Example Output Structure
```json
{
  "name": "iPhone 13 Pro Max",
  "price": 15999.0,
  "category": "accesorii-smartphone",
  "description": "Latest iPhone model with advanced features...",
  "image_url": "https://darwin.md/images/iphone13pro.jpg",
  "brand": "Apple",
  "url": "https://darwin.md/accesorii-smartphone/iphone-13-pro-max"
}
```

## Configuration

### Environment Variables
Set in `.env` file or system environment:
- `OPENAI_API_KEY`: OpenAI API key for AI processing
- `GEMINI_API_KEY`: Google Gemini API key (alternative)

### Configuration File
Create a JSON configuration file for advanced settings:
```json
{
  "workers": 8,
  "batch_size": 150,
  "timeout": 30,
  "quality_threshold": 0.85
}
```

## Performance Guidelines

### Batch Size Recommendations

**Small Batches (1-50 products):**
- Expected time: 2-5 minutes
- Workers: 3-5
- Best for: Testing, specific category extraction

**Medium Batches (51-200 products):**
- Expected time: 10-20 minutes
- Workers: 5-8
- Best for: Regular data collection, category analysis

**Large Batches (201+ products):**
- Expected time: 30+ minutes
- Workers: 8-10
- Best for: Comprehensive data collection, research

### Success Rate Expectations

| Batch Size | Expected Success Rate | Quality Score |
|------------|----------------------|---------------|
| 1-50 | 90-95% | 90-95% |
| 51-200 | 85-90% | 85-90% |
| 201-500 | 80-85% | 80-85% |
| 500+ | 75-80% | 75-80% |

## Troubleshooting

### Common Issues

**"No valid AI configuration found"**
- Solution: Check your `.env` file and ensure API keys are set correctly
- Verify API key validity by testing with a simple request

**"Scraper not available - check configuration"**
- Solution: Ensure all required dependencies are installed
- Check if the existing Darwin scraper components are accessible

**Low success rate (<70%)**
- Possible causes: Network issues, site changes, rate limiting
- Solutions: Reduce worker count, increase delays, check site status

**Memory usage warnings**
- Solution: Reduce batch size or worker count
- Consider processing in smaller chunks for large extractions

### Performance Optimization

**Slow extraction speeds:**
1. Check network connection stability
2. Reduce worker count if high error rates
3. Consider running during off-peak hours
4. Verify system resources (RAM, CPU)

**High error rates:**
1. Implement longer delays between requests
2. Reduce concurrent workers
3. Check if Darwin.md has anti-bot measures
4. Verify site structure hasn't changed

### Debug Mode

Enable verbose logging for detailed troubleshooting:
```bash
python darwin_agent.py --verbose --target 10
```

This provides:
- Detailed phase-by-phase execution information
- Individual product extraction results
- Error details and stack traces
- Performance metrics for each phase

## Best Practices

### Respectful Scraping
- Use reasonable batch sizes (≤500 products per run)
- Don't run multiple instances simultaneously
- Respect rate limits and implement delays
- Monitor Darwin.md server response times

### Data Quality
- Regularly validate output data quality
- Review extraction results before using in production
- Monitor field completeness trends
- Update extraction logic if site structure changes

### Monitoring
- Check success rates and adjust strategy if needed
- Monitor memory usage for large batches
- Review error patterns to identify systematic issues
- Keep extraction logs for troubleshooting

### Scheduling
- Run extractions during off-peak hours when possible
- Space out large extractions over time
- Consider incremental updates rather than full re-extractions
- Monitor Darwin.md traffic patterns

## Support and Maintenance

### Updating the Agent
1. Backup current configuration and data
2. Update source code files
3. Test with small batch before full deployment
4. Review and update configuration if needed

### Monitoring Health
- Check success rates regularly
- Monitor data quality trends
- Review error patterns
- Update extraction selectors if site changes

### Performance Tuning
- Adjust worker counts based on system performance
- Optimize batch sizes for your use case
- Fine-tune timeout and retry parameters
- Consider hardware upgrades for large-scale extraction

For additional support, refer to the technical specifications in the `specs/` directory or check the detailed mode documentation in `modes/`.