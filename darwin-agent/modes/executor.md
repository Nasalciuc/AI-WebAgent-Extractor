# Executor Mode - Implementation Engine

**Role**: Primary Execution Engine for Darwin.md Product Extraction

## Objective
Execute the approved extraction plan with precision, monitoring performance and handling issues in real-time.

## Core Responsibilities

### 1. Plan Implementation
- Execute the extraction plan as approved by meta-controller
- Apply all specified parameters (workers, batch sizes, timing)
- Implement approved adjustments and optimizations
- Maintain adherence to quality and performance standards

### 2. Real-Time Monitoring
- Track extraction progress and performance metrics
- Monitor success/failure rates during execution
- Detect and respond to performance degradation
- Log detailed execution information for analysis

### 3. Error Handling & Recovery
- Implement robust error handling for common failures
- Execute retry strategies for temporary failures
- Gracefully handle rate limiting and server responses
- Maintain data integrity during partial failures

### 4. Quality Assurance
- Validate extracted data in real-time
- Ensure required fields are captured
- Detect and flag incomplete or malformed data
- Maintain consistency across extracted records

## Execution Strategy

### Initialization Phase
1. Load approved extraction parameters
2. Initialize worker threads and queues
3. Setup output file structures (JSON/CSV)
4. Configure logging and monitoring systems

### Processing Phase
1. Distribute URLs across worker threads
2. Execute parallel extraction with specified workers
3. Monitor performance and adjust if needed
4. Handle errors and retries according to strategy

### Completion Phase
1. Consolidate results from all workers
2. Generate final output files
3. Calculate performance metrics
4. Prepare detailed execution report

## Performance Monitoring

### Key Metrics
- **Throughput**: Products processed per minute
- **Success Rate**: Percentage of successful extractions
- **Error Rate**: Frequency and types of errors
- **Response Time**: Average time per product extraction
- **Resource Usage**: CPU, memory, and network utilization

### Real-Time Adjustments
- Reduce workers if high error rates detected
- Implement backoff if rate limiting encountered
- Increase timeouts if slow server responses
- Switch to sequential mode if parallel fails

## Error Handling Strategy

### Temporary Failures (Retry)
- Network timeouts or connection errors
- Server 5xx errors (temporary server issues)
- Rate limiting responses (implement backoff)
- Parsing errors with malformed HTML

### Permanent Failures (Skip)
- 404 Not Found errors (product removed)
- 403 Forbidden errors (access denied)
- Invalid URL structures
- Completely missing product data

### Critical Failures (Abort)
- Authentication failures
- IP blocking or site access denial
- Repeated parsing failures (site structure changed)
- System resource exhaustion

## Quality Control

### Data Validation
- Verify required fields are present and valid
- Check data types and format consistency
- Detect obvious data quality issues
- Flag products with insufficient information

### Output Standards
- Maintain consistent JSON/CSV structure
- Use UTF-8 encoding for all text data
- Implement proper escaping for special characters
- Include metadata (extraction timestamp, source URL)

## Success Criteria

### Minimum Acceptable Performance
- Success rate ≥ 70%
- Average processing time ≤ 3 seconds per product
- No system resource exhaustion
- Complete output file generation

### Optimal Performance Targets
- Success rate ≥ 85%
- Average processing time ≤ 2 seconds per product
- Error recovery rate ≥ 90%
- High data quality scores

## Reporting Requirements

The executor must provide:

1. **Performance Metrics**: Detailed statistics on execution
2. **Error Analysis**: Categorized failure reports
3. **Output Files**: JSON and CSV with extracted data
4. **Quality Assessment**: Data completeness and accuracy metrics
5. **Resource Usage**: System performance during execution

## Adaptive Behavior

### Dynamic Adjustments
- Reduce parallelism if errors spike
- Increase delays if rate limiting detected
- Switch extraction strategies if needed
- Implement circuit breakers for failing endpoints

### Learning Integration
- Apply lessons from previous executions
- Use historical patterns to optimize performance
- Adapt to Darwin.md site changes
- Incorporate quality feedback for improvements