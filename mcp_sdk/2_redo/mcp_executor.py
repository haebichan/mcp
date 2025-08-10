import os
from typing import Dict, Any

class MCPExecutor:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
    
    def handle_file_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file reading for CSV operations"""
        if "csv_text" in args and args["csv_text"] == "sample.csv":
            try:
                with open("sample.csv", "r") as f:
                    args["csv_text"] = f.read()
                print("📁 Loaded CSV file content")
            except FileNotFoundError:
                print("❌ sample.csv not found!")
                raise
        return args
    
    async def execute_action(self, action: Dict[str, Any]) -> str:
        """Execute a single tool action"""
        tool_name = action["tool"]
        args = action["args"]
        
        # Handle file operations
        args = self.handle_file_args(args)
        
        # Call the MCP tool
        result = await self.mcp_client.call_tool(tool_name, args)
        return result.content[0].text
    
    async def execute_plan(self, actions: list) -> None:
        """Execute all actions in a plan"""
        for i, action in enumerate(actions):
            tool_name = action["tool"]
            args = action["args"]
            
            print(f"\n🔧 Step {i+1}: Calling {tool_name} with {args}...")
            
            try:
                result = await self.execute_action(action)
                print("📤 Result:", result)
            except Exception as e:
                print(f"❌ Error calling {tool_name}: {e}")