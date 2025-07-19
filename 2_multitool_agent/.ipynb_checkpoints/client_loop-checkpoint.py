# client_loop.py

import openai
import json
import yaml
import requests

# === Load tool definitions from YAML ===
with open("mcp_tools.yaml", "r") as f:
    tools_yaml = yaml.safe_load(f)

tool_descriptions = []
for tool in tools_yaml["tools"]:
    param_str = ", ".join([f"{p['name']}: {p['type']}" for p in tool["parameters"]])
    tool_descriptions.append(f"{tool['name']}({param_str}) - {tool['description']}")

tools_prompt = "\n".join(tool_descriptions)

# === Get user input ===
user_question = input("❓ Ask a question: ")

# === Step 1: Ask OpenAI what to do ===
tool_decision_prompt = f"""
You are an intelligent agent that can either:
1. Answer the question directly using your own knowledge
2. Or call one of the available tools below

Available tools:
{tools_prompt}

User question: \"{user_question}\"

If a tool should be used, return a JSON object like:
{{
  "use_tool": true,
  "tool_name": "filter_csv",
  "args": {{
    "filepath": "sample.csv",
    "column": "region",
    "value": "West"
  }}
}}

Otherwise, return:
{{ "use_tool": false, "answer": "..." }}
"""

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful agent."},
        {"role": "user", "content": tool_decision_prompt}
    ]
)

print('content:', response.choices[0].message.content)

decision = json.loads(response.choices[0].message.content)

# === Step 2: Route based on response ===
if decision.get("use_tool"):
    tool_name = decision["tool_name"]
    args = decision["args"]
    print(f"🔧 Calling tool: {tool_name} with {args}")

    res = requests.post(f"http://localhost:8080/tools/{tool_name}", json=args)
    print("🧠 Tool response:\n", res.json()["output"])
else:
    print("💬 Answer:\n", decision["answer"])
