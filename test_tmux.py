#!/usr/bin/env python3
"""
Quick test script to verify tmux-mcp is working
"""

import subprocess
import time
import sys

def test_basic_functionality():
    print("Testing tmux-mcp basic functionality...")
    
    # Test 1: Start a session
    print("\n1. Testing session creation...")
    result = subprocess.run(["tmux", "new-session", "-d", "-s", "test_session", "echo", "Hello from tmux-mcp"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Session created successfully")
    else:
        print(f"❌ Failed to create session: {result.stderr}")
        return False
    
    # Test 2: Read output
    print("\n2. Testing output capture...")
    time.sleep(0.5)  # Give it time to execute
    result = subprocess.run(["tmux", "capture-pane", "-t", "test_session", "-p"], 
                          capture_output=True, text=True)
    if "Hello from tmux-mcp" in result.stdout:
        print("✅ Output captured successfully")
        print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"❌ Failed to capture expected output: {result.stdout}")
    
    # Test 3: Kill session
    print("\n3. Testing session cleanup...")
    result = subprocess.run(["tmux", "kill-session", "-t", "test_session"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Session killed successfully")
    else:
        print(f"❌ Failed to kill session: {result.stderr}")
    
    print("\n✅ All basic tmux operations working!")
    return True

if __name__ == "__main__":
    if test_basic_functionality():
        print("\nNext: Test the MCP server with 'npx @modelcontextprotocol/inspector uv run tmux-mcp'")
        sys.exit(0)
    else:
        sys.exit(1)
