import json
from openai import OpenAI
from typing import List, Dict, Any

class MCPPlanner:
    def __init__(self, openai_api_key: str):
        self.openai_client = OpenAI(api_key=openai_api_key)
    
    def get_tool_descriptions(self, tools_response) -> str:
        """Convert MCP tools response to readable descriptions"""
        tool_descriptions = []
        
        for tool in tools_response.tools:
            tool_name = tool.name
            params = []
            if hasattr(tool, 'inputSchema') and 'properties' in tool.inputSchema:
                params = list(tool.inputSchema['properties'].keys())
            
            desc = f"- {tool_name}({', '.join([f'{param}: str' for param in params])}): {tool.description}"
            tool_descriptions.append(desc)
        
        return "\n".join(tool_descriptions)
    
    def create_plan(self, user_query: str, available_tools: str) -> Dict[str, Any]:
        """Use LLM to create an execution plan"""
        planner_prompt = f"""
You are an agent with access to these tools:
{available_tools}

User query: "{user_query}"

First, explain your reasoning step-by-step.
Then return JSON like:
{{
  "plan": "...",
  "actions": [
    {{
      "tool": "<tool_name>",
      "args": {{<arg>: <value>, ...}}
    }}
  ]
}}

For CSV operations, assume the file is "sample.csv" and read its content first.
Only return the JSON object as response — do not wrap it in markdown or add any explanation.
"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful agent that plans tool usage."},
                {"role": "user", "content": planner_prompt}
            ]
        )
        
        return json.loads(response.choices[0].message.content)