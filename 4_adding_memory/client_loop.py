# client_loop.py

import openai
import json
import requests
import yaml
import uuid

# Load tool specs from mcp_tools.yaml
def load_mcp_tools():
    with open("mcp_tools.yaml", "r") as f:
        tools_yaml = yaml.safe_load(f)
    descriptions = []
    for tool in tools_yaml.get("tools", []):
        param_str = ", ".join(f"{arg}: str" for arg in tool.get("args", []))
        descriptions.append(f"Tool: {tool['name']}({param_str})")
    return "\n\n".join(descriptions)

# Generate a session ID for tracking
session_id = str(uuid.uuid4())
print(f"📘 Session ID: {session_id}")

available_tools = load_mcp_tools()

while True:
    user_question = input("\nEnter your question (or type 'exit' to quit): ")
    if user_question.lower() in ("exit", "quit"):
        break

    tool_decision_prompt = f"""
You are an agent that can either:
1. Answer the question directly using your own knowledge
2. Or call one of the following tools if appropriate:

{available_tools}

User question: "{user_question}"

If using a tool, return JSON like:
{{"use_tool": true, "tool_name": "summarize_csv", "parameters": {{...}}}}

Otherwise, return:
{{"use_tool": false, "answer": "..."}}

only return the json, nothing else. Filepath should be sample.csv
"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful agent."},
            {"role": "user", "content": tool_decision_prompt}
        ]
    )

    try:
        response_json = response.choices[0].message.content.strip()
        print("🧠 GPT Response:\n", response_json)

        decision = json.loads(response_json)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        continue

    if decision.get("use_tool"):
        tool_name = decision["tool_name"]
        payload = decision["parameters"]
        payload["session_id"] = session_id
        print("🔧 Calling tool:", tool_name)
        res = requests.post(f"http://localhost:8080/tools/{tool_name}", json=payload)
        print("🧠 Tool response:\n", res.json()["output"])
    else:
        print("💬 Answer:\n", decision["answer"])

    # Print session memory
    print("\n📚 Memory for this session so far:")
    mem_resp = requests.get(f"http://localhost:8080/memory/{session_id}")
    try:
        memory = mem_resp.json()
        if isinstance(memory, list):
            for entry in memory:
                print(f"- [{entry['tool']}] {entry['output'][:100]}...")
        else:
            print(f"(Unexpected memory format): {memory}")
    except Exception as e:
        print(f"Failed to load memory: {e}")
