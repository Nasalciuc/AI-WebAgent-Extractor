# Darwin Agent - Workflow Execution

**Agent Mission**: Extract product data from Darwin.md using agentic multi-mode strategy

## Current Execution Context

- **Target Products**: {target_products}
- **Current Mode**: {current_mode}
- **Previous Results**: {previous_results}

## Workflow Overview

This workflow implements GitHub's Agentic Primitives framework with four distinct modes:

### 1. Planner Mode
- **Objective**: Analyze target and develop extraction strategy
- **Actions**: 
  - Discover all available product URLs
  - Analyze URL patterns and categories
  - Estimate resource requirements
  - Plan extraction approach

### 2. Meta-Controller Mode
- **Objective**: Evaluate plan and make strategic adjustments
- **Actions**:
  - Review planning results
  - Assess resource constraints
  - Make strategic decisions
  - Approve or modify execution parameters

### 3. Executor Mode
- **Objective**: Execute the extraction plan
- **Actions**:
  - Run batch extraction with approved parameters
  - Monitor progress and performance
  - Handle errors and retries
  - Generate output files

### 4. Judge Mode
- **Objective**: Evaluate results and provide assessment
- **Actions**:
  - Analyze extraction metrics
  - Assess data quality
  - Generate recommendations
  - Approve results for use

## Success Criteria

- **Completeness**: Successfully extract data for target number of products
- **Quality**: Maintain data quality standards (>80% field completeness)
- **Efficiency**: Achieve reasonable success rate (>70%)
- **Reliability**: Handle errors gracefully and provide clear feedback

## Adaptive Behavior

The agent will adapt its strategy based on:
- Historical performance patterns
- Real-time extraction results
- Resource availability
- Quality metrics

## Output Expectations

- Structured product data (JSON/CSV)
- Performance metrics and analysis
- Quality assessment and recommendations
- Actionable insights for future runs