# MCP Best Practices

This document outlines specific best practices for working with the Model Context Protocol (MCP) in the doffin-mcp project.

## Table of Contents

1. [MCP Protocol Overview](#mcp-protocol-overview)
2. [Server Implementation](#server-implementation)
3. [Client Implementation](#client-implementation)
4. [Tool Development](#tool-development)
5. [Resource Management](#resource-management)
6. [Security Guidelines](#security-guidelines)
7. [Performance Optimization](#performance-optimization)
8. [Testing MCP Components](#testing-mcp-components)

## MCP Protocol Overview

The Model Context Protocol enables standardized communication between AI models and external systems. Key components include:

### Core Concepts

- **Servers**: Expose capabilities through tools and resources
- **Clients**: Consume server capabilities 
- **Tools**: Executable functions with defined inputs/outputs
- **Resources**: Accessible data or content
- **Prompts**: Template-based response generation

### Message Types

```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {
      "param1": "value1"
    }
  }
}
```

## Server Implementation

### Basic Server Structure

```python
from mcp import Server, Tool, Resource
import asyncio

class DoffinMCPServer:
    def __init__(self):
        self.server = Server("doffin-mcp")
        self.setup_tools()
        self.setup_resources()
    
    def setup_tools(self):
        """Register all available tools."""
        self.server.add_tool(
            Tool(
                name="process_data",
                description="Process data efficiently",
                handler=self.handle_process_data,
                input_schema={
                    "type": "object",
                    "properties": {
                        "data": {"type": "string"},
                        "format": {"type": "string", "enum": ["json", "csv", "xml"]}
                    },
                    "required": ["data"]
                }
            )
        )
    
    async def handle_process_data(self, data: str, format: str = "json"):
        """Handle data processing requests."""
        try:
            # Validate input
            if not data.strip():
                raise ValueError("Data cannot be empty")
            
            # Process based on format
            result = await self.process_by_format(data, format)
            
            return {
                "success": True,
                "processed_data": result,
                "format": format
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_by_format(self, data: str, format: str):
        """Process data according to specified format."""
        processors = {
            "json": self.process_json,
            "csv": self.process_csv,
            "xml": self.process_xml
        }
        
        processor = processors.get(format, self.process_json)
        return await processor(data)
```

### Tool Registration Best Practices

```python
def register_tools_efficiently(server: Server):
    """Register tools with proper error handling and validation."""
    
    tools = [
        {
            "name": "file_operations",
            "handler": handle_file_operations,
            "schema": FILE_OPERATION_SCHEMA,
            "description": "Perform file system operations safely"
        },
        {
            "name": "data_analysis",
            "handler": handle_data_analysis,
            "schema": DATA_ANALYSIS_SCHEMA,
            "description": "Analyze data and generate insights"
        }
    ]
    
    for tool_config in tools:
        try:
            tool = Tool(
                name=tool_config["name"],
                description=tool_config["description"],
                handler=tool_config["handler"],
                input_schema=tool_config["schema"]
            )
            server.add_tool(tool)
            logger.info(f"Registered tool: {tool_config['name']}")
        except Exception as e:
            logger.error(f"Failed to register tool {tool_config['name']}: {e}")
```

## Client Implementation

### Robust Client Connection

```python
class DoffinMCPClient:
    def __init__(self, server_url: str, timeout: int = 30):
        self.server_url = server_url
        self.timeout = timeout
        self.client = None
        self.is_connected = False
    
    async def connect(self, retries: int = 3):
        """Connect to MCP server with retry logic."""
        for attempt in range(retries):
            try:
                self.client = MCPClient(self.server_url)
                await self.client.connect()
                self.is_connected = True
                logger.info(f"Connected to MCP server: {self.server_url}")
                return True
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to connect after {retries} attempts")
                    raise
    
    async def call_tool_safely(self, tool_name: str, params: dict):
        """Call a tool with comprehensive error handling."""
        if not self.is_connected:
            await self.connect()
        
        try:
            # Validate parameters
            self.validate_tool_params(tool_name, params)
            
            # Make the call
            result = await self.client.call_tool(tool_name, params)
            
            # Validate response
            self.validate_tool_response(result)
            
            return result
        except MCPTimeoutError:
            logger.error(f"Tool call timed out: {tool_name}")
            raise
        except MCPValidationError as e:
            logger.error(f"Validation error for tool {tool_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling tool {tool_name}: {e}")
            raise
    
    def validate_tool_params(self, tool_name: str, params: dict):
        """Validate parameters before sending to server."""
        if not isinstance(params, dict):
            raise MCPValidationError("Parameters must be a dictionary")
        
        # Tool-specific validation
        validators = {
            "file_operations": self.validate_file_params,
            "data_analysis": self.validate_data_params
        }
        
        validator = validators.get(tool_name)
        if validator:
            validator(params)
```

## Tool Development

### Tool Interface Standards

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MCPToolBase(ABC):
    """Base class for all MCP tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """Return JSON schema for input validation."""
        pass
    
    def validate_input(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters against schema."""
        from jsonschema import validate, ValidationError
        
        try:
            validate(instance=params, schema=self.get_input_schema())
            return True
        except ValidationError as e:
            raise MCPValidationError(f"Invalid input: {e.message}")

class FileReaderTool(MCPToolBase):
    """Tool for reading files safely."""
    
    def __init__(self):
        super().__init__(
            name="file_reader",
            description="Read file contents with safety checks"
        )
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read file and return contents."""
        file_path = params["path"]
        encoding = params.get("encoding", "utf-8")
        max_size = params.get("max_size", 1024 * 1024)  # 1MB default
        
        # Security checks
        if not self.is_safe_path(file_path):
            return {"success": False, "error": "Unsafe file path"}
        
        try:
            # Check file size
            if os.path.getsize(file_path) > max_size:
                return {"success": False, "error": "File too large"}
            
            # Read file
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "path": file_path,
                "size": len(content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return input schema for file reader."""
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "encoding": {"type": "string", "default": "utf-8"},
                "max_size": {"type": "integer", "minimum": 1}
            },
            "required": ["path"]
        }
    
    def is_safe_path(self, path: str) -> bool:
        """Check if file path is safe to access."""
        # Prevent directory traversal
        if ".." in path or path.startswith("/"):
            return False
        
        # Check against allowed directories
        allowed_dirs = ["/tmp", "/var/tmp", "./data", "./uploads"]
        return any(path.startswith(allowed) for allowed in allowed_dirs)
```

### Tool Composition Patterns

```python
class CompositeToolChain:
    """Chain multiple tools together for complex operations."""
    
    def __init__(self, client: DoffinMCPClient):
        self.client = client
    
    async def process_file_workflow(self, file_path: str):
        """Example workflow: read -> analyze -> summarize file."""
        try:
            # Step 1: Read file
            read_result = await self.client.call_tool_safely(
                "file_reader", 
                {"path": file_path}
            )
            
            if not read_result["success"]:
                return read_result
            
            # Step 2: Analyze content
            analysis_result = await self.client.call_tool_safely(
                "content_analyzer",
                {"content": read_result["content"]}
            )
            
            if not analysis_result["success"]:
                return analysis_result
            
            # Step 3: Generate summary
            summary_result = await self.client.call_tool_safely(
                "content_summarizer",
                {
                    "content": read_result["content"],
                    "analysis": analysis_result["analysis"]
                }
            )
            
            return {
                "success": True,
                "workflow_results": {
                    "file_info": read_result,
                    "analysis": analysis_result,
                    "summary": summary_result
                }
            }
        except Exception as e:
            return {"success": False, "error": f"Workflow failed: {e}"}
```

## Resource Management

### Resource Provider Implementation

```python
class DoffinResourceProvider:
    """Provide resources through MCP protocol."""
    
    def __init__(self):
        self.resources = {}
        self.setup_resources()
    
    def setup_resources(self):
        """Initialize available resources."""
        self.resources = {
            "documentation": DocumentationResource(),
            "examples": ExampleResource(),
            "schemas": SchemaResource()
        }
    
    async def get_resource(self, resource_id: str, params: Optional[Dict] = None):
        """Retrieve a resource by ID."""
        resource = self.resources.get(resource_id)
        if not resource:
            raise MCPResourceError(f"Resource not found: {resource_id}")
        
        try:
            return await resource.get_content(params or {})
        except Exception as e:
            raise MCPResourceError(f"Failed to get resource {resource_id}: {e}")

class DocumentationResource:
    """Provide access to documentation."""
    
    async def get_content(self, params: Dict[str, Any]):
        """Get documentation content."""
        section = params.get("section", "index")
        format_type = params.get("format", "markdown")
        
        content = await self.load_documentation(section, format_type)
        
        return {
            "content": content,
            "section": section,
            "format": format_type,
            "last_updated": self.get_last_updated(section)
        }
    
    async def load_documentation(self, section: str, format_type: str):
        """Load documentation from storage."""
        # Implementation depends on storage backend
        pass
```

## Security Guidelines

### Input Sanitization

```python
import re
from typing import Any, Dict

class MCPInputSanitizer:
    """Sanitize inputs for MCP tools."""
    
    @staticmethod
    def sanitize_file_path(path: str) -> str:
        """Sanitize file path to prevent directory traversal."""
        # Remove dangerous characters and patterns
        path = re.sub(r'[^\w\-_./]', '', path)
        path = re.sub(r'\.\.+', '.', path)
        
        # Ensure relative path
        if path.startswith('/'):
            path = path[1:]
        
        return path
    
    @staticmethod
    def sanitize_sql_query(query: str) -> str:
        """Basic SQL injection prevention."""
        dangerous_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*insert\s+into',
            r';\s*update\s+',
            r'union\s+select',
            r'--',
            r'/\*.*\*/'
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                raise MCPSecurityError(f"Potentially dangerous SQL pattern: {pattern}")
        
        return query
    
    @staticmethod
    def validate_json_input(data: Any, max_depth: int = 10) -> bool:
        """Validate JSON input to prevent attacks."""
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise MCPSecurityError("JSON depth limit exceeded")
            
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        check_depth(data)
        return True
```

### Authentication and Authorization

```python
class MCPAuthenticationManager:
    """Handle authentication for MCP operations."""
    
    def __init__(self):
        self.api_keys = {}
        self.permissions = {}
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key."""
        return api_key in self.api_keys
    
    def check_permission(self, api_key: str, tool_name: str) -> bool:
        """Check if API key has permission for tool."""
        user_permissions = self.permissions.get(api_key, set())
        return tool_name in user_permissions or "*" in user_permissions
    
    async def authenticate_request(self, headers: Dict[str, str], tool_name: str):
        """Authenticate incoming request."""
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise MCPAuthenticationError("Missing or invalid authorization header")
        
        api_key = auth_header[7:]  # Remove "Bearer " prefix
        
        if not self.validate_api_key(api_key):
            raise MCPAuthenticationError("Invalid API key")
        
        if not self.check_permission(api_key, tool_name):
            raise MCPAuthorizationError(f"Insufficient permissions for tool: {tool_name}")
        
        return api_key
```

## Performance Optimization

### Connection Pooling

```python
import asyncio
from typing import List

class MCPConnectionPool:
    """Manage a pool of MCP connections."""
    
    def __init__(self, server_url: str, min_connections: int = 2, max_connections: int = 10):
        self.server_url = server_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.available_connections = asyncio.Queue()
        self.total_connections = 0
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the connection pool."""
        for _ in range(self.min_connections):
            conn = await self.create_connection()
            await self.available_connections.put(conn)
    
    async def create_connection(self):
        """Create a new MCP connection."""
        client = MCPClient(self.server_url)
        await client.connect()
        self.total_connections += 1
        return client
    
    async def get_connection(self):
        """Get a connection from the pool."""
        try:
            # Try to get an available connection
            return self.available_connections.get_nowait()
        except asyncio.QueueEmpty:
            async with self.lock:
                if self.total_connections < self.max_connections:
                    return await self.create_connection()
                else:
                    # Wait for an available connection
                    return await self.available_connections.get()
    
    async def return_connection(self, connection):
        """Return a connection to the pool."""
        if connection.is_healthy():
            await self.available_connections.put(connection)
        else:
            # Connection is unhealthy, create a new one
            await connection.close()
            self.total_connections -= 1
            if self.total_connections < self.min_connections:
                new_conn = await self.create_connection()
                await self.available_connections.put(new_conn)
```

### Caching Strategies

```python
import time
from typing import Any, Optional
import hashlib

class MCPResultCache:
    """Cache MCP tool results for performance."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def generate_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Generate cache key from tool name and parameters."""
        content = f"{tool_name}:{str(sorted(params.items()))}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, tool_name: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached result if available and not expired."""
        key = self.generate_key(tool_name, params)
        
        if key in self.cache:
            result, timestamp, ttl = self.cache[key]
            if time.time() - timestamp < ttl:
                return result
            else:
                # Expired, remove from cache
                del self.cache[key]
        
        return None
    
    def set(self, tool_name: str, params: Dict[str, Any], result: Any, ttl: Optional[int] = None):
        """Cache a result."""
        key = self.generate_key(tool_name, params)
        ttl = ttl or self.default_ttl
        self.cache[key] = (result, time.time(), ttl)
    
    def clear_expired(self):
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp, ttl) in self.cache.items()
            if current_time - timestamp >= ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]

class CachedMCPClient:
    """MCP client with result caching."""
    
    def __init__(self, client: DoffinMCPClient, cache: MCPResultCache):
        self.client = client
        self.cache = cache
    
    async def call_tool_cached(self, tool_name: str, params: Dict[str, Any], use_cache: bool = True):
        """Call tool with caching support."""
        if use_cache:
            cached_result = self.cache.get(tool_name, params)
            if cached_result is not None:
                return cached_result
        
        result = await self.client.call_tool_safely(tool_name, params)
        
        if use_cache and result.get("success"):
            # Only cache successful results
            self.cache.set(tool_name, params, result)
        
        return result
```

## Testing MCP Components

### Unit Testing Tools

```python
import pytest
from unittest.mock import Mock, AsyncMock
import asyncio

class TestMCPTools:
    """Test suite for MCP tools."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock MCP client."""
        client = Mock()
        client.call_tool = AsyncMock()
        return client
    
    @pytest.fixture
    def file_reader_tool(self):
        """Create file reader tool for testing."""
        return FileReaderTool()
    
    async def test_file_reader_success(self, file_reader_tool, tmp_path):
        """Test successful file reading."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)
        
        # Test file reading
        result = await file_reader_tool.execute({"path": str(test_file)})
        
        assert result["success"] is True
        assert result["content"] == test_content
        assert result["path"] == str(test_file)
    
    async def test_file_reader_invalid_path(self, file_reader_tool):
        """Test file reader with invalid path."""
        result = await file_reader_tool.execute({"path": "../../../etc/passwd"})
        
        assert result["success"] is False
        assert "Unsafe file path" in result["error"]
    
    async def test_file_reader_nonexistent_file(self, file_reader_tool):
        """Test file reader with non-existent file."""
        result = await file_reader_tool.execute({"path": "/tmp/nonexistent.txt"})
        
        assert result["success"] is False
        assert "error" in result

class TestMCPClient:
    """Test suite for MCP client."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        client = DoffinMCPClient("http://test-server")
        # Mock the underlying connection
        client.client = Mock()
        client.is_connected = True
        return client
    
    async def test_successful_tool_call(self, client):
        """Test successful tool call."""
        expected_result = {"success": True, "data": "test_result"}
        client.client.call_tool = AsyncMock(return_value=expected_result)
        
        result = await client.call_tool_safely("test_tool", {"param": "value"})
        
        assert result == expected_result
        client.client.call_tool.assert_called_once_with("test_tool", {"param": "value"})
    
    async def test_tool_call_with_timeout(self, client):
        """Test tool call timeout handling."""
        client.client.call_tool = AsyncMock(side_effect=MCPTimeoutError("Timeout"))
        
        with pytest.raises(MCPTimeoutError):
            await client.call_tool_safely("test_tool", {"param": "value"})
```

### Integration Testing

```python
class TestMCPIntegration:
    """Integration tests for MCP components."""
    
    @pytest.mark.integration
    async def test_server_client_communication(self):
        """Test full server-client communication."""
        # Start test server
        server = DoffinMCPServer()
        server_task = asyncio.create_task(server.start())
        
        try:
            # Wait for server to start
            await asyncio.sleep(1)
            
            # Create client and connect
            client = DoffinMCPClient("http://localhost:8000")
            await client.connect()
            
            # Test tool call
            result = await client.call_tool_safely("process_data", {
                "data": '{"test": "value"}',
                "format": "json"
            })
            
            assert result["success"] is True
            assert "processed_data" in result
            
        finally:
            # Cleanup
            server_task.cancel()
            await client.disconnect()
    
    @pytest.mark.integration
    async def test_connection_pooling(self):
        """Test connection pool functionality."""
        pool = MCPConnectionPool("http://localhost:8000", min_connections=2, max_connections=5)
        await pool.initialize()
        
        # Test getting connections
        conn1 = await pool.get_connection()
        conn2 = await pool.get_connection()
        
        assert conn1 is not None
        assert conn2 is not None
        assert conn1 != conn2
        
        # Return connections
        await pool.return_connection(conn1)
        await pool.return_connection(conn2)
```

### Performance Testing

```python
import time
import statistics

class TestMCPPerformance:
    """Performance tests for MCP components."""
    
    async def test_tool_call_latency(self, client):
        """Test tool call latency."""
        latencies = []
        
        for _ in range(100):
            start_time = time.time()
            await client.call_tool_safely("simple_tool", {})
            end_time = time.time()
            latencies.append(end_time - start_time)
        
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        
        assert avg_latency < 0.1  # Average should be under 100ms
        assert p95_latency < 0.5   # 95th percentile under 500ms
    
    async def test_concurrent_tool_calls(self, client):
        """Test performance under concurrent load."""
        concurrent_calls = 50
        
        async def make_call():
            return await client.call_tool_safely("test_tool", {"data": "test"})
        
        start_time = time.time()
        tasks = [make_call() for _ in range(concurrent_calls)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        calls_per_second = concurrent_calls / total_time
        
        # All calls should succeed
        assert all(result["success"] for result in results)
        # Should handle at least 20 calls per second
        assert calls_per_second > 20
```

## Error Handling Patterns

### Comprehensive Error Recovery

```python
class MCPErrorRecovery:
    """Handle various MCP error scenarios."""
    
    def __init__(self, client: DoffinMCPClient):
        self.client = client
        self.retry_strategies = {
            MCPConnectionError: self.handle_connection_error,
            MCPTimeoutError: self.handle_timeout_error,
            MCPValidationError: self.handle_validation_error,
            MCPResourceError: self.handle_resource_error
        }
    
    async def execute_with_recovery(self, operation, *args, **kwargs):
        """Execute operation with automatic error recovery."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                strategy = self.retry_strategies.get(type(e))
                
                if strategy and attempt < max_retries - 1:
                    await strategy(e, attempt)
                    continue
                else:
                    # No recovery strategy or max retries reached
                    raise
    
    async def handle_connection_error(self, error: MCPConnectionError, attempt: int):
        """Handle connection errors."""
        wait_time = 2 ** attempt  # Exponential backoff
        logger.warning(f"Connection error on attempt {attempt + 1}, retrying in {wait_time}s")
        await asyncio.sleep(wait_time)
        
        # Try to reconnect
        try:
            await self.client.connect()
        except Exception as e:
            logger.error(f"Failed to reconnect: {e}")
    
    async def handle_timeout_error(self, error: MCPTimeoutError, attempt: int):
        """Handle timeout errors."""
        logger.warning(f"Timeout on attempt {attempt + 1}, retrying with longer timeout")
        # Increase timeout for retry
        self.client.timeout = min(self.client.timeout * 2, 120)
    
    async def handle_validation_error(self, error: MCPValidationError, attempt: int):
        """Handle validation errors."""
        # Validation errors usually don't benefit from retries
        logger.error(f"Validation error: {error}")
        raise error
    
    async def handle_resource_error(self, error: MCPResourceError, attempt: int):
        """Handle resource errors."""
        wait_time = 1 + attempt  # Linear backoff for resource errors
        logger.warning(f"Resource error on attempt {attempt + 1}, retrying in {wait_time}s")
        await asyncio.sleep(wait_time)
```

## Monitoring and Observability

### Metrics Collection

```python
import time
from collections import defaultdict, deque
from typing import Dict, Any

class MCPMetrics:
    """Collect and report MCP performance metrics."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.call_times = defaultdict(lambda: deque(maxlen=window_size))
        self.call_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.start_time = time.time()
    
    def record_call(self, tool_name: str, duration: float, success: bool):
        """Record a tool call."""
        self.call_times[tool_name].append(duration)
        self.call_counts[tool_name] += 1
        
        if not success:
            self.error_counts[tool_name] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        metrics = {
            "uptime": time.time() - self.start_time,
            "tools": {}
        }
        
        for tool_name in self.call_counts:
            times = list(self.call_times[tool_name])
            if times:
                metrics["tools"][tool_name] = {
                    "total_calls": self.call_counts[tool_name],
                    "total_errors": self.error_counts[tool_name],
                    "error_rate": self.error_counts[tool_name] / self.call_counts[tool_name],
                    "avg_duration": sum(times) / len(times),
                    "min_duration": min(times),
                    "max_duration": max(times)
                }
        
        return metrics

class InstrumentedMCPClient:
    """MCP client with built-in metrics collection."""
    
    def __init__(self, client: DoffinMCPClient, metrics: MCPMetrics):
        self.client = client
        self.metrics = metrics
    
    async def call_tool_instrumented(self, tool_name: str, params: Dict[str, Any]):
        """Call tool with metrics collection."""
        start_time = time.time()
        success = False
        
        try:
            result = await self.client.call_tool_safely(tool_name, params)
            success = result.get("success", False)
            return result
        except Exception as e:
            logger.error(f"Tool call failed: {tool_name} - {e}")
            raise
        finally:
            duration = time.time() - start_time
            self.metrics.record_call(tool_name, duration, success)
```

This comprehensive guide provides specific best practices for working with MCP implementations in the doffin-mcp project. It covers everything from basic server/client setup to advanced patterns like connection pooling, caching, and error recovery.

Remember to:
- Always validate inputs and outputs
- Implement proper error handling and recovery
- Use connection pooling for performance
- Monitor and instrument your MCP components
- Test thoroughly with both unit and integration tests
- Follow security best practices for production deployments