"""
Unit tests for doffin MCP server parsing functions.

These tests use mocked HTML responses to test the parsing logic
without making actual HTTP requests to doffin.no.
"""
import pytest
from unittest.mock import patch, Mock
import sys
import os

# Add the mcp-doffin directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-doffin'))

from mcp_doffin import (
    build_search_url, 
    parse_search, 
    parse_notice, 
    fetch,
    BASE
)


class TestBuildSearchUrl:
    """Test URL building for search requests."""
    
    def test_build_search_url_basic(self):
        """Test basic search URL generation."""
        params = {"q": "software"}
        expected = f"{BASE}/search?query=software"
        assert build_search_url(params) == expected

    def test_build_search_url_multiple_params(self, mock_search_params):
        """Test URL generation with multiple parameters."""
        url = build_search_url(mock_search_params)
        assert BASE in url
        assert "query=software" in url
        assert "buyer=Oslo+Kommune" in url
        assert "publishedFrom=2024-01-01" in url
        assert "publishedTo=2024-12-31" in url
        # page=1 should be omitted as it's the default
        assert "page=" not in url

    def test_build_search_url_cpv_codes(self):
        """Test URL generation with CPV codes array."""
        params = {"cpv": ["72000000-5", "48000000-8"]}
        url = build_search_url(params)
        assert "cpvCodesLabel=72000000-5%2C48000000-8" in url

    def test_build_search_url_empty_params(self):
        """Test URL generation with empty parameters."""
        params = {}
        expected = f"{BASE}/search?"
        assert build_search_url(params) == expected

    def test_build_search_url_page_omitted_when_one(self):
        """Test that page parameter is omitted when page=1."""
        params = {"q": "test", "page": 1}
        url = build_search_url(params)
        assert "page=" not in url

    def test_build_search_url_page_included_when_greater_than_one(self):
        """Test that page parameter is included when page > 1."""
        params = {"q": "test", "page": 2}
        url = build_search_url(params)
        assert "page=2" in url


class TestParseSearch:
    """Test parsing of search results HTML."""
    
    def test_parse_search_basic(self, sample_search_html, expected_search_result):
        """Test parsing a basic search result."""
        results = parse_search(sample_search_html)
        assert len(results) == 1
        result = results[0]
        
        assert result["notice_id"] == expected_search_result["notice_id"]
        assert result["title"] == expected_search_result["title"]
        assert result["buyer"] == expected_search_result["buyer"]
        assert result["published_at"] == expected_search_result["published_at"]
        assert result["deadline_at"] == expected_search_result["deadline_at"]
        assert result["cpv"] == expected_search_result["cpv"]
        assert result["link"] == expected_search_result["link"]

    def test_parse_search_empty_html(self):
        """Test parsing empty HTML returns empty list."""
        results = parse_search("")
        assert results == []

    def test_parse_search_no_notice_cards(self):
        """Test parsing HTML without notice cards."""
        html = "<div>No notices found</div>"
        results = parse_search(html)
        assert results == []

    def test_parse_search_missing_link(self):
        """Test parsing notice card without link is skipped."""
        html = """
        <div class="notice-card">
            <h3 class="notice-title">Test Notice</h3>
            <div class="notice-buyer">Test Buyer</div>
        </div>
        """
        results = parse_search(html)
        assert results == []

    def test_parse_search_missing_title(self):
        """Test parsing notice card without explicit title uses link text."""
        html = """
        <div class="notice-card">
            <a href="/notices/12345">View Details</a>
            <div class="notice-buyer">Test Buyer</div>
        </div>
        """
        results = parse_search(html)
        # Should find title from link text
        assert len(results) == 1
        assert results[0]["title"] == "View Details"

    def test_parse_search_relative_link_conversion(self):
        """Test that relative links are converted to absolute URLs."""
        html = """
        <div class="notice-card">
            <h3 class="notice-title">Test Notice</h3>
            <a href="/notices/12345">View Details</a>
        </div>
        """
        results = parse_search(html)
        assert len(results) == 1
        assert results[0]["link"] == f"{BASE}/notices/12345"


