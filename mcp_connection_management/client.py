import openai
import json
import requests
import yaml
import os
import re

# Replace with your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

# === ADDED: Connection management function ===
def discover_tools_from_server(server_url):
    """Discover tools from MCP server"""
    try:
        tools_payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        response = requests.post(f"{server_url}/rpc", json=tools_payload, timeout=5)
        result = response.json()
        
        if "error" in result:
            return None
            
        # Convert to your existing format
        tools = result.get("result", {}).get("tools", [])
        return {
            "tools": [
                {
                    "name": tool["name"],
                    "args": list(tool.get("inputSchema", {}).get("properties", {}).keys())
                }
                for tool in tools
            ]
        }
    except:
        return None

user_query = input("Enter your question: ")

# MODIFIED: Try server discovery first, fallback to YAML
server_url = "http://localhost:8080"
mcp_tools = discover_tools_from_server(server_url)

if mcp_tools is None:
    print("📁 Server discovery failed, using YAML...")
    # Load MCP tool definitions
    with open("mcp_tools.yaml", "r") as f:
        mcp_tools = yaml.safe_load(f)
else:
    print("🔌 Tools discovered from server")

# Create a readable list of tools for GPT
tool_descriptions = "\n".join([
    f"- {tool['name']}({', '.join([f'{arg}: str' for arg in tool['args']])})"
    for tool in mcp_tools['tools']
])

# Step 1: Ask GPT to plan tool usage
planner_prompt = f"""
You are an agent with access to these tools:
{tool_descriptions}
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
Filepath should be sample.csv. Only return the JSON object as response — do not wrap it in markdown or add any explanation.
"""

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful agent."},
        {"role": "user", "content": planner_prompt}
    ]
)

# Step 2: Extract JSON from the model's response
raw_content = response.choices[0].message.content
# Extract JSON inside triple backticks if wrapped in markdown
match = re.search(r"```(?:json)?\n(.*?)```", raw_content, re.DOTALL)
if match:
    json_str = match.group(1)
else:
    json_str = raw_content.strip()

# Parse the extracted JSON
try:
    plan_response = json.loads(json_str)
except json.JSONDecodeError:
    print("❌ Failed to decode JSON. Full response from model:")
    print(raw_content)
    raise

# Step 3: Call each tool via JSON-RPC
print("🧠 Plan:", plan_response["plan"])
for i, action in enumerate(plan_response["actions"]):
    tool = action["tool"]
    args = action["args"]
    print(f"\n🔧 Calling {tool} with {args}...")
    
    rpc_payload = {
        "jsonrpc": "2.0",
        "method": tool,
        "params": args,
        "id": i + 1  # unique ID per call
    }
    
    # UNCHANGED: Still using your original request logic
    res = requests.post("http://localhost:8080/rpc", json=rpc_payload)
    result = res.json()
    print("📤 Response:", result.get("result") or result.get("error"))