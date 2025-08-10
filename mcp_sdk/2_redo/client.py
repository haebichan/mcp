import asyncio
import os
from fastmcp import Client
from mcp_planner import MCPPlanner
from mcp_executor import MCPExecutor

async def main():
    # Get user input
    user_query = input("Enter your question: ")
    
    # Initialize components
    planner = MCPPlanner(os.environ['OPENAI_API_KEY'])
    
    # Connect to MCP server
    async with Client("http://localhost:8080/mcp") as mcp_client:
        print("🔗 Connected to MCP server!")
        
        # Initialize executor
        executor = MCPExecutor(mcp_client)
        
        # Get available tools and create descriptions
        tools_response = await mcp_client.list_tools()
        available_tools = planner.get_tool_descriptions(tools_response)
        
        # Plan tool usage
        print("🧠 Planning tool usage...")
        try:
            plan = planner.create_plan(user_query, available_tools)
            print("📋 Plan:", plan["plan"])
            
            # Execute the plan
            await executor.execute_plan(plan["actions"])
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())