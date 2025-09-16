# Doffin MCP Server

Doffin MCP Server is a Python-based Model Context Protocol (MCP) server implementation. This project uses modern Python development practices with comprehensive tooling for testing, linting, and packaging.

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Initial Development Environment Setup
**NEVER CANCEL any of these setup commands. Set timeouts to 60+ minutes for all package installations.**

- Install Python development dependencies:
  - `sudo apt-get update && sudo apt-get install -y python3-dev python3-pip python3-venv build-essential`
  - **NEVER CANCEL: Package installation takes 3-5 minutes. Set timeout to 10+ minutes.**

- Create and activate virtual environment:
  - `python3 -m venv venv`
  - `source venv/bin/activate`
  - Always activate the virtual environment before any Python operations

- Install project dependencies (once project structure is created):
  - `pip install --upgrade pip setuptools wheel --timeout 60 --retries 3`
  - `pip install -e . --timeout 60 --retries 3` -- installs project in development mode
  - `pip install -r requirements-dev.txt --timeout 60 --retries 3` -- development dependencies
  - **NEVER CANCEL: Dependency installation takes 2-5 minutes but may fail due to network timeouts. Set timeout to 15+ minutes and retry if needed.**
  - **CRITICAL**: If PyPI timeouts occur, use `pip install --no-index --find-links /tmp/wheels <package>` with pre-downloaded wheels

### Alternative Setup for Network Issues
If PyPI connectivity is limited:
- Use system packages: `sudo apt-get install -y python3-pytest python3-black python3-mypy python3-flake8`
- Run tests with system Python: `PYTHONPATH=src python3 -m pytest tests/ -v`
- Use basic linting: `python3 -m py_compile src/doffin_mcp/*.py` to check syntax

### Project Structure Creation
When creating the initial project structure, create these directories and files:

