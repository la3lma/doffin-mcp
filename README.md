# Doffin MCP Server

A Model Context Protocol (MCP) server that provides access to public procurement notices from [doffin.no](https://doffin.no) - Norway's official procurement portal. This allows AI assistants like Claude to search and retrieve Norwegian public procurement data.

## What is this?

This MCP server enables AI assistants to:
- **Search** public procurement notices using keywords, dates, buyer names, and more
- **Retrieve** detailed notice information including documents, deadlines, and requirements
- **Access** Norwegian procurement data in a structured, AI-friendly format

Perfect for procurement professionals, business analysts, or anyone monitoring Norwegian public tenders.

## Quick Start

**New to MCP?** Follow the [detailed getting started guide](GETTING_STARTED.md) for step-by-step instructions.

### Prerequisites
- Python 3.11 or later
- Claude Desktop (or any MCP-compatible client)

### 1. Clone and Install
```bash
# Clone the repository
git clone https://github.com/yourusername/doffin-mcp.git
cd doffin-mcp/mcp-doffin

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Test the Server
```bash
# Test that everything works
python mcp_doffin.py
```

### 3. Configure Claude Desktop

Create the MCP server configuration file:

**macOS/Linux:** `~/.claude/mcp-servers/doffin.json`
**Windows:** `%UserProfile%\.claude\mcp-servers\doffin.json`

```json
{
  "command": "/path/to/your/.venv/bin/python",
  "args": ["/path/to/your/checkout/mcp-doffin/mcp_doffin.py"],
  "env": {
    "NO_COLOR": "1"
  }
}
```

> ⚠️ **Important:** Replace the paths above with your actual absolute paths.

### 4. Restart Claude Desktop

After creating the configuration file, restart Claude Desktop completely.

### 5. Try it out!

Open Claude Desktop and try these examples:

```
Search for API-related procurement notices from Oslo published in the last 30 days
```

```
Find all notices with a deadline in the next 7 days
```

## Available Tools

The server provides two MCP tools:

### `search_notices`
Search public procurement notices with various filters:
- `q`: Search text (keywords)
- `buyer`: Buyer organization name
- `published_from`/`published_to`: Date range (YYYY-MM-DD)
- `deadline_to`: Deadline filter (YYYY-MM-DD)  
- `county`: Geographic filter
- `procedure`: Procurement procedure type
- `cpv`: CPV codes (procurement categories)
- `page`: Page number for pagination

### `get_notice` 
Retrieve detailed information for a specific notice:
- `notice_id`: The notice ID from search results
- `url`: Direct doffin.no notice URL

## Documentation

- **[Getting Started Guide](GETTING_STARTED.md)** - Step-by-step setup for beginners
- [Detailed Setup Guide](mcp-doffin/README.md) - Complete installation and configuration
- [Testing Guide](tests/README.md) - How to run and write tests
- [Agent Instructions](AGENT_INSTRUCTIONS.md) - For AI agents working with this code
- [Docker Deployment](DOCKER.md) - Secure containerized deployment

## Troubleshooting

### Server not showing up in Claude Desktop
1. Check that the paths in your `doffin.json` are absolute and correct
2. Ensure the virtual environment is activated when testing manually
3. Restart Claude Desktop completely (quit and reopen)
4. Check Claude Desktop's logs for error messages

### "Command not found" or Python errors
1. Verify Python 3.11+ is installed: `python3 --version` or `python --version`
2. Ensure virtual environment is activated: `source .venv/bin/activate`
3. Check all dependencies are installed: `pip list`

### Tool calls failing
1. Test the server manually: `python mcp_doffin.py`
2. Check your internet connection (server needs to access doffin.no)
3. Verify the server isn't rate-limited (wait a few minutes and try again)

## Use Cases & Examples

### Business Intelligence
```
Find all IT procurement contracts from the Norwegian government in Q4 2024, focusing on cloud services and API development
```

### Compliance Monitoring  
```
Show me all procurement notices from Stavanger municipality that are closing in the next 2 weeks
```

### Market Research
```
Search for procurement opportunities related to "artificial intelligence" or "machine learning" published in the last 60 days
```

### Competitive Analysis
```
Get detailed information about procurement notice 2024-123456, including all documentation and requirements
```

## Development & Testing

```bash
# Run the test suite
cd doffin-mcp
pip install -r test_requirements.txt
make test

# Run with coverage
make coverage

# Run end-to-end tests (requires internet)
make test-e2e
```

See [tests/README.md](tests/README.md) for detailed testing information.

## Docker Deployment (Advanced)

For enhanced security, you can run the MCP server in a Docker container:

```bash
# Quick setup with Docker
./deploy-docker.sh all
```

See [DOCKER.md](DOCKER.md) for detailed Docker deployment instructions.

## Contributing

When contributing to this repository, please:

- Follow the existing code style and patterns
- Add tests for new functionality  
- Update documentation for any changes
- Test all changes thoroughly

## License

This project is open source and available under the [MIT License](LICENSE).

## Related Resources

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Doffin.no Official Site](https://doffin.no)
- [Claude Desktop MCP Documentation](https://docs.anthropic.com/claude/docs/mcp)