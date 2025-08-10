from fastmcp import FastMCP

mcp = FastMCP(
    name="Dummy MCP Agent",
    stateless_http=True,
)

@mcp.tool()
def echo(text: str) -> str:
    """Simply returns 'Echo: <text>'."""
    return f"Echo: {text}"

if __name__ == "__main__":
    # Uses default /mcp/ endpoint
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
