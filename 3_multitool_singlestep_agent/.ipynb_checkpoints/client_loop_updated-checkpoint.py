import openai
import json
import requests
import yaml
import os
import re

# Replace with your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

user_query = input("Enter your question: ")

# Load MCP tool definitions
with open("mcp_tools.yaml", "r") as f:
    mcp_tools = yaml.safe_load(f)

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

    res = requests.post("http://localhost:8080/rpc", json=rpc_payload)
    result = res.json()
    print("📤 Response:", result.get("result") or result.get("error"))



# import openai
# import json
# import requests
# import yaml
# import os
# import re
# import ast
# from helper_function import validate_params_against_schema

# # Replace with your OpenAI key
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # === Load MCP tool definitions ===
# with open("mcp_tools.yaml", "r") as f:
#     mcp_tools = yaml.safe_load(f)


# # === Prompt user ===
# user_query = input("Enter your question: ")

# # === Build readable list of tools for GPT ===
# tool_descriptions = "\n".join([
#     f"- {tool['name']}({', '.join([f'{arg}: str' for arg in tool['args']])})"
#     for tool in mcp_tools['tools']
# ])

# # === Prompt LLM for plan ===
# planner_prompt = f"""
# You are an agent with access to these tools:
# {tool_descriptions}

# User query: "{user_query}"

# First, explain your reasoning step-by-step.
# Then return JSON like:
# {{
#   "plan": "...",
#   "actions": [
#     {{
#       "tool": "<tool_name>",
#       "args": {{<arg>: <value>, ...}}
#     }}
#   ]
# }}

# Filepath should be sample.csv. Only return the JSON object — no markdown or explanation.
# """

# response = openai.chat.completions.create(
#     model="gpt-4",
#     messages=[
#         {"role": "system", "content": "You are a helpful agent."},
#         {"role": "user", "content": planner_prompt}
#     ]
# )

# raw_content = response.choices[0].message.content

# # === Extract JSON from model output ===
# match = re.search(r"\{[\s\S]*\}", raw_content)
# if match:
#     json_str = match.group(0)
# else:
#     print("❌ Could not find JSON in model output:")
#     print(raw_content)
#     raise ValueError("No valid JSON found")

# plan_response = json.loads(json_str)


# try:
#     plan_response = json.loads(json_str)
# except json.JSONDecodeError:
#     print("❌ Failed to parse JSON from model response:")
#     print(raw_content)
#     raise

# # === Print the reasoning plan ===
# print("🧠 Plan:", plan_response.get("plan", "No plan provided."))

# # === Execute each tool call ===
# for i, action in enumerate(plan_response.get("actions", [])):
#     tool = action["tool"]
#     args = action["args"]

#     rpc_payload = {
#         "jsonrpc": "2.0",
#         "method": tool,
#         "params": args,
#         "id": i + 1
#     }

#     # ✅ Validate params using schema
#     try:
#         validate_params_against_schema(tool, args, mcp_tools)
#     except ValueError as e:
#         print(e)
#         continue

#     print(f"\n🔧 Calling {tool} with args: {args}...")

#     res = requests.post("http://localhost:8080/rpc", json=rpc_payload)

#     try:
#         result = res.json()
#         print("📤 Response:", result.get("result") or result.get("error"))
#     except Exception as e:
#         print("❌ Server returned non-JSON response:", res.text)


