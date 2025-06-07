#!/usr/bin/env python3
"""
tmux-mcp: A Model Context Protocol server for interactive CLI programs via tmux
"""

import subprocess
import logging
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Configure logging - MUST use stderr for stdio transport!
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

@dataclass
class TmuxSession:
    """Represents a tmux session"""
    name: str
    program: str
    created_at: datetime
    last_accessed: datetime

# Create the FastMCP server instance
mcp = FastMCP("tmux-mcp")

# Store active sessions
sessions: Dict[str, TmuxSession] = {}

# Tools implementation

@mcp.tool()
async def tmux_start_session(session_name: str, program: str, args: Optional[List[str]] = None) -> str:
    """Start a new tmux session with an interactive CLI program
    
    Args:
        session_name: Name for the tmux session
        program: The CLI program to run (e.g., 'python', 'node', 'nethack', 'vim')
        args: Optional arguments to pass to the program
    """
    if args is None:
        args = []
    
    # Check if session already exists
    if session_name in sessions:
        return f"Session '{session_name}' already exists"
    
    # Check if tmux session with this name exists
    try:
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True
        )
        if result.returncode == 0:
            return f"Tmux session '{session_name}' already exists"
    except Exception:
        pass
    
    # Start the tmux session
    cmd = ["tmux", "new-session", "-d", "-s", session_name, program] + args
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Track the session
        sessions[session_name] = TmuxSession(
            name=session_name,
            program=program,
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        
        return f"Started tmux session '{session_name}' running '{program}'"
    except subprocess.CalledProcessError as e:
        return f"Failed to start session: {e.stderr}"

@mcp.tool()
async def tmux_send_command(session_name: str, command: str, press_enter: bool = True) -> str:
    """Send a command or input to a tmux session
    
    Args:
        session_name: Name of the tmux session
        command: Command or text to send to the session
        press_enter: Whether to press Enter after the command (default: true)
    """
    if session_name not in sessions:
        return f"Session '{session_name}' not found"
    
    # Send the command
    try:
        if press_enter:
            subprocess.run(
                ["tmux", "send-keys", "-t", session_name, command, "Enter"],
                check=True, capture_output=True, text=True
            )
        else:
            subprocess.run(
                ["tmux", "send-keys", "-t", session_name, command],
                check=True, capture_output=True, text=True
            )
        
        sessions[session_name].last_accessed = datetime.now()
        return f"Sent command to session '{session_name}'"
    except subprocess.CalledProcessError as e:
        return f"Failed to send command: {e.stderr}"

@mcp.tool()
async def tmux_read_output(session_name: str, lines: Optional[int] = None) -> str:
    """Read the current output from a tmux session
    
    Args:
        session_name: Name of the tmux session
        lines: Number of lines to read from the end (default: all visible)
    """
    if session_name not in sessions:
        return f"Session '{session_name}' not found"
    
    # Capture pane content
    try:
        cmd = ["tmux", "capture-pane", "-t", session_name, "-p"]
        if lines:
            cmd.extend(["-S", f"-{lines}"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        sessions[session_name].last_accessed = datetime.now()
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Failed to read output: {e.stderr}"

@mcp.tool()
async def tmux_send_key(session_name: str, key: str) -> str:
    """Send a special key to a tmux session (e.g., Ctrl+C, Tab, Escape)
    
    Args:
        session_name: Name of the tmux session
        key: Key to send (e.g., 'C-c' for Ctrl+C, 'Tab', 'Escape', 'Up', 'Down')
    """
    if session_name not in sessions:
        return f"Session '{session_name}' not found"
    
    try:
        subprocess.run(
            ["tmux", "send-keys", "-t", session_name, key],
            check=True, capture_output=True, text=True
        )
        
        sessions[session_name].last_accessed = datetime.now()
        return f"Sent key '{key}' to session '{session_name}'"
    except subprocess.CalledProcessError as e:
        return f"Failed to send key: {e.stderr}"

@mcp.tool()
async def tmux_list_sessions() -> str:
    """List all active tmux sessions managed by this server"""
    if not sessions:
        return "No active sessions"
    
    session_info = []
    for name, session in sessions.items():
        # Check if tmux session still exists
        try:
            subprocess.run(
                ["tmux", "has-session", "-t", name],
                capture_output=True, check=True
            )
            status = "active"
        except subprocess.CalledProcessError:
            status = "dead"
        
        session_info.append(
            f"- {name}: {session.program} ({status}) - "
            f"Created: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    return "Active sessions:\n" + "\n".join(session_info)

@mcp.tool()
async def tmux_kill_session(session_name: str) -> str:
    """Kill a tmux session
    
    Args:
        session_name: Name of the tmux session to kill
    """
    if session_name not in sessions:
        return f"Session '{session_name}' not found"
    
    try:
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            check=True, capture_output=True, text=True
        )
        
        del sessions[session_name]
        return f"Killed session '{session_name}'"
    except subprocess.CalledProcessError as e:
        return f"Failed to kill session: {e.stderr}"

# Resources implementation - commented out for now as FastMCP resources may work differently
# We'll focus on tools first and add resources later if needed

# @mcp.resource(f"tmux://session/")
# async def list_sessions_resource() -> List[Resource]:
#     """List all active tmux sessions as resources"""
#     resources = []
#     for session_name in sessions:
#         resources.append(
#             Resource(
#                 uri=f"tmux://session/{session_name}",
#                 name=f"Session: {session_name}",
#                 description=f"Current state of tmux session '{session_name}'",
#                 mimeType="text/plain"
#             )
#         )
#     return resources

# @mcp.resource(r"tmux://session/(.+)")
# async def read_session_resource(uri: str) -> str:
#     """Read the current state of a tmux session"""
#     # Extract session name from URI
#     session_name = uri.replace("tmux://session/", "")
#     
#     if session_name not in sessions:
#         return f"Session '{session_name}' not found"
#     
#     # Get session output
#     try:
#         result = subprocess.run(
#             ["tmux", "capture-pane", "-t", session_name, "-p"],
#             capture_output=True, text=True, check=True
#         )
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         return f"Failed to read session: {e.stderr}"

def main():
    """Main entry point"""
    logger.info("Starting tmux-mcp server...")
    
    # Check if tmux is installed
    try:
        subprocess.run(["tmux", "-V"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("tmux is not installed. Please install tmux first.")
        return
    
    # Run the server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