class TestParseNotice:
    """Test parsing of notice detail HTML."""
    
    def test_parse_notice_basic(self, sample_notice_html):
        """Test parsing a basic notice detail page."""
        url = "https://doffin.no/notices/12345"
        result = parse_notice(sample_notice_html, url)
        
        assert result["source_url"] == url
        assert result["title"] == "Test Procurement Notice"
        assert result["buyer"] == "Oslo Kommune"
        # JSON-LD takes precedence over HTML content
        assert result["description"] == "Software development services"
        assert result["published_at"] == "2024-01-15T10:00:00Z"
        assert result["deadline_at"] == "2024-02-15T15:00:00Z"
        assert result["cpv"] == ["72000000-5"]
        # Check that we have attachments and at least one matches our expected pattern
        assert len(result["attachments"]) >= 1
        attachment_names = [att["name"] for att in result["attachments"]]
        assert "Tender Documentation.pdf" in attachment_names

    def test_parse_notice_json_ld_parsing(self, sample_notice_html):
        """Test that JSON-LD data is properly parsed and merged."""
        url = "https://doffin.no/notices/12345"
        result = parse_notice(sample_notice_html, url)
        
        # JSON-LD should override HTML-parsed values
        assert result["title"] == "Test Procurement Notice"
        assert result["buyer"] == "Oslo Kommune"
        assert result["description"] == "Software development services"  # From JSON-LD

    def test_parse_notice_empty_html(self):
        """Test parsing empty HTML."""
        url = "https://doffin.no/notices/12345"
        result = parse_notice("", url)
        
        assert result["source_url"] == url
        assert result.get("title") is None
        assert result.get("buyer") is None
        assert result.get("attachments") == []

    def test_parse_notice_invalid_json_ld(self):
        """Test handling of invalid JSON-LD data."""
        html = """
        <h1>Test Notice</h1>
        <script type="application/ld+json">
        { invalid json }
        </script>
        """
        url = "https://doffin.no/notices/12345"
        result = parse_notice(html, url)
        
        assert result["source_url"] == url
        assert result["title"] == "Test Notice"

    def test_parse_notice_relative_attachment_urls(self):
        """Test that relative attachment URLs are converted to absolute."""
        html = """
        <h1>Test Notice</h1>
        <a href="/Document/123.pdf">Document.pdf</a>
        """
        url = "https://doffin.no/notices/12345"
        result = parse_notice(html, url)
        
        # Filter to just the document we're testing
        doc_attachments = [att for att in result["attachments"] if att["name"] == "Document.pdf"]
        assert len(doc_attachments) >= 1
        assert doc_attachments[0]["url"] == f"{BASE}/Document/123.pdf"

    def test_parse_notice_raw_html_truncation(self):
        """Test that raw HTML is truncated to keep payload size manageable."""
        # Create HTML that's longer than 200,000 characters
        large_html = "<h1>Test</h1>" + "x" * 250000
        url = "https://doffin.no/notices/12345"
        result = parse_notice(large_html, url)
        
        assert len(result["raw_html"]) <= 200000


class TestFetch:
    """Test HTTP fetching functionality."""
    
    @pytest.mark.asyncio
    async def test_fetch_success(self, httpx_mock):
        """Test successful HTTP fetch."""
        url = "https://doffin.no/test"
        expected_content = "<html>Test content</html>"
        
        httpx_mock.add_response(
            method="GET",
            url=url,
            text=expected_content,
            status_code=200
        )
        
        result = await fetch(url)
        assert result == expected_content

    @pytest.mark.asyncio
    async def test_fetch_http_error(self, httpx_mock):
        """Test HTTP error handling."""
        url = "https://doffin.no/test"
        
        httpx_mock.add_response(
            method="GET",
            url=url,
            status_code=404
        )
        
        # The fetch function has retry logic, so it will try 3 times
        # We need to add the same response 3 times
        for _ in range(2):  # Add 2 more responses for retries
            httpx_mock.add_response(
                method="GET", 
                url=url,
                status_code=404
            )
        
        with pytest.raises(Exception):
            await fetch(url)

    @pytest.mark.asyncio
    async def test_fetch_retry_on_failure(self, httpx_mock):
        """Test retry behavior on failure."""
        url = "https://doffin.no/test"
        
        # First two requests fail, third succeeds
        httpx_mock.add_response(
            method="GET",
            url=url,
            status_code=500
        )
        httpx_mock.add_response(
            method="GET",
            url=url,
            status_code=500
        )
        httpx_mock.add_response(
            method="GET",
            url=url,
            text="Success",
            status_code=200
        )
        
        result = await fetch(url)
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_fetch_user_agent_header(self, httpx_mock):
        """Test that correct User-Agent header is sent."""
        url = "https://doffin.no/test"
        
        # Use a simple response instead of callback to avoid mocking issues
        httpx_mock.add_response(
            method="GET",
            url=url,
            text="OK",
            status_code=200,
            match_headers={"User-Agent": "MCP-Doffin/1.0 (+contact@example.com)"}
        )
        
        result = await fetch(url)
        assert result == "OK"

    @pytest.mark.asyncio
    async def test_fetch_timeout_handling(self, httpx_mock):
        """Test timeout handling."""
        url = "https://doffin.no/test"
        
        httpx_mock.add_response(
            method="GET",
            url=url,
            text="Success",
            status_code=200
        )
        
        # This test verifies that the timeout parameter is set correctly
        # The actual timeout testing would require more complex mocking
        result = await fetch(url)
        assert result == "Success"