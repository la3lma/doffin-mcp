# Examples for doffin-mcp

This directory contains practical examples demonstrating the concepts outlined in the agent instructions and MCP best practices.

## Available Examples

1. [Basic MCP Server](basic-server.py) - Simple MCP server implementation
2. [Robust MCP Client](robust-client.py) - Client with error handling and retries
3. [Tool Development](tool-examples.py) - Example tool implementations
4. [Connection Pooling](connection-pool.py) - Connection pool implementation
5. [Caching Example](caching-example.py) - Result caching for performance
6. [Testing Examples](test-examples.py) - Comprehensive testing approaches

## Running the Examples

Each example is self-contained and includes instructions for execution. Make sure to install the required dependencies:

```bash
pip install mcp-sdk asyncio pytest
```

## Example Usage Patterns

### Quick Start Server
```python
python examples/basic-server.py
```

### Client with Error Handling
```python
python examples/robust-client.py
```

### Running Tests
```python
python -m pytest examples/test-examples.py -v
```

For detailed explanations of each example, see the individual files.