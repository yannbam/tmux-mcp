# Development Notes for tmux-mcp

## Critical: stdio Transport and Output

When using MCP with stdio transport (which is the default), **ALL output must go to stderr**, not stdout!

The stdio transport uses:
- **stdin/stdout** for JSON-RPC protocol messages
- **stderr** for logging, debugging, and any other output

### Rules:
1. **NEVER use `print()`** in the server code - it writes to stdout
2. **Always use logging to stderr**: `logger.info()`, `logger.error()`, etc.
3. **Configure logging properly**:
   ```python
   logging.basicConfig(
       handlers=[logging.StreamHandler(sys.stderr)]
   )
   ```

### Why This Matters:
Any output to stdout will corrupt the JSON-RPC communication between the MCP client and server, causing:
- Protocol errors
- Server crashes
- Silent failures

### Testing:
When testing manually, you can redirect stderr to see logs:
```bash
uv run tmux-mcp 2>server.log
```

### Debugging:
Use the MCP Inspector for debugging - it handles stdio properly:
```bash
npx @modelcontextprotocol/inspector uv run tmux-mcp
```
