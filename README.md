# tmux-mcp

A Model Context Protocol (MCP) server that provides Claude and other LLMs with access to interactive CLI programs through tmux sessions. This allows LLMs to interact with terminal-based applications like Python/Node REPLs, Vim, games, and more.

## Features

- **Start Sessions**: Launch any CLI program in a tmux session
- **Send Commands**: Send text input and special keys to running programs  
- **Read Output**: Capture the current terminal output
- **Session Management**: List and kill active sessions
- **Resource Access**: Access session state via MCP resources

## Installation

### Prerequisites

1. **tmux** must be installed:
   ```bash
   # On macOS
   brew install tmux
   
   # On Ubuntu/Debian
   sudo apt-get install tmux
   
   # On other systems
   # Check your package manager
   ```

2. **Python 3.10+** and **uv** (recommended) or pip

### Install with uv (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/tmux-mcp.git
cd tmux-mcp

# Install dependencies and sync virtual environment
uv sync

# Verify installation
uv run tmux-mcp --help
```

### Install with pip

```bash
# Clone the repository  
git clone https://github.com/yourusername/tmux-mcp.git
cd tmux-mcp

# Install with pip
pip install -e .
```

## Usage

### Running the Server

#### Standalone Mode

```bash
# With uv
uv run tmux-mcp

# Or if installed globally
tmux-mcp
```

#### With MCP Inspector (for testing)

```bash
npx @modelcontextprotocol/inspector uv run tmux-mcp
```

**Note**: Before configuring Claude Desktop, test that the server starts correctly by running `uv run tmux-mcp`. You should see a startup message like "Starting tmux-mcp server...". If you get import errors, run `uv sync` first.

#### Configure with Claude Desktop

**Step 1: Locate your Claude Desktop config file**

The configuration file location depends on your operating system:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**Step 2: Add tmux-mcp to your configuration**

Add this to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "tmux": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/path/to/tmux-mcp/tmux_mcp/server.py"
      ]
    }
  }
}
```

Replace `/path/to/tmux-mcp` with the actual path to your tmux-mcp directory.

**Alternative configuration (if installed globally):**

If you have tmux-mcp installed globally and want to use the direct execution method:

```json
{
  "mcpServers": {
    "tmux": {
      "command": "uv",
      "args": ["run", "tmux-mcp"],
      "cwd": "/path/to/tmux-mcp"
    }
  }
}
```

**Step 3: Restart Claude Desktop**

After saving the configuration, restart Claude Desktop for the changes to take effect.

## Available Tools

### `tmux_start_session`
Start a new tmux session with an interactive program.

**Parameters:**
- `session_name` (required): Name for the tmux session
- `program` (required): CLI program to run (e.g., 'python', 'node', 'vim')
- `args` (optional): Array of arguments to pass to the program

**Example:**
```json
{
  "session_name": "python_repl",
  "program": "python",
  "args": ["-i"]
}
```

### `tmux_send_command`
Send text input to a running session.

**Parameters:**
- `session_name` (required): Target session name
- `command` (required): Text to send
- `press_enter` (optional): Whether to press Enter after (default: true)

**Example:**
```json
{
  "session_name": "python_repl",
  "command": "print('Hello, World!')"
}
```

### `tmux_read_output`
Read the current terminal output from a session.

**Parameters:**
- `session_name` (required): Target session name
- `lines` (optional): Number of lines from the end (default: all visible)

**Example:**
```json
{
  "session_name": "python_repl",
  "lines": 50
}
```

### `tmux_send_key`
Send special keys like Ctrl+C, Tab, Arrow keys, etc.

**Parameters:**
- `session_name` (required): Target session name
- `key` (required): Key to send

**Common keys:**
- `C-c`: Ctrl+C (interrupt)
- `C-d`: Ctrl+D (EOF)  
- `Tab`: Tab completion
- `Escape`: Escape key
- `Up`, `Down`, `Left`, `Right`: Arrow keys
- `Enter`: Enter key
- `Space`: Space key

