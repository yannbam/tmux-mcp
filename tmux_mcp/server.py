#!/usr/bin/env python3
"""
tmux-mcp: A Model Context Protocol server for interactive CLI programs via tmux

Supports both local and remote tmux sessions via SSH.

Environment variables:
    TMUX_MCP__ssh_host: SSH host for remote tmux (e.g., "backloom-claude")
                       If not set, operates on local tmux.
"""

import shlex
import subprocess
import logging
import os
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

# SSH host for remote tmux (None = local)
# Can be set via env var or dynamically via tmux_set_ssh_host tool
_ssh_host: Optional[str] = os.environ.get("TMUX_MCP__ssh_host")
if _ssh_host:
    logger.info(f"Remote mode: connecting to tmux via SSH host '{_ssh_host}'")
else:
    logger.info("Local mode: operating on local tmux (use tmux_set_ssh_host to connect remotely)")


def run_tmux_command(args: List[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a tmux command, optionally via SSH if _ssh_host is set."""
    if _ssh_host:
        # Wrap command in SSH — quote args properly for remote shell
        tmux_cmd = "tmux " + " ".join(shlex.quote(arg) for arg in args)
        cmd = ["ssh", _ssh_host, tmux_cmd]
    else:
        cmd = ["tmux"] + args
    return subprocess.run(cmd, **kwargs)


@dataclass
class TmuxSession:
    """Represents a tmux session"""
    name: str
    program: str
    created_at: datetime
    last_accessed: datetime
    is_remote: bool = False


# Create the FastMCP server instance
mcp = FastMCP("tmux-mcp")

# Store active sessions
sessions: Dict[str, TmuxSession] = {}


# Tools implementation

@mcp.tool()
async def tmux_set_ssh_host(ssh_host: Optional[str] = None) -> str:
    """Set SSH host for remote tmux access (call with no args to switch back to local)

    Args:
        ssh_host: SSH host to connect through (e.g., "backloom-claude"). Pass None or empty to use local tmux.
    """
    global _ssh_host
    old_host = _ssh_host

    if ssh_host:
        _ssh_host = ssh_host
        # Verify connection works
        try:
            result = run_tmux_command(["-V"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                return f"Now using remote tmux via '{ssh_host}' ({version})"
            else:
                _ssh_host = old_host  # Revert on failure
                return f"Failed to connect to '{ssh_host}': {result.stderr}"
        except Exception as e:
            _ssh_host = old_host  # Revert on failure
            return f"Failed to connect to '{ssh_host}': {e}"
    else:
        _ssh_host = None
        return "Now using local tmux"


@mcp.tool()
async def tmux_get_connection() -> str:
    """Get current tmux connection info (local or remote SSH host)"""
    if _ssh_host:
        return f"Connected to remote tmux via SSH host: {_ssh_host}"
    else:
        return "Using local tmux"

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

    # Check if session already exists in our tracking
    if session_name in sessions:
        return f"Session '{session_name}' already exists"

    # Check if tmux session with this name exists
    try:
        result = run_tmux_command(
            ["has-session", "-t", session_name],
            capture_output=True
        )
        if result.returncode == 0:
            return f"Tmux session '{session_name}' already exists (use tmux_attach_session to track it)"
    except Exception:
        pass

    # Start the tmux session
    try:
        run_tmux_command(
            ["new-session", "-d", "-s", session_name, program] + args,
            check=True, capture_output=True, text=True
        )

        # Track the session
        sessions[session_name] = TmuxSession(
            name=session_name,
            program=program,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            is_remote=bool(_ssh_host)
        )

        location = f"on {_ssh_host}" if _ssh_host else "locally"
        return f"Started tmux session '{session_name}' running '{program}' {location}"
    except subprocess.CalledProcessError as e:
        return f"Failed to start session: {e.stderr}"


@mcp.tool()
async def tmux_attach_session(session_name: str, program: str = "unknown") -> str:
    """Attach to an existing tmux session (for sessions not created by this server)

    Args:
        session_name: Name of the existing tmux session to attach to
        program: Description of what's running in the session (for tracking)
    """
    # Check if already tracking
    if session_name in sessions:
        return f"Session '{session_name}' is already being tracked"

    # Verify the session exists
    try:
        result = run_tmux_command(
            ["has-session", "-t", session_name],
            capture_output=True
        )
        if result.returncode != 0:
            return f"Tmux session '{session_name}' does not exist"
    except subprocess.CalledProcessError:
        return f"Tmux session '{session_name}' does not exist"
    except Exception as e:
        return f"Failed to check session: {e}"

    # Track the session
    sessions[session_name] = TmuxSession(
        name=session_name,
        program=program,
        created_at=datetime.now(),  # We don't know actual creation time
        last_accessed=datetime.now(),
        is_remote=bool(_ssh_host)
    )

    location = f"on {_ssh_host}" if _ssh_host else "locally"
    return f"Now tracking existing tmux session '{session_name}' ({program}) {location}"

@mcp.tool()
async def tmux_send_command(session_name: str, command: str, press_enter: bool = True) -> str:
    """Send a command or input to a tmux session

    Args:
        session_name: Name of the tmux session
        command: Command or text to send to the session
        press_enter: Whether to press Enter after the command (default: true)
    """
    if session_name not in sessions:
        return f"Session '{session_name}' not found (use tmux_attach_session first for existing sessions)"

    # Send the command
    try:
        if press_enter:
            run_tmux_command(
                ["send-keys", "-t", session_name, command, "Enter"],
                check=True, capture_output=True, text=True
            )
        else:
            run_tmux_command(
                ["send-keys", "-t", session_name, command],
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
        return f"Session '{session_name}' not found (use tmux_attach_session first for existing sessions)"

    # Capture pane content
    try:
        args = ["capture-pane", "-t", session_name, "-p"]
        if lines:
            args.extend(["-S", f"-{lines}"])

        result = run_tmux_command(args, capture_output=True, text=True, check=True)

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
        return f"Session '{session_name}' not found (use tmux_attach_session first for existing sessions)"

    try:
        run_tmux_command(
            ["send-keys", "-t", session_name, key],
            check=True, capture_output=True, text=True
        )

        sessions[session_name].last_accessed = datetime.now()
        return f"Sent key '{key}' to session '{session_name}'"
    except subprocess.CalledProcessError as e:
        return f"Failed to send key: {e.stderr}"

@mcp.tool()
async def tmux_list_sessions() -> str:
    """List all tmux sessions being tracked by this server"""
    if not sessions:
        location = f"on {_ssh_host}" if _ssh_host else "locally"
        return f"No tracked sessions {location}. Use tmux_discover_sessions to find existing sessions, then tmux_attach_session to track them."

    session_info = []
    for name, session in sessions.items():
        # Check if tmux session still exists
        try:
            result = run_tmux_command(
                ["has-session", "-t", name],
                capture_output=True
            )
            status = "active" if result.returncode == 0 else "dead"
        except subprocess.CalledProcessError:
            status = "dead"

        location = "remote" if session.is_remote else "local"
        session_info.append(
            f"- {name}: {session.program} ({status}, {location}) - "
            f"Last accessed: {session.last_accessed.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    return "Tracked sessions:\n" + "\n".join(session_info)


@mcp.tool()
async def tmux_discover_sessions() -> str:
    """Discover all tmux sessions available (both tracked and untracked)

    Useful for finding existing sessions to attach to.
    """
    location = f"on {_ssh_host}" if _ssh_host else "locally"
    try:
        result = run_tmux_command(
            ["list-sessions", "-F", "#{session_name}: #{session_windows} windows (created #{session_created})"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"No tmux sessions found {location}"

        output = result.stdout.strip()
        if not output:
            return f"No tmux sessions found {location}"

        # Mark which ones we're tracking
        lines = output.split("\n")
        annotated = []
        for line in lines:
            session_name = line.split(":")[0]
            tracked = " [TRACKED]" if session_name in sessions else ""
            annotated.append(f"  {line}{tracked}")

        return f"Tmux sessions {location}:\n" + "\n".join(annotated)
    except Exception as e:
        return f"Failed to list sessions {location}: {e}"

@mcp.tool()
async def tmux_kill_session(session_name: str) -> str:
    """Kill a tmux session

    Args:
        session_name: Name of the tmux session to kill
    """
    if session_name not in sessions:
        return f"Session '{session_name}' not found (use tmux_attach_session first for existing sessions)"

    try:
        run_tmux_command(
            ["kill-session", "-t", session_name],
            check=True, capture_output=True, text=True
        )

        del sessions[session_name]
        return f"Killed session '{session_name}'"
    except subprocess.CalledProcessError as e:
        return f"Failed to kill session: {e.stderr}"


@mcp.tool()
async def tmux_detach_session(session_name: str) -> str:
    """Stop tracking a session without killing it (useful for remote sessions you want to leave running)

    Args:
        session_name: Name of the tmux session to stop tracking
    """
    if session_name not in sessions:
        return f"Session '{session_name}' not found in tracking"

    del sessions[session_name]
    return f"Stopped tracking session '{session_name}' (session still running)"

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

def check_tmux_available() -> bool:
    """Check if tmux is available (locally or via SSH)."""
    try:
        result = run_tmux_command(["-V"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            location = f"on {_ssh_host}" if _ssh_host else "locally"
            logger.info(f"tmux {version} available {location}")
            return True
        return False
    except FileNotFoundError:
        if _ssh_host:
            logger.error(f"SSH not available or cannot connect to {_ssh_host}")
        else:
            logger.error("tmux is not installed. Please install tmux first.")
        return False
    except Exception as e:
        logger.error(f"Failed to check tmux: {e}")
        return False


def main():
    """Main entry point for direct execution"""
    logger.info("Starting tmux-mcp server...")

    if not check_tmux_available():
        return

    # Run the server
    mcp.run(transport="stdio")


# Initialize tmux check for MCP CLI usage
if check_tmux_available():
    logger.info("tmux-mcp server ready")

if __name__ == "__main__":
    main()
