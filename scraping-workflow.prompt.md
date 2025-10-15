---
mode: agent
description: 'Darwin.md product scraping workflow with multi-agent coordination'
---

# Darwin.md Scraping Workflow - Agentic Orchestration

## Workflow Overview

This agentic workflow orchestrates the complete Darwin.md product scraping process using multi-agent coordination, adaptive strategies, and continuous learning.

**Execution Pattern**: Context → Plan → Route → Execute → Evaluate → Learn

## Phase 1: Context Loading 📚

### Memory & Pattern Analysis

🚨 **VALIDATION GATE**: Verify memory and pattern files accessibility

- [ ] Load historical success rates from [success rates](.memory.md)
- [ ] Analyze previous extraction patterns from [darwin patterns](./docs/darwin-patterns.md)
- [ ] Review site structure changes and selector updates
- [ ] Load category-specific performance metrics
- [ ] Initialize adaptive thresholds based on historical data

**Context Checklist:**
```markdown
- [ ] Memory file loaded successfully
- [ ] Pattern recognition data available
- [ ] Site structure baseline established
- [ ] Performance benchmarks loaded
- [ ] Error pattern history analyzed
```

### Environment Assessment

🚨 **VALIDATION GATE**: Environment configuration validation

- [ ] Verify API keys (OpenAI/Gemini) availability
- [ ] Check network connectivity to Darwin.md
- [ ] Validate scraper dependencies and versions
- [ ] Test anti-bot bypass capabilities
- [ ] Confirm rate limiting configuration

**Environment Status:**
```markdown
- [ ] ✅ API Provider: [OpenAI/Gemini] configured
- [ ] ✅ Darwin.md accessibility confirmed
- [ ] ✅ Cloudflare bypass operational
- [ ] ✅ Rate limiting: 2 req/sec configured
- [ ] ✅ User agent rotation enabled
```

## Phase 2: Planning Phase 🎯

### Strategic Analysis

🚨 **VALIDATION GATE**: Target and resource feasibility check

**Input Parameters:**
- Target product count: `{target_products}`
- Preferred categories: `{categories}`
- Quality threshold: `{quality_threshold}`
- Time constraints: `{max_execution_time}`

**Planning Decisions:**
- [ ] Analyze target scope vs. available resources
- [ ] Select optimal extraction strategy (parallel/sequential)
- [ ] Determine worker thread allocation
- [ ] Calculate estimated completion time
- [ ] Identify potential bottlenecks and risks

### URL Discovery Strategy

🚨 **VALIDATION GATE**: Sitemap accessibility and parsing capability

- [ ] Access Darwin.md sitemap.xml
- [ ] Parse and categorize product URLs
- [ ] Filter URLs based on target criteria
- [ ] Validate URL accessibility (sample check)
- [ ] Estimate extraction complexity per category

**URL Analysis Results:**
```markdown
- [ ] Total discoverable products: {total_urls}
- [ ] Target-filtered products: {filtered_urls}
- [ ] Category distribution analyzed
- [ ] URL accessibility: {accessibility_rate}%
- [ ] Complexity score: {complexity_score}/10
```

### Resource Optimization

- [ ] Calculate optimal worker count based on:
  - Historical performance for similar batch sizes
  - Current system resources (CPU, memory)
  - Network bandwidth and latency
  - Darwin.md server response patterns

**Resource Plan:**
```markdown
- [ ] Recommended workers: {optimal_workers}
- [ ] Batch size: {batch_size}
- [ ] Memory allocation: {memory_mb} MB
- [ ] Estimated duration: {estimated_minutes} minutes
- [ ] Success rate prediction: {predicted_success_rate}%
```

## Phase 3: Meta-Controller Phase 🎛️

### Strategy Routing Decision

🚨 **VALIDATION GATE**: Plan validation and optimization approval

**Decision Matrix:**
- [ ] **APPROVE**: Plan is optimal and risk-acceptable
  - Success rate prediction > 80%
  - Resource usage within limits
  - Timeline meets requirements
  
- [ ] **OPTIMIZE**: Plan needs adjustments
  - Reduce worker count if high risk detected
  - Adjust batch size for stability
  - Implement additional error handling
  
- [ ] **ABORT**: Plan requires complete revision
  - Success rate prediction < 60%
  - Resource constraints exceeded
  - Critical risks identified

### Adaptive Parameter Adjustment

🚨 **VALIDATION GATE**: Parameter optimization based on conditions

**Adjustment Triggers:**
- [ ] **High Error Rate History**: Reduce parallelism
- [ ] **Site Performance Issues**: Increase delays
- [ ] **Memory Constraints**: Smaller batch sizes
- [ ] **Time Pressure**: Increase workers (with caution)

**Final Parameters:**
```markdown
- [ ] Workers: {final_workers} (adjusted from {initial_workers})
- [ ] Delays: {request_delay}s between requests
- [ ] Batch size: {final_batch_size}
- [ ] Timeout: {request_timeout}s per request
- [ ] Retry attempts: {max_retries}
```

### Risk Mitigation Setup

- [ ] Configure circuit breakers for error rate spikes
- [ ] Setup adaptive throttling for rate limiting
- [ ] Initialize fallback selectors for parsing failures
- [ ] Prepare graceful degradation strategies

## Phase 4: Execution Phase ⚡

### Pre-Execution Setup

🚨 **VALIDATION GATE**: All systems ready for extraction

- [ ] Initialize worker thread pool
- [ ] Setup request session with proper headers
- [ ] Configure logging and monitoring systems
- [ ] Prepare output file structures (JSON/CSV)
- [ ] Start performance metric collection

### Real-Time Extraction Monitoring

🚨 **VALIDATION GATE**: Continuous performance monitoring during execution

