"""
Integration tests for doffin MCP server.

These tests mock HTTP responses but test the actual MCP tool functions
to ensure they work correctly end-to-end.
"""
import pytest
from unittest.mock import patch, AsyncMock
import sys
import os
import asyncio

# Add the mcp-doffin directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-doffin'))

from mcp_doffin import main, fetch, parse_search, parse_notice, BASE


class TestMCPServerIntegration:
    """Integration tests for MCP server tools."""
    
    @pytest.mark.asyncio
    async def test_search_notices_tool_with_mock(self, httpx_mock, sample_search_html):
        """Test search_notices tool with mocked HTTP response."""
        # Mock the doffin.no search endpoint
        search_url = f"{BASE}/search?query=software"
        httpx_mock.add_response(
            method="GET",
            url=search_url,
            text=sample_search_html,
            status_code=200
        )
        
        # Import and create server instance
        from mcp.server.fastmcp import FastMCP
        server = FastMCP("test-server")
        
        # We need to manually set up the tools since we can't easily test the decorator
        # Instead, we'll test the underlying functions
        from mcp_doffin import build_search_url, parse_search
        
        # Test the URL building
        params = {"q": "software"}
        url = build_search_url(params)
        
        # Test the fetch and parse
        html = await fetch(url)
        results = parse_search(html)
        
        assert len(results) == 1
        assert results[0]["title"] == "Test Procurement Notice"
        assert results[0]["notice_id"] == "12345"

    @pytest.mark.asyncio
    async def test_get_notice_tool_with_mock(self, httpx_mock, sample_notice_html):
        """Test get_notice tool with mocked HTTP response."""
        notice_id = "12345"
        notice_url = f"{BASE}/notices/{notice_id}"
        
        httpx_mock.add_response(
            method="GET",
            url=notice_url,
            text=sample_notice_html,
            status_code=200
        )
        
        # Test the fetch and parse
        from mcp_doffin import parse_notice
        html = await fetch(notice_url)
        result = parse_notice(html, notice_url)
        
        assert result["source_url"] == notice_url
        assert result["title"] == "Test Procurement Notice"
        assert result["buyer"] == "Oslo Kommune"
        assert len(result["attachments"]) >= 1

    @pytest.mark.asyncio
    async def test_search_notices_error_handling(self, httpx_mock):
        """Test error handling in search_notices tool."""
        search_url = f"{BASE}/search?query=test"
        
        # Mock a server error - need to add multiple responses for retries
        for _ in range(3):  # Match the retry attempts in tenacity
            httpx_mock.add_response(
                method="GET",
                url=search_url,
                status_code=500
            )
        
        # Test that fetch raises an exception on HTTP error
        with pytest.raises(Exception):
            await fetch(search_url)

    @pytest.mark.asyncio
    async def test_get_notice_error_handling(self, httpx_mock):
        """Test error handling in get_notice tool."""
        notice_url = f"{BASE}/notices/nonexistent"
        
        # Mock a 404 error - need multiple responses for retries
        for _ in range(3):
            httpx_mock.add_response(
                method="GET",
                url=notice_url,
                status_code=404
            )
        
        # Test that fetch raises an exception on HTTP error
        with pytest.raises(Exception):
            await fetch(notice_url)


