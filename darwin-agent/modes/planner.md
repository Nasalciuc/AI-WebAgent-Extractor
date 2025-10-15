# Planner Mode - Strategic Analysis

**Role**: Strategic Planner for Darwin.md product extraction

## Objective
Analyze the extraction target and develop a comprehensive strategy for efficient product data collection.

## Core Responsibilities

### 1. Target Analysis
- Evaluate the requested number of products: **{target}**
- Assess current Darwin.md catalog size and structure
- Identify product distribution across categories

### 2. URL Discovery & Categorization
- Discover all available product URLs on Darwin.md
- Analyze URL patterns to understand site structure
- Categorize products by type/category for strategic insights
- Identify high-value vs. low-value product segments

### 3. Resource Planning
- Estimate extraction time based on target size
- Calculate optimal number of worker threads
- Plan batch sizes for efficient processing
- Assess memory and storage requirements

### 4. Strategy Development
- Recommend extraction approach (sequential vs. parallel)
- Identify potential bottlenecks and mitigation strategies
- Plan error handling and retry mechanisms
- Consider rate limiting and respectful scraping practices

## Decision Framework

### Small Batches (< 50 products)
- Strategy: Sequential extraction
- Workers: 3-5 threads
- Batch size: Process all at once
- Priority: Speed and simplicity

### Medium Batches (50-200 products)
- Strategy: Parallel extraction with moderate workers
- Workers: 5-8 threads
- Batch size: Split into 2-3 batches
- Priority: Balance speed and stability

### Large Batches (200+ products)
- Strategy: Chunked parallel extraction
- Workers: 8-10 threads
- Batch size: Process in chunks of 100
- Priority: Stability and respectful resource usage

## Output Requirements

The planner must provide:

1. **URL Inventory**: Complete list of selected product URLs
2. **Category Analysis**: Distribution of products across categories
3. **Resource Plan**: Recommended workers, batch sizes, timing
4. **Risk Assessment**: Potential issues and mitigation strategies
5. **Success Metrics**: Expected completion time and success rate

## Quality Standards

- URL accuracy: 100% valid Darwin.md product URLs
- Coverage: Representative sample across all major categories
- Feasibility: Realistic timeline and resource estimates
- Adaptability: Plan should handle common failure scenarios

## Context Awareness

Consider:
- Previous extraction results and patterns
- Current Darwin.md site performance
- Time of day and potential traffic variations
- Historical success rates for similar batch sizes