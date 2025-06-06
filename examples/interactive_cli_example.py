"""
Example: Interactive CLI Game Session

This example demonstrates how to use tmux-mcp to interact with terminal-based games
or other interactive CLI programs.
"""

# Example 1: Python's interactive turtle graphics
# (Note: This requires a terminal that supports graphics)

# Tool: tmux_start_session
# Arguments: {
#   "session_name": "turtle_demo",
#   "program": "python",
#   "args": ["-i"]
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "turtle_demo",
#   "command": "import turtle"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "turtle_demo",
#   "command": "t = turtle.Turtle()"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "turtle_demo",
#   "command": "for i in range(4): t.forward(100); t.right(90)"
# }

# Example 2: Interactive Node.js REPL

# Tool: tmux_start_session
# Arguments: {
#   "session_name": "node_repl",
#   "program": "node"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "node_repl",
#   "command": "const readline = require('readline')"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "node_repl",
#   "command": "console.log('Node.js version:', process.version)"
# }

# Example 3: Interactive debugging session with Python's pdb

# First, create a file with a bug
# Tool: tmux_start_session
# Arguments: {
#   "session_name": "debug_session",
#   "program": "bash"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "cat > buggy.py << 'EOF'"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "def divide(a, b):"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "    return a / b"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": ""
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "result = divide(10, 0)"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "print(result)"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "EOF"
# }

# Now debug it
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "python -m pdb buggy.py"
# }

# Set a breakpoint
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "b divide"
# }

# Continue execution
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "c"
# }

# Step through the code
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "n"
# }

# Inspect variables
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "debug_session",
#   "command": "p b"
# }

# Example 4: Interactive git commit session

# Tool: tmux_start_session
# Arguments: {
#   "session_name": "git_interactive",
#   "program": "bash"
# }

# Create a test repository
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "git_interactive",
#   "command": "mkdir test_repo && cd test_repo && git init"
# }

# Create a file
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "git_interactive",
#   "command": "echo 'Hello World' > README.md"
# }

# Add and commit interactively
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "git_interactive",
#   "command": "git add -i"
# }

# Navigate the interactive menu
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "git_interactive",
#   "command": "a"  # Add untracked
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "git_interactive",
#   "command": "1"  # Select file
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "git_interactive",
#   "command": ""  # Confirm
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "git_interactive",
#   "command": "q"  # Quit interactive mode
# }

# Example 5: Using special keys in interactive programs

# For programs that use arrow keys for navigation:
# Tool: tmux_send_key
# Arguments: {"session_name": "my_session", "key": "Up"}
# Arguments: {"session_name": "my_session", "key": "Down"}
# Arguments: {"session_name": "my_session", "key": "Left"}
# Arguments: {"session_name": "my_session", "key": "Right"}

# For programs that use function keys:
# Tool: tmux_send_key
# Arguments: {"session_name": "my_session", "key": "F1"}
# Arguments: {"session_name": "my_session", "key": "F2"}

# For programs that use Tab completion:
# Tool: tmux_send_key
# Arguments: {"session_name": "my_session", "key": "Tab"}

# To send Ctrl combinations:
# Tool: tmux_send_key
# Arguments: {"session_name": "my_session", "key": "C-a"}  # Ctrl+A
# Arguments: {"session_name": "my_session", "key": "C-x"}  # Ctrl+X
# Arguments: {"session_name": "my_session", "key": "C-z"}  # Ctrl+Z (suspend)

# Page navigation:
# Tool: tmux_send_key
# Arguments: {"session_name": "my_session", "key": "PageUp"}
# Arguments: {"session_name": "my_session", "key": "PageDown"}
# Arguments: {"session_name": "my_session", "key": "Home"}
# Arguments: {"session_name": "my_session", "key": "End"}
