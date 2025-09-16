
# MCP Doffin (Python)

A minimal **Model Context Protocol (MCP)** server that lets Claude (Desktop/Workbench or any MCP client) search and read public notices from **doffin.no** responsibly (scraping public pages at ≤1 req/s).

It exposes two MCP tools:
- `doffin.search_notices`
- `doffin.get_notice`

> Note: This uses public pages only. Be polite and considerate when scraping.
> The CSS selectors are intentionally defensive; you may adjust them after a quick look in DevTools.

---

## 1) Install (Python 3.11+ recommended)

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Upgrade pip and install deps
pip install --upgrade pip
pip install -r requirements.txt
```

If you prefer Poetry/PDM, there's also a `pyproject.toml` you can use:

```bash
# Poetry example
pip install poetry
poetry install
```

---

## 2) Run the MCP server (stdio)

```bash
# From this folder with the venv active:
python mcp_doffin.py
```

The server speaks MCP over **stdio**, so MCP clients (like Claude Desktop) can launch it as a subprocess.

---

## 3) Wire into Claude Desktop

Create a server definition so Claude can auto‑launch the MCP server.

### macOS / Linux

Create the file:
```
~/.claude/mcp-servers/doffin.json
```
with contents (edit paths to your local checkout and Python path):

```json
{
  "command": "/absolute/path/to/your/.venv/bin/python",
  "args": ["/absolute/path/to/checkout/mcp_doffin.py"],
  "env": {
    "NO_COLOR": "1"
  }
}
```

Then **restart Claude Desktop**. You should see an MCP server named **mcp-doffin** available, providing tools:
- `doffin.search_notices`
- `doffin.get_notice`

### Windows

Create:
```
%UserProfile%\.claude\mcp-servers\doffin.json
```
with:
```json
{
  "command": "C:\\path\\to\\your\\venv\\Scripts\\python.exe",
  "args": ["C:\\path\\to\\checkout\\mcp_doffin.py"],
  "env": {
    "NO_COLOR": "1"
  }
}
```

Restart Claude Desktop.

> Tip: If you keep the project elsewhere later, just update the JSON paths.

---

## 4) Try it

Open a chat with Claude and type:

- “Finn kunngjøringer fra Oslo kommune publisert siste 30 dager med ‘API’ i teksten. Bruk `doffin.search_notices`, deretter `doffin.get_notice` på de tre første.”
- “Hent detaljer (CPV, frist, dokumenter) for `https://doffin.no/notices/XXXXXX`.”

Claude should automatically pick the right tool calls via MCP.

---

## 5) Files in this repo

- `mcp_doffin.py` — MCP server implementation (Python + httpx + selectolax + tenacity)
- `requirements.txt` — pip dependencies
- `pyproject.toml` — optional modern packaging metadata
- `doffin.json.example` — sample Claude Desktop config
- `Makefile` — convenience commands

---

## 6) Notes, etiquette & troubleshooting

- **Rate limit**: The server limits to ~1 request/second with retry backoff.
- **Selectors**: If Doffin changes DOM, tweak `parse_search` / `parse_notice` functions.
- **Caching**: You can add a simple in‑memory cache if you plan to do many repeated queries.
- **Errors**: If Claude reports a tool error, run `python mcp_doffin.py` manually to see logs.

If you want a Node/TypeScript version or a FastAPI HTTP tool server instead of stdio, we can add that too.

---

## 7) Testing

This project includes comprehensive tests to ensure reliability and correctness.

### Test Suites

- **Unit Tests**: Test individual functions with mocked dependencies
- **Integration Tests**: Test component interactions with mocked HTTP calls  
- **End-to-End Tests**: Test against real doffin.no API (optional)

### Running Tests

```bash
# Install test dependencies
pip install -r test_requirements.txt

# Run unit tests (fast)
make test-unit

# Run integration tests
make test-integration

# Run both unit and integration tests
make test

# Run end-to-end tests (requires internet)
make test-e2e

# Generate coverage report
make coverage
```

### Test Coverage
Current test coverage: **86%**

The test suite includes:
- 23 unit tests covering URL building, HTML parsing, and HTTP fetching
- 12 integration tests covering complete workflows and error handling
- 8 end-to-end tests for real API validation

### Continuous Integration
GitHub Actions automatically runs tests on:
- All pushes and pull requests (unit + integration tests)
- Pushes to main branch (includes end-to-end tests)

See `tests/README.md` for detailed testing documentation.
