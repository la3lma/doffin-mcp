#!/usr/bin/env python3
"""
Robust MCP Client Example

This example demonstrates a resilient MCP client implementation with:
- Connection retry logic
- Error handling and recovery
- Request timeout management
- Connection pooling
- Result caching
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Mock classes for demonstration (replace with actual MCP SDK in practice)
class MCPConnectionError(Exception):
    """Raised when MCP connection fails."""
    pass

class MCPTimeoutError(Exception):
    """Raised when MCP request times out."""
    pass

class MCPValidationError(Exception):
    """Raised when request validation fails."""
    pass

class MockMCPClient:
    """Mock MCP client for demonstration."""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.is_connected = False
    
    async def connect(self):
        """Mock connection."""
        await asyncio.sleep(0.1)  # Simulate connection time
        self.is_connected = True
    
    async def disconnect(self):
        """Mock disconnection."""
        self.is_connected = False
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]):
        """Mock tool call."""
        if not self.is_connected:
            raise MCPConnectionError("Not connected to server")
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        # Mock response
        return {
            "success": True,
            "result": f"Processed {tool_name} with params {params}",
            "timestamp": time.time()
        }

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_factor: float = 2.0
    jitter: bool = True

class ConnectionState(Enum):
    """Connection state enumeration."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"