class TestToolFunctions:
    """Test the individual tool functions that would be called by MCP."""
    
    @pytest.mark.asyncio
    async def test_search_tool_function(self, httpx_mock, sample_search_html):
        """Test the search tool function logic."""
        # Create a mock search function similar to what the MCP tool would do
        async def mock_search_notices(
            q=None, cpv=None, buyer=None, published_from=None, 
            published_to=None, deadline_to=None, county=None, 
            procedure=None, page=1
        ):
            from mcp_doffin import build_search_url, fetch, parse_search
            
            args = {
                "q": q, "cpv": cpv, "buyer": buyer, 
                "published_from": published_from, "published_to": published_to,
                "deadline_to": deadline_to, "county": county, 
                "procedure": procedure, "page": page
            }
            url = build_search_url(args)
            html = await fetch(url)
            return {"results": parse_search(html), "source_url": url}
        
        # Mock the HTTP response
        httpx_mock.add_response(
            method="GET",
            url=f"{BASE}/search?query=software&buyer=Oslo+Kommune",
            text=sample_search_html,
            status_code=200
        )
        
        # Call the function
        result = await mock_search_notices(
            q="software", 
            buyer="Oslo Kommune"
        )
        
        assert "results" in result
        assert "source_url" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test Procurement Notice"

    @pytest.mark.asyncio
    async def test_get_notice_tool_function(self, httpx_mock, sample_notice_html):
        """Test the get notice tool function logic."""
        # Create a mock get notice function
        async def mock_get_notice(notice_id=None, url=None):
            from mcp_doffin import fetch, parse_notice, BASE
            
            if not notice_id and not url:
                raise ValueError("Either notice_id or url must be provided")
            
            target_url = url or f"{BASE}/notices/{notice_id}"
            html = await fetch(target_url)
            return parse_notice(html, target_url)
        
        # Mock the HTTP response - only add what we need
        notice_url = f"{BASE}/notices/12345"
        httpx_mock.add_response(
            method="GET",
            url=notice_url,
            text=sample_notice_html,
            status_code=200
        )
        
        # Test with notice_id
        result = await mock_get_notice(notice_id="12345")
        assert result["source_url"] == notice_url
        assert result["title"] == "Test Procurement Notice"
        
        # Don't test with URL separately to avoid unused mocks
        # Instead just test error case
        with pytest.raises(ValueError):
            await mock_get_notice()

    @pytest.mark.asyncio
    async def test_complex_search_parameters(self, httpx_mock):
        """Test search with complex parameters."""
        from mcp_doffin import build_search_url, fetch, parse_search
        
        # Mock a search with multiple parameters
        complex_params = {
            "q": "software development",
            "cpv": ["72000000-5", "48000000-8"],
            "buyer": "Oslo Kommune",
            "published_from": "2024-01-01",
            "published_to": "2024-12-31",
            "deadline_to": "2024-06-30",
            "county": "Oslo",
            "procedure": "open",
            "page": 2
        }
        
        url = build_search_url(complex_params)
        
        # Verify URL contains all parameters
        assert "query=software+development" in url
        assert "cpvCodesLabel=72000000-5%2C48000000-8" in url
        assert "buyer=Oslo+Kommune" in url
        assert "publishedFrom=2024-01-01" in url
        assert "publishedTo=2024-12-31" in url
        assert "deadlineTo=2024-06-30" in url
        assert "county=Oslo" in url
        assert "procedure=open" in url
        assert "page=2" in url
        
        # Mock the response
        mock_html = """
        <div class="notice-card">
            <h3 class="notice-title">Complex Search Result</h3>
            <a href="/notices/67890">View Details</a>
            <div class="notice-buyer">Oslo Kommune</div>
        </div>
        """
        
        httpx_mock.add_response(
            method="GET",
            url=url,
            text=mock_html,
            status_code=200
        )
        
        html = await fetch(url)
        results = parse_search(html)
        
        assert len(results) == 1
        assert results[0]["title"] == "Complex Search Result"
        assert results[0]["notice_id"] == "67890"


class TestRetryBehavior:
    """Test retry behavior of the fetch function."""
    
    @pytest.mark.asyncio
    async def test_fetch_retry_success_on_second_attempt(self, httpx_mock):
        """Test that fetch retries and succeeds on second attempt."""
        url = f"{BASE}/test"
        
        # First request fails, second succeeds
        httpx_mock.add_response(
            method="GET",
            url=url,
            status_code=500
        )
        httpx_mock.add_response(
            method="GET",
            url=url,
            text="Success after retry",
            status_code=200
        )
        
        result = await fetch(url)
        assert result == "Success after retry"

    @pytest.mark.asyncio
    async def test_fetch_retry_exhaustion(self, httpx_mock):
        """Test that fetch fails after all retries are exhausted."""
        url = f"{BASE}/test"
        
        # All 3 attempts fail
        for _ in range(3):
            httpx_mock.add_response(
                method="GET",
                url=url,
                status_code=500
            )
        
        with pytest.raises(Exception):
            await fetch(url)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self, httpx_mock):
        """Test handling of empty search results."""
        from mcp_doffin import build_search_url, fetch, parse_search
        
        url = build_search_url({"q": "nonexistent"})
        
        # Mock empty search results
        empty_html = "<div>No results found</div>"
        httpx_mock.add_response(
            method="GET",
            url=url,
            text=empty_html,
            status_code=200
        )
        
        html = await fetch(url)
        results = parse_search(html)
        
        assert results == []

    @pytest.mark.asyncio
    async def test_malformed_html_handling(self, httpx_mock):
        """Test handling of malformed HTML."""
        from mcp_doffin import parse_search, parse_notice
        
        malformed_html = "<div><span>Unclosed tags<div>"
        
        # Should not crash on malformed HTML
        results = parse_search(malformed_html)
        assert results == []
        
        notice_result = parse_notice(malformed_html, "http://test.com")
        assert notice_result["source_url"] == "http://test.com"

    def test_url_encoding_special_characters(self):
        """Test that special characters in search parameters are properly encoded."""
        from mcp_doffin import build_search_url
        
        params = {
            "q": "software & hardware",
            "buyer": "Østfold Kommune"
        }
        
        url = build_search_url(params)
        
        # Check that special characters are properly encoded
        assert "software+%26+hardware" in url or "software%20%26%20hardware" in url
        assert "%C3%98stfold" in url or "Østfold" in url  # URL encoding may vary