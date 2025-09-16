# Testing Documentation

This document describes the testing infrastructure for the doffin-mcp server.

## Test Structure

The testing suite is organized into three main categories:

### 1. Unit Tests (`tests/test_unit.py`)
- **Purpose**: Test individual functions in isolation with mocked dependencies
- **Coverage**: URL building, HTML parsing, HTTP fetching with retry logic
- **No external dependencies**: All HTTP requests are mocked
- **Fast execution**: Suitable for development and CI/CD

### 2. Integration Tests (`tests/test_integration.py`)
- **Purpose**: Test the interaction between components with mocked external services
- **Coverage**: MCP tool functions, error handling, complex scenarios
- **Mocked external services**: HTTP requests to doffin.no are mocked
- **Medium execution time**: Tests complete workflows

### 3. End-to-End Tests (`tests/test_e2e.py`)
- **Purpose**: Test against the real doffin.no API
- **Coverage**: Actual network requests, real data parsing, live service integration
- **External dependencies**: Requires internet connection and doffin.no availability
- **Slower execution**: Only run in specific CI environments or manually

## Running Tests

### Prerequisites
```bash
cd mcp-doffin
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r test_requirements.txt
```

### Running Individual Test Suites

```bash
# Unit tests only (fastest)
make test-unit
# or
python -m pytest tests/test_unit.py -v

# Integration tests only
make test-integration
# or
python -m pytest tests/test_integration.py -v

# End-to-end tests only (requires internet)
make test-e2e
# or
python -m pytest tests/test_e2e.py -v -m e2e

# All tests except e2e
make test

# All tests including e2e
make test-all
```

### Coverage Analysis

```bash
# Generate coverage report
make coverage
# or
python -m pytest tests/test_unit.py tests/test_integration.py --cov=mcp_doffin --cov-report=html --cov-report=term
```

The coverage report will be generated in `htmlcov/index.html` for detailed analysis.

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- Configures test discovery, async handling, and coverage settings
- Sets up markers for different test types
- Configures coverage thresholds (currently 80%)

### Test Fixtures (`tests/conftest.py`)
- Shared test data and mock objects
- Sample HTML responses from doffin.no
- Expected parsed results for validation

## GitHub Actions Workflow

The CI/CD pipeline (`.github/workflows/test.yml`) runs:

1. **Unit and Integration Tests**: On all pushes and pull requests
   - Tests multiple Python versions (3.11, 3.12)
   - Generates coverage reports
   - Fails if coverage drops below threshold

2. **End-to-End Tests**: Only on pushes to main branch
   - Tests against real doffin.no API
   - Continues on error (external service dependency)

3. **Server Startup Test**: Validates that the MCP server starts correctly

## Writing New Tests

### Unit Test Guidelines
- Mock all external dependencies
- Test edge cases and error conditions
- Focus on single function behavior
- Use descriptive test names

Example:
```python
def test_build_search_url_with_special_characters(self):
    """Test URL building handles special characters correctly."""
    params = {"q": "software & hardware"}
    url = build_search_url(params)
    assert "software+%26+hardware" in url
```

### Integration Test Guidelines
- Test component interactions
- Mock external HTTP calls
- Test complete workflows
- Verify error propagation

### E2E Test Guidelines
- Mark with `@pytest.mark.e2e`
- Handle external service failures gracefully
- Test realistic scenarios
- Don't depend on specific data (it changes)

## Test Data

### Mocked HTML Responses
Located in `tests/conftest.py`, these provide realistic sample data:
- `sample_search_html`: Search results page HTML
- `sample_notice_html`: Notice detail page HTML
- Expected parsing results for validation

### Updating Test Data
When doffin.no changes their HTML structure:
1. Update sample HTML in `tests/conftest.py`
2. Update expected results accordingly
3. Run tests to verify compatibility
4. Update parsing logic if needed

## Troubleshooting

### Common Issues

1. **Coverage warnings**: Ensure PYTHONPATH includes the module directory
2. **Async test failures**: Check that fixtures use proper async/await
3. **Mock issues**: Verify HTTP mocks match actual request patterns
4. **E2E test failures**: External service dependency, check manually

### Test Isolation
Each test is isolated and should not depend on others. If tests fail when run together but pass individually, check for:
- Shared state in fixtures
- Global variable modifications
- Improper mocking cleanup

## Performance Considerations

- Unit tests: ~6 seconds for 23 tests
- Integration tests: ~11 seconds for 12 tests  
- E2E tests: Variable (depends on network and service response times)

Total test suite (unit + integration): ~18 seconds with 35 tests and 86% coverage.