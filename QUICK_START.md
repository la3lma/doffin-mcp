# Quick Start Guide

This guide helps you get started with doffin-mcp quickly.

## For AI Agents

If you're an AI agent working with this repository:

1. **Read the Agent Instructions first**: [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md)
2. **Review MCP Best Practices**: [docs/mcp-best-practices.md](docs/mcp-best-practices.md)
3. **Check the examples**: [examples/](examples/)

## Key Principles for Efficient Agent Work

### 1. Understand Before Acting
- Read existing code and documentation thoroughly
- Understand the project structure and dependencies
- Identify patterns and conventions used

### 2. Make Minimal Changes
- Change only what's necessary to achieve the goal
- Preserve existing functionality
- Follow established patterns and conventions

### 3. Test and Validate
- Run existing tests before making changes
- Create focused tests for new functionality
- Validate changes don't break existing behavior

### 4. Document Changes
- Update documentation when making changes
- Follow existing documentation patterns
- Include examples for complex changes

## MCP Development Workflow

1. **Setup**: Install dependencies and understand the MCP protocol
2. **Design**: Plan your server/client architecture
3. **Implement**: Follow the patterns in the examples
4. **Test**: Use the testing strategies from the documentation
5. **Deploy**: Follow security and performance best practices

## Common Patterns

### Error Handling
```python
try:
    result = await mcp_client.call_tool("tool_name", params)
    if result["success"]:
        return result["data"]
    else:
        logger.error(f"Tool failed: {result['error']}")
        return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Input Validation
```python
def validate_params(params: dict) -> bool:
    if not isinstance(params, dict):
        raise ValueError("Parameters must be a dictionary")
    
    required_fields = ["field1", "field2"]
    for field in required_fields:
        if field not in params:
            raise ValueError(f"Required field missing: {field}")
    
    return True
```

### Async Tool Implementation
```python
async def handle_tool(self, **params):
    try:
        # Validate inputs
        self.validate_inputs(params)
        
        # Process request
        result = await self.process_request(params)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

## Resources

- [Agent Instructions](AGENT_INSTRUCTIONS.md) - Comprehensive guide
- [MCP Best Practices](docs/mcp-best-practices.md) - Protocol-specific guidelines
- [Examples](examples/) - Working code examples
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/) - Official spec

## Getting Help

- Check the examples for similar use cases
- Review the troubleshooting section in the agent instructions
- Look at the error handling patterns in the best practices
- Open an issue if you find gaps in the documentation