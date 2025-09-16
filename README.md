# doffin-mcp

A repository focused on providing comprehensive instructions and best practices for AI agents working with the Model Context Protocol (MCP).

## Overview

This repository contains documentation, guidelines, and best practices to help AI agents work more efficiently when using MCP (Model Context Protocol) implementations.

## Documentation

- [Agent Instructions](AGENT_INSTRUCTIONS.md) - Comprehensive guide for AI agents
- [MCP Best Practices](docs/mcp-best-practices.md) - Specific guidelines for MCP usage
- [Examples](examples/) - Practical examples and use cases

## Quick Start

For AI agents working with this repository:

1. Read the [Quick Start Guide](QUICK_START.md) for immediate guidance
2. Review the comprehensive [Agent Instructions](AGENT_INSTRUCTIONS.md)
3. Check MCP-specific guidelines in [docs/mcp-best-practices.md](docs/mcp-best-practices.md)
4. Explore [examples](examples/) for practical implementations

## Contributing

When contributing to this repository, please:

- Follow the agent efficiency guidelines
- Update documentation for any new patterns
- Include examples for complex implementations
- Test all code changes thoroughly

## Docker Deployment

For enhanced security, you can run the MCP server in a Docker container instead of directly on your system. This approach:

- Runs the server with a non-root user in an isolated environment
- Provides resource limits and network isolation
- Reduces security risks compared to running as your user account

See [DOCKER.md](DOCKER.md) for detailed Docker deployment instructions, or use the quick deployment script:

```bash
# Quick setup with Docker
./deploy-docker.sh all
```

## License

This project is open source and available under the [MIT License](LICENSE).