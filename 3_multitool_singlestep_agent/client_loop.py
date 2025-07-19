import openai
import json
import requests
import yaml
import os

# Replace with your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

user_query = input("Enter your question: ")

# Load MCP tool definitions
with open("mcp_tools.yaml", "r") as f:
    mcp_tools = yaml.safe_load(f)

tool_descriptions = "\n".join([
    f"- {tool['name']}({', '.join([f'{arg}: str' for arg in tool['args']])})" for tool in mcp_tools['tools']
])

# Step 1: Ask LLM to plan multiple tool calls
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

Filepath should be sample.csv. Only return the json as response, nothing additional. 
"""

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful agent."},
        {"role": "user", "content": planner_prompt}
    ]
)


# Step 2: Parse and run each tool call
plan_response = json.loads(response.choices[0].message.content)
print("🧠 Plan:", plan_response["plan"])

for action in plan_response["actions"]:
    tool = action["tool"]
    args = action["args"]
    print(f"\n🔧 Calling {tool} with {args}...")
    res = requests.post(f"http://localhost:8080/tools/{tool}", json=args)
    print("📤 Response:", res.json()["output"])



## Questions
# Summarize the data in sample.csv, then filter it to only include rows where region is 'West'
# First describe what's in the CSV, then show me just the rows where product is 'A'
# Give me basic statistics on the CSV, and then filter to keep only rows where revenue is greater than 1000
