"""
Example: Interactive Python REPL Session

This example demonstrates how to use tmux-mcp to interact with a Python REPL.
"""

# Example workflow that an LLM might follow:

# 1. Start a Python REPL session
# Tool: tmux_start_session
# Arguments: {
#   "session_name": "python_calc",
#   "program": "python",
#   "args": ["-i"]
# }

# 2. Import required modules
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": "import math"
# }

# 3. Read the current output to see the result
# Tool: tmux_read_output
# Arguments: {
#   "session_name": "python_calc"
# }

# 4. Perform calculations
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc", 
#   "command": "radius = 5"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": "area = math.pi * radius ** 2"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": "print(f'Area of circle with radius {radius}: {area:.2f}')"
# }

# 5. Read the final output
# Tool: tmux_read_output
# Arguments: {
#   "session_name": "python_calc"
# }

# 6. Define a function interactively
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": "def calculate_circle_area(r):"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": "    return math.pi * r ** 2"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": ""  # Empty line to finish function definition
# }

# 7. Use the function
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": "areas = [calculate_circle_area(r) for r in range(1, 6)]"
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "python_calc",
#   "command": "print('Circle areas:', areas)"
# }

# 8. Exit the REPL
# Tool: tmux_send_key
# Arguments: {
#   "session_name": "python_calc",
#   "key": "C-d"  # Ctrl+D to exit
# }

# 9. Clean up the session
# Tool: tmux_kill_session
# Arguments: {
#   "session_name": "python_calc"
# }
