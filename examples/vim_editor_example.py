"""
Example: Vim Editor Session

This example demonstrates how to use tmux-mcp to interact with Vim for editing code.
"""

# Example workflow for creating and editing a Python script in Vim:

# 1. Start Vim with a new file
# Tool: tmux_start_session
# Arguments: {
#   "session_name": "vim_editor",
#   "program": "vim",
#   "args": ["hello_world.py"]
# }

# 2. Wait a moment for Vim to load, then read the initial state
# Tool: tmux_read_output
# Arguments: {
#   "session_name": "vim_editor"
# }

# 3. Enter insert mode
# Tool: tmux_send_key
# Arguments: {
#   "session_name": "vim_editor",
#   "key": "i"
# }

# 4. Write a Python script
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "#!/usr/bin/env python3",
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": '"""A simple hello world program"""',
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "",
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "def main():",
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "    print('Hello, World!')",
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "    print('This file was created using tmux-mcp!')",
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "",
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "if __name__ == '__main__':",
#   "press_enter": true
# }

# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": "    main()",
#   "press_enter": false
# }

# 5. Exit insert mode
# Tool: tmux_send_key
# Arguments: {
#   "session_name": "vim_editor",
#   "key": "Escape"
# }

# 6. Save the file
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": ":w",
#   "press_enter": true
# }

# 7. Read the output to confirm save
# Tool: tmux_read_output
# Arguments: {
#   "session_name": "vim_editor"
# }

# 8. Run the script within Vim
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": ":!python3 %",
#   "press_enter": true
# }

# 9. Press Enter to return to Vim after seeing the output
# Tool: tmux_send_key
# Arguments: {
#   "session_name": "vim_editor",
#   "key": "Enter"
# }

# 10. Quit Vim
# Tool: tmux_send_command
# Arguments: {
#   "session_name": "vim_editor",
#   "command": ":q",
#   "press_enter": true
# }

# 11. Clean up the session
# Tool: tmux_kill_session
# Arguments: {
#   "session_name": "vim_editor"
# }

# Additional Vim navigation examples:

# Go to line 5:
# Tool: tmux_send_command
# Arguments: {"session_name": "vim_editor", "command": ":5", "press_enter": true}

# Search for text:
# Tool: tmux_send_command
# Arguments: {"session_name": "vim_editor", "command": "/main", "press_enter": true}

# Navigate with arrow keys:
# Tool: tmux_send_key
# Arguments: {"session_name": "vim_editor", "key": "Down"}
# Arguments: {"session_name": "vim_editor", "key": "Up"}
# Arguments: {"session_name": "vim_editor", "key": "Left"}
# Arguments: {"session_name": "vim_editor", "key": "Right"}

# Visual mode selection:
# Tool: tmux_send_key
# Arguments: {"session_name": "vim_editor", "key": "v"}  # Enter visual mode
# Tool: tmux_send_key
# Arguments: {"session_name": "vim_editor", "key": "Down"}  # Select lines
# Tool: tmux_send_key
# Arguments: {"session_name": "vim_editor", "key": "d"}  # Delete selection