class RobustMCPClient:
    """
    A robust MCP client with comprehensive error handling and retry logic.
    
    Features:
    - Automatic connection recovery
    - Exponential backoff with jitter
    - Request timeout management
    - Connection state tracking
    - Detailed logging and metrics
    """
    
    def __init__(
        self,
        server_url: str,
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None
    ):
        self.server_url = server_url
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        
        self.client: Optional[MockMCPClient] = None
        self.state = ConnectionState.DISCONNECTED
        self.connection_attempts = 0
        self.last_error: Optional[Exception] = None
        
        # Metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.reconnection_count = 0
        
        # Setup logging
        self.logger = logging.getLogger(f"robust-mcp-client-{id(self)}")
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for the client."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    async def connect(self) -> bool:
        """
        Connect to the MCP server with retry logic.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.state == ConnectionState.CONNECTED:
            return True
        
        self.state = ConnectionState.CONNECTING
        
        for attempt in range(self.retry_config.max_attempts):
            try:
                self.logger.info(f"Connecting to MCP server: {self.server_url} (attempt {attempt + 1})")
                
                self.client = MockMCPClient(self.server_url)
                await asyncio.wait_for(self.client.connect(), timeout=self.timeout)
                
                self.state = ConnectionState.CONNECTED
                self.connection_attempts = attempt + 1
                self.logger.info(f"Successfully connected to MCP server")
                return True
                
            except asyncio.TimeoutError:
                self.last_error = MCPTimeoutError(f"Connection timeout after {self.timeout}s")
                self.logger.warning(f"Connection attempt {attempt + 1} timed out")
            except Exception as e:
                self.last_error = e
                self.logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < self.retry_config.max_attempts - 1:
                delay = self._calculate_retry_delay(attempt)
                self.logger.info(f"Retrying connection in {delay:.2f} seconds")
                await asyncio.sleep(delay)
        
        self.state = ConnectionState.FAILED
        self.logger.error(f"Failed to connect after {self.retry_config.max_attempts} attempts")
        return False
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        if self.client and self.state == ConnectionState.CONNECTED:
            try:
                await self.client.disconnect()
                self.logger.info("Disconnected from MCP server")
            except Exception as e:
                self.logger.warning(f"Error during disconnection: {e}")
            finally:
                self.client = None
                self.state = ConnectionState.DISCONNECTED
    
    async def call_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None,
        retry_on_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Call an MCP tool with comprehensive error handling.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            timeout: Request timeout (uses client default if None)
            retry_on_failure: Whether to retry on connection failures
        
        Returns:
            Tool response dictionary
        
        Raises:
            MCPConnectionError: If unable to connect
            MCPTimeoutError: If request times out
            MCPValidationError: If request validation fails
        """
        self.total_requests += 1
        request_timeout = timeout or self.timeout
        
        # Validate inputs
        self._validate_tool_request(tool_name, params)
        
        # Ensure connection
        if not await self._ensure_connected(retry_on_failure):
            self.failed_requests += 1
            raise MCPConnectionError(f"Unable to connect to server: {self.last_error}")
        
        # Execute request with retry logic
        for attempt in range(self.retry_config.max_attempts):
            try:
                self.logger.debug(f"Calling tool: {tool_name} (attempt {attempt + 1})")
                
                result = await asyncio.wait_for(
                    self.client.call_tool(tool_name, params),
                    timeout=request_timeout
                )
                
                self.successful_requests += 1
                self.logger.debug(f"Tool call successful: {tool_name}")
                return result
                
            except asyncio.TimeoutError:
                error = MCPTimeoutError(f"Tool call timed out after {request_timeout}s")
                self.logger.warning(f"Tool call timeout: {tool_name} (attempt {attempt + 1})")
                
                if attempt == self.retry_config.max_attempts - 1:
                    self.failed_requests += 1
                    raise error
                    
            except MCPConnectionError as e:
                self.logger.warning(f"Connection error during tool call: {e}")
                self.state = ConnectionState.DISCONNECTED
                
                if retry_on_failure and attempt < self.retry_config.max_attempts - 1:
                    # Try to reconnect
                    if await self._attempt_reconnection():
                        continue
                
                self.failed_requests += 1
                raise
                
            except Exception as e:
                self.logger.error(f"Unexpected error during tool call: {e}")
                
                if attempt == self.retry_config.max_attempts - 1:
                    self.failed_requests += 1
                    raise
            
            # Wait before retry
            if attempt < self.retry_config.max_attempts - 1:
                delay = self._calculate_retry_delay(attempt)
                await asyncio.sleep(delay)
        
        self.failed_requests += 1
        raise MCPConnectionError("Tool call failed after all retry attempts")
    
    async def batch_call_tools(
        self,
        tool_calls: List[Dict[str, Any]],
        max_concurrent: int = 5,
        fail_fast: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls concurrently.
        
        Args:
            tool_calls: List of tool call dictionaries with 'tool' and 'params' keys
            max_concurrent: Maximum number of concurrent calls
            fail_fast: If True, stop on first failure
        
        Returns:
            List of results in the same order as input
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def call_single_tool(call_info):
            async with semaphore:
                try:
                    return await self.call_tool(
                        call_info["tool"],
                        call_info["params"]
                    )
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "tool": call_info["tool"]
                    }
        
        # Create tasks
        tasks = [call_single_tool(call) for call in tool_calls]
        
        if fail_fast:
            # Stop on first failure
            results = []
            for task in asyncio.as_completed(tasks):
                result = await task
                if not result.get("success", True):
                    # Cancel remaining tasks
                    for remaining_task in tasks:
                        if not remaining_task.done():
                            remaining_task.cancel()
                    raise Exception(f"Batch operation failed: {result.get('error')}")
                results.append(result)
            return results
        else:
            # Wait for all tasks to complete
            return await asyncio.gather(*tasks, return_exceptions=True)
    
    def _validate_tool_request(self, tool_name: str, params: Dict[str, Any]):
        """Validate tool request parameters."""
        if not tool_name or not isinstance(tool_name, str):
            raise MCPValidationError("Tool name must be a non-empty string")
        
        if not isinstance(params, dict):
            raise MCPValidationError("Parameters must be a dictionary")
        
        # Additional validation can be added here
        # For example, checking parameter types, required fields, etc.
    
    async def _ensure_connected(self, retry_on_failure: bool = True) -> bool:
        """Ensure client is connected to the server."""
        if self.state == ConnectionState.CONNECTED:
            return True
        
        if retry_on_failure:
            return await self.connect()
        
        return False
    
    async def _attempt_reconnection(self) -> bool:
        """Attempt to reconnect to the server."""
        self.logger.info("Attempting to reconnect to server")
        self.state = ConnectionState.RECONNECTING
        self.reconnection_count += 1
        
        success = await self.connect()
        if success:
            self.logger.info("Reconnection successful")
        else:
            self.logger.error("Reconnection failed")
        
        return success
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt with exponential backoff and jitter."""
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_factor ** attempt),
            self.retry_config.max_delay
        )
        
        if self.retry_config.jitter:
            import random
            # Add up to 25% jitter
            jitter = delay * 0.25 * random.random()
            delay += jitter
        
        return delay
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about the current connection."""
        return {
            "server_url": self.server_url,
            "state": self.state.value,
            "connection_attempts": self.connection_attempts,
            "last_error": str(self.last_error) if self.last_error else None,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (
                self.successful_requests / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "reconnection_count": self.reconnection_count
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics about client performance."""
        return {
            "connection": self.get_connection_info(),
            "performance": {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": (
                    self.successful_requests / self.total_requests
                    if self.total_requests > 0 else 0
                ),
                "failure_rate": (
                    self.failed_requests / self.total_requests
                    if self.total_requests > 0 else 0
                )
            },
            "configuration": {
                "timeout": self.timeout,
                "max_retry_attempts": self.retry_config.max_attempts,
                "base_retry_delay": self.retry_config.base_delay,
                "max_retry_delay": self.retry_config.max_delay
            }
        }

class ClientWithConnectionPool:
    """MCP client that uses connection pooling for better performance."""
    
    def __init__(
        self,
        server_url: str,
        min_connections: int = 2,
        max_connections: int = 10,
        timeout: float = 30.0
    ):
        self.server_url = server_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.timeout = timeout
        
        self.available_clients = asyncio.Queue()
        self.total_clients = 0
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger("pooled-mcp-client")
    
    async def initialize(self):
        """Initialize the connection pool."""
        for _ in range(self.min_connections):
            client = await self._create_client()
            await self.available_clients.put(client)
        
        self.logger.info(f"Initialized connection pool with {self.min_connections} connections")
    
    async def _create_client(self) -> RobustMCPClient:
        """Create and connect a new client."""
        client = RobustMCPClient(self.server_url, timeout=self.timeout)
        await client.connect()
        self.total_clients += 1
        return client
    
    async def get_client(self) -> RobustMCPClient:
        """Get a client from the pool."""
        try:
            # Try to get an available client
            return self.available_clients.get_nowait()
        except asyncio.QueueEmpty:
            async with self.lock:
                if self.total_clients < self.max_connections:
                    # Create new client
                    return await self._create_client()
                else:
                    # Wait for available client
                    return await self.available_clients.get()
    
    async def return_client(self, client: RobustMCPClient):
        """Return a client to the pool."""
        if client.state == ConnectionState.CONNECTED:
            await self.available_clients.put(client)
        else:
            # Client is not healthy, create a replacement
            await client.disconnect()
            self.total_clients -= 1
            
            if self.total_clients < self.min_connections:
                try:
                    new_client = await self._create_client()
                    await self.available_clients.put(new_client)
                except Exception as e:
                    self.logger.error(f"Failed to create replacement client: {e}")
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool using a pooled connection."""
        client = await self.get_client()
        try:
            return await client.call_tool(tool_name, params)
        finally:
            await self.return_client(client)
    
    async def close_pool(self):
        """Close all connections in the pool."""
        clients_to_close = []
        
        # Collect all available clients
        while not self.available_clients.empty():
            try:
                client = self.available_clients.get_nowait()
                clients_to_close.append(client)
            except asyncio.QueueEmpty:
                break
        
        # Close all clients
        for client in clients_to_close:
            await client.disconnect()
        
        self.total_clients = 0
        self.logger.info("Connection pool closed")

async def demonstrate_robust_client():
    """Demonstrate the robust MCP client features."""
    print("=== Robust MCP Client Demonstration ===\n")
    
    # Create client with custom retry configuration
    retry_config = RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        exponential_factor=2.0,
        jitter=True
    )
    
    client = RobustMCPClient(
        server_url="http://localhost:8000",
        timeout=30.0,
        retry_config=retry_config
    )
    
    try:
        # Connect to server
        print("1. Connecting to MCP server...")
        connected = await client.connect()
        
        if not connected:
            print("Failed to connect to server")
            return
        
        print("   ✓ Connected successfully")
        
        # Make some tool calls
        print("\n2. Making tool calls...")
        
        # Simple tool call
        result1 = await client.call_tool("file_reader", {
            "path": "./data/sample.txt",
            "encoding": "utf-8"
        })
        print(f"   ✓ File reader result: {result1.get('success')}")
        
        # Data processing call
        result2 = await client.call_tool("data_processor", {
            "data": '{"name": "test", "value": 123}',
            "format": "json",
            "operation": "validate"
        })
        print(f"   ✓ Data processor result: {result2.get('success')}")
        
        # Text analysis call
        result3 = await client.call_tool("text_analyzer", {
            "text": "This is a sample text for analysis.",
            "analysis_type": "sentiment"
        })
        print(f"   ✓ Text analyzer result: {result3.get('success')}")
        
        # Batch call demonstration
        print("\n3. Batch tool calls...")
        batch_calls = [
            {"tool": "file_reader", "params": {"path": "./data/file1.txt"}},
            {"tool": "file_reader", "params": {"path": "./data/file2.txt"}},
            {"tool": "data_processor", "params": {
                "data": "1,2,3\n4,5,6",
                "format": "csv",
                "operation": "analyze"
            }}
        ]
        
        batch_results = await client.batch_call_tools(batch_calls, max_concurrent=3)
        print(f"   ✓ Batch processing completed: {len(batch_results)} results")
        
        # Show client metrics
        print("\n4. Client Metrics:")
        metrics = client.get_metrics()
        
        conn_info = metrics["connection"]
        perf_info = metrics["performance"]
        
        print(f"   Connection State: {conn_info['state']}")
        print(f"   Total Requests: {perf_info['total_requests']}")
        print(f"   Success Rate: {perf_info['success_rate']:.2%}")
        print(f"   Reconnections: {conn_info['reconnection_count']}")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
    finally:
        # Clean up
        await client.disconnect()
        print("\n5. Disconnected from server")

async def demonstrate_connection_pool():
    """Demonstrate connection pooling."""
    print("\n=== Connection Pool Demonstration ===\n")
    
    pool_client = ClientWithConnectionPool(
        server_url="http://localhost:8000",
        min_connections=2,
        max_connections=5,
        timeout=30.0
    )
    
    try:
        # Initialize pool
        print("1. Initializing connection pool...")
        await pool_client.initialize()
        print("   ✓ Connection pool initialized")
        
        # Make concurrent calls
        print("\n2. Making concurrent tool calls...")
        
        async def make_call(call_id):
            result = await pool_client.call_tool("data_processor", {
                "data": f"Call {call_id}",
                "format": "text",
                "operation": "analyze"
            })
            return f"Call {call_id}: {result.get('success')}"
        
        # Create 10 concurrent tasks
        tasks = [make_call(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"   ✓ {result}")
        
    except Exception as e:
        print(f"Error during pool demonstration: {e}")
    finally:
        await pool_client.close_pool()
        print("\n3. Connection pool closed")

async def main():
    """Main function demonstrating robust MCP client usage."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Robust MCP Client Examples")
    print("=" * 50)
    
    # Run demonstrations
    await demonstrate_robust_client()
    await demonstrate_connection_pool()
    
    print("\nDemonstration completed!")

if __name__ == "__main__":
    asyncio.run(main())