**Performance Metrics:**
```markdown
- [ ] Success Rate: {current_success_rate}% (target: >70%)
- [ ] Processing Speed: {products_per_minute}/min
- [ ] Error Rate: {error_rate}% (threshold: <30%)
- [ ] Memory Usage: {memory_usage}MB/{memory_limit}MB
- [ ] Response Time: {avg_response_time}s (target: <5s)
```

**Circuit Breaker Status:**
- [ ] Network errors: {network_error_count}/{network_error_threshold}
- [ ] Parsing failures: {parsing_error_count}/{parsing_error_threshold}
- [ ] Rate limiting hits: {rate_limit_count}/{rate_limit_threshold}

### Adaptive Response Handling

🚨 **VALIDATION GATE**: Error handling and recovery mechanisms

**Error Response Strategies:**
- [ ] **Network Timeouts**: Exponential backoff retry
- [ ] **403/429 Responses**: Implement cooling period
- [ ] **Parsing Failures**: Switch to fallback selectors
- [ ] **IP Blocking**: Alert and graceful shutdown

### Data Quality Validation

- [ ] Real-time field completeness checking
- [ ] Format consistency validation
- [ ] Duplicate detection and handling
- [ ] Price format normalization (MDL currency)

## Phase 5: Quality Evaluation Phase ⚖️

### Performance Assessment

🚨 **VALIDATION GATE**: Extraction results meet minimum standards

**Quantitative Metrics:**
```markdown
- [ ] Products extracted: {extracted_count}/{target_count}
- [ ] Success rate: {final_success_rate}% (min: 70%)
- [ ] Processing time: {total_time} minutes
- [ ] Average time per product: {time_per_product}s
- [ ] Error distribution analyzed
```

**Quality Analysis:**
```markdown
- [ ] Required fields completeness: {required_completeness}%
- [ ] Optional fields completeness: {optional_completeness}%
- [ ] Data format consistency: {format_consistency}%
- [ ] Price validation: {price_validation}% valid
- [ ] Image URL accessibility: {image_accessibility}%
```

### Data Integrity Validation

🚨 **VALIDATION GATE**: Data quality meets acceptability thresholds

- [ ] **PASS**: Results exceed quality thresholds
  - Success rate ≥ 80%
  - Data completeness ≥ 85%
  - Format consistency ≥ 90%
  
- [ ] **CONDITIONAL**: Results usable with limitations
  - Success rate 60-79%
  - Data completeness 70-84%
  - Document known limitations
  
- [ ] **FAIL**: Results require re-extraction
  - Success rate < 60%
  - Data completeness < 70%
  - Critical data integrity issues

### Output File Generation

- [ ] Generate structured JSON output
- [ ] Create CSV export for analysis
- [ ] Produce execution summary report
- [ ] Archive logs and debug information

## Phase 6: Learning Phase 🧠

### Performance Pattern Analysis

🚨 **VALIDATION GATE**: Learning data extraction and pattern identification

**Pattern Recognition:**
- [ ] Identify successful extraction strategies by category
- [ ] Analyze optimal worker counts for different batch sizes
- [ ] Document error patterns and recovery success rates
- [ ] Track performance variations by time of day

**Success Factor Analysis:**
```markdown
- [ ] Best performing categories: {top_categories}
- [ ] Optimal worker count: {optimal_workers_learned}
- [ ] Most effective selectors: {successful_selectors}
- [ ] Peak performance time: {best_time_window}
- [ ] Error recovery patterns: {recovery_strategies}
```

### Memory Updates

🚨 **VALIDATION GATE**: Learning data persistence and validation

- [ ] Update [success rates](.memory.md) with new metrics
- [ ] Enhance [darwin patterns](./docs/darwin-patterns.md) with discoveries
- [ ] Record new selector patterns and effectiveness
- [ ] Update category-specific optimization parameters
- [ ] Archive extraction session for future reference

**Memory Structure Updates:**
```markdown
- [ ] Last run summary persisted
- [ ] Performance benchmarks updated
- [ ] Error pattern library enhanced
- [ ] Optimization insights recorded
- [ ] Prediction models refined
```

### Adaptive Threshold Adjustment

- [ ] Adjust quality thresholds based on achievable performance
- [ ] Update error rate tolerances for different scenarios
- [ ] Refine worker count recommendations
- [ ] Optimize timing parameters for future runs

### Recommendations Generation

🚨 **VALIDATION GATE**: Actionable insights for future improvements

**Strategy Recommendations:**
```markdown
- [ ] Optimal batch size for similar targets: {recommended_batch}
- [ ] Best extraction time window: {recommended_schedule}
- [ ] Selector updates needed: {selector_updates}
- [ ] Infrastructure improvements: {infra_recommendations}
- [ ] Quality enhancement opportunities: {quality_improvements}
```

## Workflow Completion Summary

### Final Status Report

```markdown
## Extraction Session Summary

**Execution Details:**
- Target: {target_products} products
- Achieved: {final_extracted} products ({achievement_rate}%)
- Duration: {total_execution_time} minutes
- Success Rate: {final_success_rate}%

**Quality Metrics:**
- Data Completeness: {final_completeness}%
- Format Consistency: {final_consistency}%
- Overall Quality Score: {quality_score}/100

**Verdict:** {final_verdict} ✅/⚠️/❌

**Output Files:**
- JSON: {json_output_file}
- CSV: {csv_output_file}
- Report: {summary_report_file}
```

### Next Steps

- [ ] Review quality assessment and recommendations
- [ ] Apply learned optimizations to future extractions
- [ ] Update documentation with new insights
- [ ] Schedule maintenance if selector updates needed
- [ ] Archive session data for trend analysis

---

**Workflow Status**: `{workflow_status}` | **Last Updated**: `{timestamp}` | **Version**: `1.0.0`