**Example:**
```json
{
  "session_name": "vim_editor",
  "key": "Escape"
}
```

### `tmux_list_sessions`
List all active tmux sessions managed by this server.

No parameters required.

### `tmux_kill_session`
Terminate a tmux session.

**Parameters:**
- `session_name` (required): Session to kill

## Example Interactions

### Python REPL Session

1. Start a Python session:
   ```
   Tool: tmux_start_session
   Args: {"session_name": "py", "program": "python"}
   ```

2. Send a command:
   ```
   Tool: tmux_send_command
   Args: {"session_name": "py", "command": "import math"}
   ```

3. Read the output:
   ```
   Tool: tmux_read_output
   Args: {"session_name": "py"}
   ```

4. More commands:
   ```
   Tool: tmux_send_command
   Args: {"session_name": "py", "command": "math.pi * 2"}
   ```

### Vim Editor Session

1. Start Vim:
   ```
   Tool: tmux_start_session
   Args: {"session_name": "editor", "program": "vim", "args": ["test.py"]}
   ```

2. Enter insert mode:
   ```
   Tool: tmux_send_key
   Args: {"session_name": "editor", "key": "i"}
   ```

3. Type some code:
   ```
   Tool: tmux_send_command
   Args: {"session_name": "editor", "command": "def hello():", "press_enter": true}
   Tool: tmux_send_command  
   Args: {"session_name": "editor", "command": "    print('Hello!')", "press_enter": false}
   ```

4. Exit insert mode and save:
   ```
   Tool: tmux_send_key
   Args: {"session_name": "editor", "key": "Escape"}
   Tool: tmux_send_command
   Args: {"session_name": "editor", "command": ":wq"}
   ```

### Interactive Game Session

1. Start a game:
   ```
   Tool: tmux_start_session
   Args: {"session_name": "game", "program": "nethack"}
   ```

2. Send game commands:
   ```
   Tool: tmux_send_command
   Args: {"session_name": "game", "command": "h"}  // Move left
   ```

3. Read game state:
   ```
   Tool: tmux_read_output
   Args: {"session_name": "game"}
   ```

## Resources

The server also exposes MCP resources for each active session:

- URI format: `tmux://session/{session_name}`
- Returns the current terminal output for the session

## Tips

1. **Session Names**: Use descriptive session names to track multiple programs
2. **Special Keys**: Use `tmux_send_key` for control sequences and special keys
3. **Reading Output**: The output includes the entire visible terminal buffer
4. **Cleanup**: Remember to kill sessions when done to free resources

## Troubleshooting

### "Connection error" or "Server failed to start" in Claude Desktop

**Common causes and solutions:**

1. **Wrong configuration pattern**: Use the MCP CLI pattern for most reliable operation:
   ```json
   "command": "uv",
   "args": ["run", "--with", "mcp[cli]", "mcp", "run", "/path/to/tmux-mcp/tmux_mcp/server.py"]
   ```

2. **Dependencies not installed**: Run `uv sync` in the project directory to ensure all dependencies are installed.

3. **Test the server**: Run `uv run tmux-mcp` in the project directory (should show startup message).

4. **Restart Claude Desktop** after making configuration changes.

### "tmux is not installed"
Install tmux using your system's package manager.

### "Session already exists"  
Either kill the existing session or use a different name.

### Commands not working
- Check the session is still active with `tmux_list_sessions`
- Try reading the output to see the current state
- Some programs may need specific key sequences or timing

### "ImportError: No module named 'mcp'"
Run `uv sync` in the project directory to install all dependencies.

## Development

### Running Tests
```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing
Pull requests are welcome! Please ensure:
- Code follows Python conventions
- New features include tests
- Documentation is updated

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Inspired by the approach in [claude-code-plays-cave](https://github.com/brendanlong/claude-code-plays-cave) which demonstrated using tmux for LLM interaction with terminal programs.
