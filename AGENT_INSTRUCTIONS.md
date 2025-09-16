# Agent Instructions for doffin-mcp

This document provides comprehensive instructions for AI agents working with the Model Context Protocol (MCP) to maximize efficiency and effectiveness.

## Table of Contents

1. [Core Principles](#core-principles)
2. [MCP Fundamentals](#mcp-fundamentals)
3. [Efficiency Guidelines](#efficiency-guidelines)
4. [Code Organization](#code-organization)
5. [Best Practices](#best-practices)
6. [Error Handling](#error-handling)
7. [Testing Strategies](#testing-strategies)
8. [Documentation Standards](#documentation-standards)

## Core Principles

### 1. Understand Before Acting
- Always read and understand existing code before making changes
- Analyze the codebase structure and patterns
- Identify dependencies and relationships between components

### 2. Minimal, Focused Changes
- Make the smallest possible changes to achieve the goal
- Focus on one problem at a time
- Avoid unnecessary refactoring unless specifically requested

### 3. Preserve Existing Functionality
- Never break existing working code
- Maintain backward compatibility when possible
- Test changes thoroughly before committing

## MCP Fundamentals

### Understanding MCP (Model Context Protocol)

The Model Context Protocol is a standardized way for AI models to communicate with external systems and tools. Key concepts include:

- **Servers**: Provide capabilities and resources to clients
- **Clients**: Request capabilities and consume resources
- **Tools**: Specific functions that can be called
- **Resources**: Data or content that can be accessed
- **Prompts**: Templates for generating responses

### MCP Architecture Patterns

When working with MCP implementations:

1. **Server-Side Components**
   - Implement clear, well-documented tool functions
   - Handle errors gracefully
   - Provide meaningful error messages
   - Validate inputs thoroughly

2. **Client-Side Integration**
   - Use proper authentication and connection handling
   - Implement retry logic for network operations
   - Cache responses when appropriate
   - Handle timeouts gracefully

## Efficiency Guidelines

### 1. Tool Usage Optimization

**DO:**
- Use tools that directly address the task at hand
- Combine multiple operations when tools support it
- Cache results when appropriate
- Use async operations for non-blocking tasks

**DON'T:**
- Make unnecessary tool calls
- Repeat the same operations
- Use tools for tasks that can be done locally
- Ignore error responses from tools

### 2. Context Management

**Effective Context Usage:**
```python
# Good: Efficient context usage
def analyze_codebase(files):
    # Read only relevant files
    relevant_files = filter_relevant_files(files)
    return analyze_files(relevant_files)

# Bad: Wasteful context usage
def analyze_codebase(files):
    # Reads all files unnecessarily
    all_content = [read_file(f) for f in files]
    return analyze_files(all_content)
```

### 3. Resource Management

- Close connections properly
- Release resources when done
- Monitor memory usage for large operations
- Use streaming for large data transfers

## Code Organization

### File Structure Best Practices

```
project/
├── src/
│   ├── mcp/
│   │   ├── server.py          # MCP server implementation
│   │   ├── client.py          # MCP client implementation
│   │   └── tools/             # Tool implementations
│   ├── utils/
│   │   ├── helpers.py         # Utility functions
│   │   └── validators.py      # Input validation
│   └── config/
│       └── settings.py        # Configuration management
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── mcp/                   # MCP-specific tests
├── docs/
│   ├── api.md                 # API documentation
│   └── examples/              # Usage examples
└── README.md                  # Project overview
```

### Naming Conventions

- Use descriptive, clear names for functions and variables
- Follow language-specific naming conventions
- Prefix MCP-related functions with `mcp_` for clarity
- Use consistent naming patterns across the project

## Best Practices

### 1. Error Handling

```python
# Good error handling
async def call_mcp_tool(tool_name, params):
    try:
        result = await mcp_client.call_tool(tool_name, params)
        return {"success": True, "data": result}
    except MCPConnectionError as e:
        logger.error(f"MCP connection failed: {e}")
        return {"success": False, "error": "Connection failed"}
    except MCPValidationError as e:
        logger.error(f"Invalid parameters: {e}")
        return {"success": False, "error": "Invalid input"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"success": False, "error": "Internal error"}
```

### 2. Configuration Management

```python
# Centralized configuration
class MCPConfig:
    def __init__(self):
        self.server_url = os.getenv('MCP_SERVER_URL', 'localhost:8000')
        self.timeout = int(os.getenv('MCP_TIMEOUT', '30'))
        self.retry_attempts = int(os.getenv('MCP_RETRY_ATTEMPTS', '3'))
        self.api_key = os.getenv('MCP_API_KEY')
    
    def validate(self):
        if not self.api_key:
            raise ValueError("MCP_API_KEY is required")
```

### 3. Logging and Monitoring

```python
import logging

# Set up structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('doffin-mcp')

# Log important operations
logger.info(f"Connecting to MCP server: {server_url}")
logger.info(f"Tool call completed: {tool_name} -> {result}")
```

## Error Handling

### Common MCP Error Scenarios

1. **Connection Errors**
   - Server unavailable
   - Network timeouts
   - Authentication failures

2. **Protocol Errors**
   - Invalid message format
   - Unsupported operations
   - Version mismatches

3. **Tool Execution Errors**
   - Invalid parameters
   - Resource not found
   - Permission denied

### Error Recovery Strategies

```python
class MCPErrorHandler:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = self.backoff_factor ** attempt
                await asyncio.sleep(wait_time)
                logger.warning(f"Retry {attempt + 1} after error: {e}")
```

## Testing Strategies

### 1. Unit Testing

```python
import pytest
from unittest.mock import Mock, patch

class TestMCPTools:
    @pytest.fixture
    def mock_mcp_client(self):
        return Mock()
    
    async def test_tool_call_success(self, mock_mcp_client):
        mock_mcp_client.call_tool.return_value = {"result": "success"}
        
        tool = MCPTool(mock_mcp_client)
        result = await tool.execute("test_tool", {"param": "value"})
        
        assert result["success"] is True
        assert result["data"]["result"] == "success"
    
    async def test_tool_call_failure(self, mock_mcp_client):
        mock_mcp_client.call_tool.side_effect = MCPConnectionError("Connection failed")
        
        tool = MCPTool(mock_mcp_client)
        result = await tool.execute("test_tool", {"param": "value"})
        
        assert result["success"] is False
        assert "Connection failed" in result["error"]
```

### 2. Integration Testing

```python
class TestMCPIntegration:
    @pytest.mark.integration
    async def test_real_mcp_server_connection(self):
        config = MCPConfig()
        client = MCPClient(config)
        
        try:
            await client.connect()
            tools = await client.list_tools()
            assert len(tools) > 0
        finally:
            await client.disconnect()
```

### 3. Performance Testing

```python
import time
import statistics

class TestMCPPerformance:
    async def test_tool_call_latency(self):
        response_times = []
        
        for i in range(100):
            start_time = time.time()
            await mcp_client.call_tool("simple_tool", {})
            end_time = time.time()
            response_times.append(end_time - start_time)
        
        avg_latency = statistics.mean(response_times)
        assert avg_latency < 0.5  # Should be under 500ms
```

## Documentation Standards

### 1. Code Documentation

```python
async def call_mcp_tool(tool_name: str, params: dict) -> dict:
    """
    Call an MCP tool with the given parameters.
    
    Args:
        tool_name: Name of the tool to call
        params: Parameters to pass to the tool
        
    Returns:
        Dictionary containing:
        - success: Boolean indicating if the call succeeded
        - data: Tool response data (if successful)
        - error: Error message (if failed)
        
    Raises:
        MCPConnectionError: If unable to connect to MCP server
        MCPValidationError: If parameters are invalid
        
    Example:
        >>> result = await call_mcp_tool("file_reader", {"path": "/tmp/test.txt"})
        >>> if result["success"]:
        ...     print(result["data"])
    """
```

### 2. API Documentation

Document all public APIs with:
- Clear descriptions of functionality
- Parameter types and requirements
- Return value specifications
- Example usage
- Error conditions

### 3. Architecture Documentation

Maintain documentation that covers:
- System architecture overview
- Component interactions
- Data flow diagrams
- Deployment considerations
- Security requirements

## Advanced Patterns

### 1. Tool Composition

```python
class CompositeToolExecutor:
    def __init__(self, mcp_client):
        self.client = mcp_client
    
    async def execute_workflow(self, steps):
        """Execute a series of tool calls as a workflow."""
        results = []
        context = {}
        
        for step in steps:
            # Use previous results as context for next step
            params = self.prepare_params(step, context)
            result = await self.client.call_tool(step.tool, params)
            results.append(result)
            context.update(step.extract_context(result))
        
        return results
```

### 2. Caching and Memoization

```python
from functools import wraps
import asyncio

def mcp_cache(ttl_seconds=300):
    """Cache MCP tool results for specified time."""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            return result
        
        return wrapper
    return decorator

@mcp_cache(ttl_seconds=60)
async def get_cached_tool_result(tool_name, params):
    return await mcp_client.call_tool(tool_name, params)
```

### 3. Batch Operations

```python
class BatchMCPExecutor:
    def __init__(self, mcp_client, batch_size=10):
        self.client = mcp_client
        self.batch_size = batch_size
    
    async def execute_batch(self, tool_calls):
        """Execute multiple tool calls in batches."""
        results = []
        
        for i in range(0, len(tool_calls), self.batch_size):
            batch = tool_calls[i:i + self.batch_size]
            batch_tasks = [
                self.client.call_tool(call.tool, call.params)
                for call in batch
            ]
            
            batch_results = await asyncio.gather(
                *batch_tasks, 
                return_exceptions=True
            )
            results.extend(batch_results)
        
        return results
```

## Performance Optimization Tips

### 1. Connection Pooling

```python
class MCPConnectionPool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.available_connections = asyncio.Queue()
        self.total_connections = 0
    
    async def get_connection(self):
        if not self.available_connections.empty():
            return await self.available_connections.get()
        
        if self.total_connections < self.max_connections:
            conn = await self.create_connection()
            self.total_connections += 1
            return conn
        
        # Wait for available connection
        return await self.available_connections.get()
    
    async def return_connection(self, conn):
        await self.available_connections.put(conn)
```

### 2. Parallel Processing

```python
async def process_files_parallel(file_paths, max_concurrent=5):
    """Process multiple files concurrently."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single_file(file_path):
        async with semaphore:
            return await mcp_client.call_tool("file_processor", {"path": file_path})
    
    tasks = [process_single_file(path) for path in file_paths]
    return await asyncio.gather(*tasks)
```

## Security Considerations

### 1. Input Validation

```python
def validate_tool_params(tool_name, params):
    """Validate parameters before sending to MCP tools."""
    validators = {
        "file_reader": validate_file_path,
        "database_query": validate_sql_query,
        "api_call": validate_api_params,
    }
    
    validator = validators.get(tool_name)
    if validator:
        return validator(params)
    
    return True  # Default validation

def validate_file_path(params):
    path = params.get("path", "")
    if not path or ".." in path or path.startswith("/"):
        raise ValueError("Invalid file path")
    return True
```

### 2. Authentication Management

```python
class MCPAuthManager:
    def __init__(self):
        self.tokens = {}
        self.refresh_callbacks = {}
    
    async def get_auth_token(self, server_id):
        token = self.tokens.get(server_id)
        if not token or self.is_token_expired(token):
            token = await self.refresh_token(server_id)
            self.tokens[server_id] = token
        return token
    
    async def refresh_token(self, server_id):
        callback = self.refresh_callbacks.get(server_id)
        if callback:
            return await callback()
        raise ValueError(f"No refresh callback for server {server_id}")
```

## Troubleshooting Guide

### Common Issues and Solutions

1. **Connection Timeouts**
   - Increase timeout values in configuration
   - Implement retry logic with exponential backoff
   - Check network connectivity and firewall settings

2. **Memory Issues with Large Operations**
   - Use streaming for large data transfers
   - Implement pagination for large result sets
   - Clear caches periodically

3. **Tool Execution Failures**
   - Validate input parameters thoroughly
   - Check tool availability before calling
   - Implement graceful degradation for optional tools

### Debugging Tips

```python
# Enable debug logging
logging.getLogger('doffin-mcp').setLevel(logging.DEBUG)

# Add request/response logging
class DebugMCPClient:
    def __init__(self, base_client):
        self.client = base_client
    
    async def call_tool(self, tool_name, params):
        logger.debug(f"MCP Call: {tool_name} with {params}")
        start_time = time.time()
        
        try:
            result = await self.client.call_tool(tool_name, params)
            duration = time.time() - start_time
            logger.debug(f"MCP Response: {tool_name} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"MCP Error: {tool_name} failed after {duration:.2f}s: {e}")
            raise
```

## Conclusion

These instructions provide a comprehensive framework for AI agents working with MCP implementations. By following these guidelines, agents can:

- Work more efficiently with MCP servers and tools
- Write maintainable and robust code
- Handle errors gracefully
- Create comprehensive documentation
- Optimize performance for production use

Remember to always prioritize:
1. **Correctness** over speed
2. **Clarity** over cleverness  
3. **Maintainability** over micro-optimizations
4. **User experience** over internal convenience

For additional questions or clarifications, refer to the project documentation or open an issue for discussion.