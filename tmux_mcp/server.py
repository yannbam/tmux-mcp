#!/usr/bin/env python3
"""
tmux-mcp: A Model Context Protocol server for interactive CLI programs via tmux
"""

import asyncio
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    ListResourcesResult,
)
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TmuxSession:
    """Represents a tmux session"""
    name: str
    program: str
    created_at: datetime
    last_accessed: datetime

class TmuxMCPServer:
    """MCP Server that provides access to interactive CLI programs via tmux"""
    
    def __init__(self):
        self.server = Server("tmux-mcp")
        self.sessions: Dict[str, TmuxSession] = {}
        
        # Register handlers
        self.server.list_tools(self._handle_list_tools)
        self.server.call_tool(self._handle_call_tool)
        self.server.list_resources(self._handle_list_resources)
        self.server.read_resource(self._handle_read_resource)
    
    async def _handle_list_tools(self) -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="tmux_start_session",
                description="Start a new tmux session with an interactive CLI program",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_name": {
                            "type": "string",
                            "description": "Name for the tmux session"
                        },
                        "program": {
                            "type": "string",
                            "description": "The CLI program to run (e.g., 'python', 'node', 'nethack', 'vim')"
                        },
                        "args": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional arguments to pass to the program"
                        }
                    },
                    "required": ["session_name", "program"]
                }
            ),
            Tool(
                name="tmux_send_command",
                description="Send a command or input to a tmux session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_name": {
                            "type": "string",
                            "description": "Name of the tmux session"
                        },
                        "command": {
                            "type": "string",
                            "description": "Command or text to send to the session"
                        },
                        "press_enter": {
                            "type": "boolean",
                            "description": "Whether to press Enter after the command (default: true)"
                        }
                    },
                    "required": ["session_name", "command"]
                }
            ),
            Tool(
                name="tmux_read_output",
                description="Read the current output from a tmux session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_name": {
                            "type": "string",
                            "description": "Name of the tmux session"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of lines to read from the end (default: all visible)"
                        }
                    },
                    "required": ["session_name"]
                }
            ),
            Tool(
                name="tmux_send_key",
                description="Send a special key to a tmux session (e.g., Ctrl+C, Tab, Escape)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_name": {
                            "type": "string",
                            "description": "Name of the tmux session"
                        },
                        "key": {
                            "type": "string",
                            "description": "Key to send (e.g., 'C-c' for Ctrl+C, 'Tab', 'Escape', 'Up', 'Down')"
                        }
                    },
                    "required": ["session_name", "key"]
                }
            ),
            Tool(
                name="tmux_list_sessions",
                description="List all active tmux sessions managed by this server",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="tmux_kill_session",
                description="Kill a tmux session",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_name": {
                            "type": "string",
                            "description": "Name of the tmux session to kill"
                        }
                    },
                    "required": ["session_name"]
                }
            )
        ]
    
    async def _handle_call_tool(self, name: str, arguments: Any) -> List[TextContent]:
        """Handle tool calls"""
        try:
            if name == "tmux_start_session":
                return await self._start_session(arguments)
            elif name == "tmux_send_command":
                return await self._send_command(arguments)
            elif name == "tmux_read_output":
                return await self._read_output(arguments)
            elif name == "tmux_send_key":
                return await self._send_key(arguments)
            elif name == "tmux_list_sessions":
                return await self._list_sessions()
            elif name == "tmux_kill_session":
                return await self._kill_session(arguments)
            else:
                return [TextContent(text=f"Unknown tool: {name}")]
        except Exception as e:
            return [TextContent(text=f"Error: {str(e)}")]
    
    async def _start_session(self, args: Dict[str, Any]) -> List[TextContent]:
        """Start a new tmux session"""
        session_name = args["session_name"]
        program = args["program"]
        program_args = args.get("args", [])
        
        # Check if session already exists
        if session_name in self.sessions:
            return [TextContent(text=f"Session '{session_name}' already exists")]
        
        # Check if tmux session with this name exists
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True
            )
            if result.returncode == 0:
                return [TextContent(text=f"Tmux session '{session_name}' already exists")]
        except Exception:
            pass
        
        # Start the tmux session
        cmd = ["tmux", "new-session", "-d", "-s", session_name, program] + program_args
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Track the session
            self.sessions[session_name] = TmuxSession(
                name=session_name,
                program=program,
                created_at=datetime.now(),
                last_accessed=datetime.now()
            )
            
            return [TextContent(text=f"Started tmux session '{session_name}' running '{program}'")]
        except subprocess.CalledProcessError as e:
            return [TextContent(text=f"Failed to start session: {e.stderr}")]
    
    async def _send_command(self, args: Dict[str, Any]) -> List[TextContent]:
        """Send a command to a tmux session"""
        session_name = args["session_name"]
        command = args["command"]
        press_enter = args.get("press_enter", True)
        
        if session_name not in self.sessions:
            return [TextContent(text=f"Session '{session_name}' not found")]
        
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
            
            self.sessions[session_name].last_accessed = datetime.now()
            return [TextContent(text=f"Sent command to session '{session_name}'")]
        except subprocess.CalledProcessError as e:
            return [TextContent(text=f"Failed to send command: {e.stderr}")]
    
    async def _read_output(self, args: Dict[str, Any]) -> List[TextContent]:
        """Read output from a tmux session"""
        session_name = args["session_name"]
        lines = args.get("lines")
        
        if session_name not in self.sessions:
            return [TextContent(text=f"Session '{session_name}' not found")]
        
        # Capture pane content
        try:
            cmd = ["tmux", "capture-pane", "-t", session_name, "-p"]
            if lines:
                cmd.extend(["-S", f"-{lines}"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.sessions[session_name].last_accessed = datetime.now()
            return [TextContent(text=result.stdout)]
        except subprocess.CalledProcessError as e:
            return [TextContent(text=f"Failed to read output: {e.stderr}")]
    
    async def _send_key(self, args: Dict[str, Any]) -> List[TextContent]:
        """Send a special key to a tmux session"""
        session_name = args["session_name"]
        key = args["key"]
        
        if session_name not in self.sessions:
            return [TextContent(text=f"Session '{session_name}' not found")]
        
        try:
            subprocess.run(
                ["tmux", "send-keys", "-t", session_name, key],
                check=True, capture_output=True, text=True
            )
            
            self.sessions[session_name].last_accessed = datetime.now()
            return [TextContent(text=f"Sent key '{key}' to session '{session_name}'")]
        except subprocess.CalledProcessError as e:
            return [TextContent(text=f"Failed to send key: {e.stderr}")]
    
    async def _list_sessions(self) -> List[TextContent]:
        """List all active sessions"""
        if not self.sessions:
            return [TextContent(text="No active sessions")]
        
        session_info = []
        for name, session in self.sessions.items():
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
        
        return [TextContent(text="Active sessions:\n" + "\n".join(session_info))]
    
    async def _kill_session(self, args: Dict[str, Any]) -> List[TextContent]:
        """Kill a tmux session"""
        session_name = args["session_name"]
        
        if session_name not in self.sessions:
            return [TextContent(text=f"Session '{session_name}' not found")]
        
        try:
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                check=True, capture_output=True, text=True
            )
            
            del self.sessions[session_name]
            return [TextContent(text=f"Killed session '{session_name}'")]
        except subprocess.CalledProcessError as e:
            return [TextContent(text=f"Failed to kill session: {e.stderr}")]
    
    async def _handle_list_resources(self) -> ListResourcesResult:
        """List available resources"""
        resources = []
        for session_name in self.sessions:
            resources.append(
                Resource(
                    uri=f"tmux://session/{session_name}",
                    name=f"Session: {session_name}",
                    description=f"Current state of tmux session '{session_name}'",
                    mimeType="text/plain"
                )
            )
        return ListResourcesResult(resources=resources)
    
    async def _handle_read_resource(self, uri: str) -> List[TextContent]:
        """Read a resource"""
        if uri.startswith("tmux://session/"):
            session_name = uri.replace("tmux://session/", "")
            if session_name in self.sessions:
                # Get session output
                try:
                    result = subprocess.run(
                        ["tmux", "capture-pane", "-t", session_name, "-p"],
                        capture_output=True, text=True, check=True
                    )
                    return [TextContent(text=result.stdout)]
                except subprocess.CalledProcessError as e:
                    return [TextContent(text=f"Failed to read session: {e.stderr}")]
        
        return [TextContent(text=f"Resource not found: {uri}")]
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting tmux-mcp server...")
        
        # Check if tmux is installed
        try:
            subprocess.run(["tmux", "-V"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("tmux is not installed. Please install tmux first.")
            return
        
        # Run the server
        await stdio_server(self.server.request_handlers, self.server.name)

def main():
    """Main entry point"""
    server = TmuxMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
