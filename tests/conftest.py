# Test configuration and fixtures
import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_search_html():
    """Sample HTML response from doffin.no search page."""
    return """
    <div class="notice-card">
        <h3 class="notice-title">Test Procurement Notice</h3>
        <a href="/notices/12345">View Details</a>
        <div class="notice-buyer">Oslo Kommune</div>
        <time datetime="2024-01-15T10:00:00Z" data-test="published">Published: 15.01.2024</time>
        <time datetime="2024-02-15T15:00:00Z" data-test="deadline">Deadline: 15.02.2024</time>
        <div class="notice-cpv">
            <span class="tag">72000000-5</span>
            <span class="tag">Software development</span>
        </div>
    </div>
    """

@pytest.fixture
def sample_notice_html():
    """Sample HTML response from doffin.no notice detail page."""
    return """
    <h1>Test Procurement Notice</h1>
    <div data-test="buyer-name">Oslo Kommune</div>
    <time datetime="2024-01-15T10:00:00Z" data-test="published">Published: 15.01.2024</time>
    <time datetime="2024-02-15T15:00:00Z" data-test="deadline">Deadline: 15.02.2024</time>
    <div data-test="description">
        Looking for software development services for a new digital platform.
    </div>
    <div data-test="cpv">
        <span class="tag">72000000-5</span>
    </div>
    <a href="/Document/123456.pdf">Tender Documentation.pdf</a>
    <script type="application/ld+json">
    {
        "title": "Test Procurement Notice",
        "buyer": "Oslo Kommune",
        "description": "Software development services"
    }
    </script>
    """

@pytest.fixture
def mock_search_params():
    """Sample search parameters."""
    return {
        "q": "software",
        "buyer": "Oslo Kommune",
        "published_from": "2024-01-01",
        "published_to": "2024-12-31",
        "page": 1
    }

@pytest.fixture
def expected_search_result():
    """Expected parsed search result."""
    return {
        "notice_id": "12345",
        "title": "Test Procurement Notice",
        "buyer": "Oslo Kommune",
        "published_at": "2024-01-15T10:00:00Z",
        "deadline_at": "2024-02-15T15:00:00Z",
        "cpv": ["72000000-5", "Software development"],
        "link": "https://doffin.no/notices/12345"
    }

@pytest.fixture
def expected_notice_result():
    """Expected parsed notice result."""
    return {
        "source_url": "https://doffin.no/notices/12345",
        "title": "Test Procurement Notice",
        "buyer": "Oslo Kommune",
        "description": "Software development services",  # From JSON-LD
        "published_at": "2024-01-15T10:00:00Z",
        "deadline_at": "2024-02-15T15:00:00Z",
        "cpv": ["72000000-5"],
        "attachments": [
            {
                "name": "Tender Documentation.pdf",
                "url": "https://doffin.no/Document/123456.pdf"
            }
        ]
    }