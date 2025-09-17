# Getting Started with Doffin MCP Server

This guide walks you through setting up the Doffin MCP Server from scratch, even if you've never used MCP before.

## What You'll Need

Before starting, make sure you have:
- **Python 3.11 or later** installed on your computer
- **Claude Desktop** installed (download from [claude.ai](https://claude.ai))
- **Basic command line knowledge** (we'll guide you through the commands)
- **Internet connection** (the server fetches data from doffin.no)

## Step-by-Step Setup

### Step 1: Check Your Python Installation

Open your terminal/command prompt and check if Python is installed:

```bash
python3 --version
```

You should see something like `Python 3.11.x` or higher. If not, install Python from [python.org](https://python.org).

### Step 2: Download the Code

Clone this repository to your computer:

```bash
# Navigate to where you want to store the code
cd ~/Documents  # or wherever you prefer

# Clone the repository
git clone https://github.com/yourusername/doffin-mcp.git
cd doffin-mcp/mcp-doffin
```

### Step 3: Create an Isolated Python Environment

This keeps the server's dependencies separate from your other Python projects:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Activate it (Windows)
# .venv\Scripts\activate
```

You'll see `(.venv)` appear in your terminal prompt when activated.

### Step 4: Install Dependencies

With the virtual environment activated, install required packages:

```bash
pip install -r requirements.txt
```

This will install the MCP framework and web scraping libraries.

### Step 5: Test the Server

Make sure everything works by running the server manually:

```bash
python mcp_doffin.py
```

The server should start without errors. Press `Ctrl+C` to stop it.

### Step 6: Configure Claude Desktop

Now you need to tell Claude Desktop how to find and run your MCP server.

#### Find Your Absolute Paths

First, get the full paths we'll need:

```bash
# Get the path to your Python executable
which python
# Example output: /Users/yourusername/Documents/doffin-mcp/mcp-doffin/.venv/bin/python

# Get the path to the server script
pwd
ls mcp_doffin.py
# This confirms the file exists in your current directory
```

#### Create the Configuration File

**macOS/Linux users:** Create the file `~/.claude/mcp-servers/doffin.json`

**Windows users:** Create the file `%UserProfile%\.claude\mcp-servers\doffin.json`

```bash
# Create the directory if it doesn't exist (macOS/Linux)
mkdir -p ~/.claude/mcp-servers

# Create the configuration file (replace with your actual paths!)
cat > ~/.claude/mcp-servers/doffin.json << 'EOF'
{
  "command": "/Users/yourusername/Documents/doffin-mcp/mcp-doffin/.venv/bin/python",
  "args": ["/Users/yourusername/Documents/doffin-mcp/mcp-doffin/mcp_doffin.py"],
  "env": {
    "NO_COLOR": "1"
  }
}
EOF
```

**⚠️ IMPORTANT:** Replace the paths in the JSON with your actual paths from the previous step!

### Step 7: Restart Claude Desktop

Completely quit Claude Desktop and reopen it. The server should now be available.

### Step 8: Test It Out!

Open a new conversation in Claude Desktop and try:

```
Search for procurement notices from Oslo published in the last 7 days
```

or

```
Find all notices with "API" in the description
```

If Claude responds with actual procurement data, congratulations! Your MCP server is working.

## What Just Happened?

You've successfully set up a bridge between Claude Desktop and the Norwegian procurement system. Here's what the components do:

- **MCP Server** (`mcp_doffin.py`): A Python program that fetches data from doffin.no
- **Configuration file** (`doffin.json`): Tells Claude Desktop how to start your server
- **Virtual environment** (`.venv/`): Keeps the server's dependencies isolated

## Next Steps

Now that it's working, you can:

- **Explore the tools**: Try different search filters and parameters
- **Read the documentation**: Check out the other guides in this repository
- **Develop locally**: Modify the server to add new features
- **Deploy with Docker**: Use the containerized version for enhanced security

## Troubleshooting

### Server Doesn't Appear in Claude Desktop

1. **Check your paths**: Make sure the paths in `doffin.json` are correct and absolute
2. **Check file permissions**: Ensure the Python executable and script are readable
3. **Restart completely**: Quit Claude Desktop entirely and reopen
4. **Check the logs**: Look for error messages in Claude Desktop's logs

### Python or Command Errors

1. **Virtual environment**: Make sure it's activated (`(.venv)` in prompt)
2. **Python version**: Verify you have Python 3.11+ with `python --version`
3. **Dependencies**: Reinstall with `pip install -r requirements.txt`

### Tool Calls Failing

1. **Test manually**: Run `python mcp_doffin.py` and check for errors
2. **Internet connection**: The server needs to access doffin.no
3. **Rate limiting**: Wait a few minutes if you've made many requests

### Still Having Issues?

1. Check the main [README.md](README.md) for additional troubleshooting
2. Review the [testing documentation](tests/README.md)
3. Open an issue on GitHub with details about your setup and error messages

## Understanding MCP

The Model Context Protocol (MCP) is a standard way for AI assistants to securely access external data and tools. This server:

1. **Receives requests** from Claude Desktop via MCP
2. **Fetches data** from doffin.no public APIs
3. **Returns structured data** back to Claude
4. **Respects rate limits** to be a good citizen

Your Claude Desktop client can now seamlessly access Norwegian procurement data as if it were part of Claude's built-in knowledge!