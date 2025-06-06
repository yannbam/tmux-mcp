#!/usr/bin/env python3
"""
Manual test of tmux-mcp functionality
"""

import subprocess
import time
import json

def test_mcp_server():
    """Test the MCP server is working by checking if it can start"""
    print("Testing if tmux-mcp server can start...")
    
    # Test if the command exists
    result = subprocess.run(["uv", "run", "which", "tmux-mcp"], 
                          capture_output=True, text=True, 
                          cwd="/home/jan/projects/tmux-mcp")
    
    if result.returncode == 0:
        print(f"✅ tmux-mcp command found at: {result.stdout.strip()}")
        print("\nTo fully test the server, run:")
        print("  npx @modelcontextprotocol/inspector uv run tmux-mcp")
        print("\nOr add it to Claude Desktop config and test there!")
        return True
    else:
        print(f"❌ tmux-mcp command not found: {result.stderr}")
        return False

if __name__ == "__main__":
    test_mcp_server()
