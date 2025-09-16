#!/usr/bin/env python3
"""
Basic MCP Server Example

This example demonstrates a simple but robust MCP server implementation
following the best practices outlined in the doffin-mcp documentation.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional

# Note: This is a conceptual example. In practice, you would use an actual MCP SDK
# For demonstration purposes, we'll create mock classes that show the structure

class MockMCPServer:
    """Mock MCP server for demonstration purposes."""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.logger = logging.getLogger(f"mcp-server-{name}")
    
    def add_tool(self, tool):
        """Register a tool with the server."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    async def start(self, host: str = "localhost", port: int = 8000):
        """Start the MCP server."""
        self.logger.info(f"Starting MCP server '{self.name}' on {host}:{port}")
        # In a real implementation, this would start the actual server
        await asyncio.sleep(0.1)  # Simulate startup time
        self.logger.info("Server started successfully")

class MockTool:
    """Mock tool for demonstration purposes."""
    
    def __init__(self, name: str, description: str, handler, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.handler = handler
        self.input_schema = input_schema

class DoffinMCPServer:
    """
    Example MCP server implementation for doffin-mcp.
    
    This server provides basic tools for file operations and data processing,
    demonstrating best practices for error handling, validation, and logging.
    """
    
    def __init__(self):
        self.server = MockMCPServer("doffin-mcp-example")
        self.logger = logging.getLogger("doffin-mcp-server")
        self.setup_logging()
        self.setup_tools()
    
    def setup_logging(self):
        """Configure logging for the server."""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def setup_tools(self):
        """Register all available tools."""
        # File reader tool
        self.server.add_tool(MockTool(
            name="file_reader",
            description="Read file contents safely with size limits",
            handler=self.handle_file_reader,
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "encoding": {"type": "string", "default": "utf-8"},
                    "max_size": {"type": "integer", "default": 1048576}  # 1MB
                },
                "required": ["path"]
            }
        ))
        
        # Data processor tool
        self.server.add_tool(MockTool(
            name="data_processor",
            description="Process data in various formats",
            handler=self.handle_data_processor,
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "string"},
                    "format": {"type": "string", "enum": ["json", "csv", "text"]},
                    "operation": {"type": "string", "enum": ["validate", "transform", "analyze"]}
                },
                "required": ["data", "format", "operation"]
            }
        ))
        
        # Text analyzer tool
        self.server.add_tool(MockTool(
            name="text_analyzer",
            description="Analyze text content for insights",
            handler=self.handle_text_analyzer,
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "analysis_type": {"type": "string", "enum": ["sentiment", "keywords", "summary"]}
                },
                "required": ["text", "analysis_type"]
            }
        ))
    
    async def handle_file_reader(self, path: str, encoding: str = "utf-8", max_size: int = 1048576):
        """
        Handle file reading requests with safety checks.
        
        Args:
            path: File path to read
            encoding: Text encoding (default: utf-8)
            max_size: Maximum file size in bytes (default: 1MB)
        
        Returns:
            Dict containing success status and file content or error message
        """
        try:
            # Validate path safety
            if not self._is_safe_path(path):
                return {
                    "success": False,
                    "error": "Unsafe file path detected",
                    "details": "Path contains dangerous patterns"
                }
            
            # Check if file exists (mock implementation)
            if not self._file_exists(path):
                return {
                    "success": False,
                    "error": "File not found",
                    "path": path
                }
            
            # Check file size (mock implementation)
            file_size = self._get_file_size(path)
            if file_size > max_size:
                return {
                    "success": False,
                    "error": "File too large",
                    "size": file_size,
                    "max_size": max_size
                }
            
            # Read file content (mock implementation)
            content = self._read_file_content(path, encoding)
            
            self.logger.info(f"Successfully read file: {path} ({file_size} bytes)")
            
            return {
                "success": True,
                "content": content,
                "path": path,
                "size": file_size,
                "encoding": encoding
            }
            
        except UnicodeDecodeError as e:
            self.logger.error(f"Encoding error reading {path}: {e}")
            return {
                "success": False,
                "error": "Encoding error",
                "details": str(e)
            }
        except Exception as e:
            self.logger.error(f"Unexpected error reading {path}: {e}")
            return {
                "success": False,
                "error": "Internal server error",
                "details": str(e)
            }
    
    async def handle_data_processor(self, data: str, format: str, operation: str):
        """
        Handle data processing requests.
        
        Args:
            data: Input data to process
            format: Data format (json, csv, text)
            operation: Operation to perform (validate, transform, analyze)
        
        Returns:
            Dict containing processing results
        """
        try:
            # Validate input data
            if not data.strip():
                return {
                    "success": False,
                    "error": "Empty data provided"
                }
            
            # Process based on format and operation
            result = await self._process_data(data, format, operation)
            
            self.logger.info(f"Successfully processed {format} data with {operation} operation")
            
            return {
                "success": True,
                "result": result,
                "format": format,
                "operation": operation,
                "input_size": len(data)
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {
                "success": False,
                "error": "Invalid JSON format",
                "details": str(e)
            }
        except Exception as e:
            self.logger.error(f"Data processing error: {e}")
            return {
                "success": False,
                "error": "Processing failed",
                "details": str(e)
            }
    
    async def handle_text_analyzer(self, text: str, analysis_type: str):
        """
        Handle text analysis requests.
        
        Args:
            text: Text content to analyze
            analysis_type: Type of analysis (sentiment, keywords, summary)
        
        Returns:
            Dict containing analysis results
        """
        try:
            if not text.strip():
                return {
                    "success": False,
                    "error": "Empty text provided"
                }
            
            # Perform analysis based on type
            analysis_result = await self._analyze_text(text, analysis_type)
            
            self.logger.info(f"Successfully analyzed text: {analysis_type} analysis")
            
            return {
                "success": True,
                "analysis": analysis_result,
                "analysis_type": analysis_type,
                "text_length": len(text),
                "word_count": len(text.split())
            }
            
        except Exception as e:
            self.logger.error(f"Text analysis error: {e}")
            return {
                "success": False,
                "error": "Analysis failed",
                "details": str(e)
            }
    
    def _is_safe_path(self, path: str) -> bool:
        """Check if file path is safe to access."""
        # Prevent directory traversal
        if ".." in path or path.startswith("/"):
            return False
        
        # Check against allowed directories (in real implementation)
        allowed_prefixes = ["./data/", "./uploads/", "/tmp/"]
        return any(path.startswith(prefix) for prefix in allowed_prefixes)
    
    def _file_exists(self, path: str) -> bool:
        """Mock file existence check."""
        # In real implementation, use os.path.exists(path)
        return True  # Assume file exists for demo
    
    def _get_file_size(self, path: str) -> int:
        """Mock file size check."""
        # In real implementation, use os.path.getsize(path)
        return 1024  # Return 1KB for demo
    
    def _read_file_content(self, path: str, encoding: str) -> str:
        """Mock file content reading."""
        # In real implementation:
        # with open(path, 'r', encoding=encoding) as f:
        #     return f.read()
        return f"Mock content from {path} (encoding: {encoding})"
    
    async def _process_data(self, data: str, format: str, operation: str) -> Dict[str, Any]:
        """Process data based on format and operation."""
        processors = {
            "json": self._process_json,
            "csv": self._process_csv,
            "text": self._process_text
        }
        
        processor = processors.get(format, self._process_text)
        return await processor(data, operation)
    
    async def _process_json(self, data: str, operation: str) -> Dict[str, Any]:
        """Process JSON data."""
        parsed_data = json.loads(data)  # Will raise JSONDecodeError if invalid
        
        if operation == "validate":
            return {"valid": True, "structure": type(parsed_data).__name__}
        elif operation == "transform":
            # Example transformation: flatten if it's a dict
            if isinstance(parsed_data, dict):
                return {"transformed": True, "keys": list(parsed_data.keys())}
            return {"transformed": False, "reason": "Not a dictionary"}
        elif operation == "analyze":
            return {
                "type": type(parsed_data).__name__,
                "size": len(str(parsed_data)),
                "keys": list(parsed_data.keys()) if isinstance(parsed_data, dict) else None
            }
    
    async def _process_csv(self, data: str, operation: str) -> Dict[str, Any]:
        """Process CSV data."""
        lines = data.strip().split('\n')
        
        if operation == "validate":
            return {"valid": True, "rows": len(lines)}
        elif operation == "transform":
            return {"rows": len(lines), "columns": len(lines[0].split(',')) if lines else 0}
        elif operation == "analyze":
            return {
                "rows": len(lines),
                "estimated_columns": len(lines[0].split(',')) if lines else 0,
                "size": len(data)
            }
    
    async def _process_text(self, data: str, operation: str) -> Dict[str, Any]:
        """Process plain text data."""
        words = data.split()
        
        if operation == "validate":
            return {"valid": True, "text_length": len(data)}
        elif operation == "transform":
            return {"word_count": len(words), "uppercase": data.upper()[:100]}  # First 100 chars
        elif operation == "analyze":
            return {
                "character_count": len(data),
                "word_count": len(words),
                "line_count": len(data.split('\n')),
                "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
            }
    
    async def _analyze_text(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Analyze text content."""
        if analysis_type == "sentiment":
            # Mock sentiment analysis
            return {
                "sentiment": "neutral",
                "confidence": 0.75,
                "positive_score": 0.4,
                "negative_score": 0.3,
                "neutral_score": 0.3
            }
        elif analysis_type == "keywords":
            # Mock keyword extraction
            words = text.lower().split()
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top 5 most frequent words
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "keywords": [word for word, count in top_keywords],
                "keyword_scores": dict(top_keywords),
                "total_unique_words": len(word_freq)
            }
        elif analysis_type == "summary":
            # Mock text summarization
            sentences = text.split('.')
            return {
                "summary": f"Text contains {len(sentences)} sentences with {len(text.split())} words.",
                "key_points": [
                    "Main topic discussed",
                    "Supporting details provided", 
                    "Conclusion reached"
                ],
                "readability": "moderate"
            }
    
    async def start_server(self, host: str = "localhost", port: int = 8000):
        """Start the MCP server."""
        try:
            await self.server.start(host, port)
            self.logger.info("Doffin MCP Server is ready to handle requests")
            
            # Keep server running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Server shutdown requested")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise

async def main():
    """Main function to run the server."""
    server = DoffinMCPServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server failed to start: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Starting Doffin MCP Server Example...")
    print("Press Ctrl+C to stop the server")
    
    asyncio.run(main())