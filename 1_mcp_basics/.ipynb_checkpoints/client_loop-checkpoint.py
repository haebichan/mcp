import openai
from openai import OpenAI
import requests
import os
import json
from dotenv import load_dotenv
import yaml

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load tool spec from YAML
tool = {
    "name": "summarize_csv",
    "description": "Summarizes a CSV file using pandas. Expects a file path and a natural language instruction.",
    "parameters": [
        {"name": "filepath", "type": "string"},
        {"name": "instruction", "type": "string"}
    ]
}

# Prompt user
user_question = input("Ask me something: ")


# Load tool description from YAML
with open("mcp_tools.yaml") as f:
    mcp_spec = yaml.safe_load(f)

tool = mcp_spec["tools"][0]  # We're only using summarize_csv for now

tool_prompt_desc = f"{tool['name']}(" + ", ".join([f"{p['name']}: {p['type']}" for p in tool['parameters']]) + ")"

tool_decision_prompt = f"""
You are an agent that can either:
1. Answer the user's question directly
2. Or call the tool: {tool_prompt_desc}

Tool description: {tool['description']}

User question: \"{user_question}\"

If the tool should be used, return:
{{"use_tool": true, "filepath": "sample.csv", "instruction": "summarize revenue by region"}}
Otherwise, return:
{{"use_tool": false, "answer": "..."}}
"""


client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful agent."},
        {"role": "user", "content": tool_decision_prompt}
    ]
)

decision = json.loads(response.choices[0].message.content)

# print('decision is: ', decision)

if decision.get("use_tool"):
    print("🔧 Calling tool...")
    payload = {
        "filepath": decision["filepath"],
        "instruction": decision["instruction"]
    }
    res = requests.post("http://localhost:8080/tools/summarize_csv", json=payload)
    print("🧠 Tool response:\n", res.json()["output"])
else:
    print("💬 Answer:\n", decision["answer"])