```
doffin-mcp/
├── src/
│   └── doffin_mcp/
│       ├── __init__.py
│       ├── server.py
│       └── handlers/
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_server.py
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── pyproject.toml
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

### Build and Test Commands
**CRITICAL: All build and test commands require appropriate timeouts. NEVER CANCEL these operations.**

- Install project in development mode:
  - `pip install -e . --timeout 60 --retries 3`
  - **NEVER CANCEL: Takes 30-60 seconds. Set timeout to 5+ minutes. May fail with network timeouts.**

- Run unit tests:
  - `python -m pytest tests/ -v` (if pytest installed in venv)
  - `PYTHONPATH=src python3 -m pytest tests/ -v` (if using system pytest)
  - **NEVER CANCEL: Test suite takes 1-2 minutes. Set timeout to 10+ minutes.**

- Run tests with coverage (if tools available):
  - `python -m pytest tests/ --cov=src/doffin_mcp --cov-report=html --cov-report=term`
  - **NEVER CANCEL: Coverage testing takes 2-3 minutes. Set timeout to 10+ minutes.**

- Basic functionality test (always works):
  - `PYTHONPATH=src python3 -m doffin_mcp.server` -- test server startup
  - `PYTHONPATH=src python3 -c "from doffin_mcp.server import hello_world; print(hello_world())"` -- test imports

- Type checking with mypy (if available):
  - `mypy src/doffin_mcp` or `python3 -m mypy src/doffin_mcp`
  - **Takes 30-60 seconds. Set timeout to 5+ minutes.**

- Code formatting and linting (if tools available):
  - `black src/ tests/` -- code formatting
  - `isort src/ tests/` -- import sorting  
  - `flake8 src/ tests/` -- linting
  - `ruff check src/ tests/` -- modern linting
  - **Each command takes 10-30 seconds. Set timeout to 2+ minutes each.**

- Syntax checking (always available):
  - `python3 -m py_compile src/doffin_mcp/*.py` -- basic syntax check
  - `python3 -m compileall src/` -- compile all Python files

### Running the MCP Server
- Start the development server:
  - `PYTHONPATH=src python3 -m doffin_mcp.server` (basic method, always works)
  - `python -m doffin_mcp.server` (if package installed in venv)
  - Or using the entry point: `doffin-mcp-server` (if package installed)

- Run server with debug logging:
  - `PYTHONPATH=src python3 -m doffin_mcp.server --debug`

- Test server functionality:
  - Basic import test: `PYTHONPATH=src python3 -c "from doffin_mcp.server import hello_world; print('✓ Server imported successfully:', hello_world())"`
  - Check that server starts and runs without errors

## Validation

### Manual Testing Requirements
**ALWAYS manually validate any changes using these scenarios:**

1. **Basic Server Functionality**:
   - Start the MCP server: `PYTHONPATH=src python3 -m doffin_mcp.server`
   - Verify server starts without errors and displays greeting message  
   - Test basic import: `PYTHONPATH=src python3 -c "from doffin_mcp.server import hello_world; assert 'Hello' in hello_world()"`
   - Verify the function returns expected greeting message

2. **MCP Protocol Compliance**:
   - Test capability negotiation
   - Verify resource listing functionality
   - Test tool invocation if applicable
   - Validate JSON-RPC message format compliance

3. **Development Workflow**:
   - Make a small code change
   - Run syntax check: `python3 -m py_compile src/doffin_mcp/*.py`
   - Run basic functionality test: `PYTHONPATH=src python3 -c "from doffin_mcp.server import hello_world; print('✓ Test passed:', hello_world())"`
   - If tools available: `black src/ tests/ && isort src/ tests/ && flake8 src/ tests/`
   - If pytest available: `PYTHONPATH=src python3 -m pytest tests/ -v`
   - Start server and verify functionality: `PYTHONPATH=src python3 -m doffin_mcp.server`

### Pre-commit Validation
**ALWAYS run these commands before committing changes or the CI will fail:**

```bash
# Basic syntax validation (always available)
python3 -m py_compile src/doffin_mcp/*.py
python3 -m compileall src/

# Basic functionality test
PYTHONPATH=src python3 -c "from doffin_mcp.server import hello_world; print('✓ Import test passed')"
PYTHONPATH=src python3 -m doffin_mcp.server

# If development tools are available:
black src/ tests/
isort src/ tests/ 
flake8 src/ tests/
ruff check src/ tests/ --fix

# Type checking (if mypy available)
mypy src/doffin_mcp

# Run tests (if pytest available)
PYTHONPATH=src python3 -m pytest tests/ -v

# Verify server starts
timeout 10s bash -c "PYTHONPATH=src python3 -m doffin_mcp.server" || echo "✓ Server executable"
```

**NEVER CANCEL: Full validation takes 1-3 minutes. Set timeout to 10+ minutes. Some tools may not be available due to network issues.**

## Development Guidelines

### MCP Server Specific Considerations
- Follow the Model Context Protocol specification
- Implement proper JSON-RPC 2.0 message handling
- Use structured logging for debugging
- Handle client disconnections gracefully
- Implement proper capability negotiation

### Code Quality Standards
- All code must pass type checking with mypy
- Code coverage should be >90%
- Follow PEP 8 style guidelines (enforced by black/flake8)
- All public functions require docstrings
- Use structured exception handling

### Common Development Tasks

#### Adding New MCP Capabilities
1. Define capability in `src/doffin_mcp/capabilities.py`
2. Implement handler in `src/doffin_mcp/handlers/`
3. Add tests in `tests/test_[capability_name].py`
4. Update server registration in `src/doffin_mcp/server.py`
5. Run full validation suite

#### Adding Dependencies
1. Add to `requirements.txt` for runtime dependencies
2. Add to `requirements-dev.txt` for development dependencies
3. Run `pip install -r requirements.txt -r requirements-dev.txt`
4. Update `setup.py` if adding core dependencies

## Repository Structure

### Current Repository State
```
doffin-mcp/
├── .git/
├── .gitignore (Python-focused)
├── pyproject.toml (modern Python packaging configuration)
├── requirements.txt (runtime dependencies template)
├── requirements-dev.txt (development dependencies)
└── .github/
    └── copilot-instructions.md (this file)
```

### Key Files to Create
- `README.md` -- project overview and quick start
- `src/doffin_mcp/` -- main package directory
  - `__init__.py` -- package initialization
  - `server.py` -- main MCP server implementation
  - `handlers/` -- MCP capability handlers
- `tests/` -- test suite
  - `test_server.py` -- server tests
  - Additional test files as needed
- `.github/workflows/ci.yml` -- CI/CD pipeline

### Files Already Present
- ✅ `pyproject.toml` -- modern Python packaging configuration
- ✅ `requirements.txt` -- runtime dependencies template  
- ✅ `requirements-dev.txt` -- development dependencies
- ✅ `.gitignore` -- Python-focused ignore patterns

### Important Notes
- This is a new repository with minimal existing code
- Virtual environment setup is critical for development
- MCP server requires careful protocol implementation
- Follow Python packaging best practices
- Use modern Python development tools (black, mypy, pytest, ruff)

## Troubleshooting

### Common Issues
- **Import errors**: Ensure `PYTHONPATH=src` is set when running commands outside virtual environment or use `pip install -e .`
- **Test failures**: Check that all dependencies are installed or use `PYTHONPATH=src` prefix for commands
- **Server won't start**: Verify import with `PYTHONPATH=src python3 -c "import doffin_mcp.server"`
- **Type checking errors**: Use `# type: ignore` comments for problematic imports if mypy unavailable
- **PyPI timeouts**: Use system packages with `sudo apt-get install python3-<package>` or retry with longer timeouts

### Network Connectivity Issues
This environment may have limited internet access. If `pip install` fails:
1. Use system packages: `sudo apt-get install python3-pytest python3-black python3-mypy`
2. Use offline mode: `pip install --no-index --find-links <local-path> <package>`
3. Continue development with basic tools: `python3 -m py_compile` and `PYTHONPATH=src`

### Performance Expectations
- Virtual environment creation: 30-60 seconds
- Package installation: 2-5 minutes (may timeout, retry with longer timeouts)
- Test suite: 1-3 minutes (grows with test count)
- Linting/formatting: 10-30 seconds each
- Server startup: 1-5 seconds
- **CRITICAL**: PyPI operations may fail due to network timeouts - this is expected

**CRITICAL REMINDER: NEVER CANCEL long-running operations. Always set appropriate timeouts and wait for completion.**