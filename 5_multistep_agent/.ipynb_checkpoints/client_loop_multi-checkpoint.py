# client_loop.py

import openai
import json
import requests
import yaml
import uuid

# Load tool specs from YAML
def load_mcp_tools():
    with open("mcp_tools.yaml", "r") as f:
        tools_yaml = yaml.safe_load(f)
    descriptions = []
    for tool in tools_yaml.get("tools", []):
        param_str = ", ".join(f"{arg}: str" for arg in tool.get("args", []))
        descriptions.append(f"Tool: {tool['name']}({param_str})")
    return "\n\n".join(descriptions)

# Persistent session ID across turns
session_id = str(uuid.uuid4())
print(f"📘 Session ID: {session_id}")

available_tools = load_mcp_tools()

while True:
    user_question = input("\n💬 Enter your question (or type 'exit' to quit): ")
    if user_question.lower() in ("exit", "quit"):
        break

    # Step 1: Fetch memory
    mem_resp = requests.get(f"http://localhost:8080/memory/{session_id}")
    try:
        memory_entries = mem_resp.json() if mem_resp.status_code == 200 else []
    except Exception as e:
        print(f"⚠️ Failed to fetch memory: {e}")
        memory_entries = []

    memory_context = "\n".join(
        f"- [{entry['tool']}] {entry['output'][:300]}" for entry in memory_entries
    )

    # Step 2: Build prompt
    tool_decision_prompt = f"""
        You are an agent that can either:
        1. Answer the question directly using your own knowledge
        2. Or call one or more of the following tools if appropriate.
        
        Available tools:
        {available_tools}
        
        Here is what you know from prior steps in this session:
        {memory_context or '(no prior memory)'}
        c
        User question: "{user_question}"
        
        If using tool(s), return JSON array like:
        [
          {{"tool_name": "summarize_csv", "parameters": {{...}}}},
          {{"tool_name": "filter_csv", "parameters": {{...}}}}
        ]
        
        Otherwise, return:
        {{"answer": "..."}}
        
        Only return the JSON. Filepath is sample.csv.
        """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful agent."},
            {"role": "user", "content": tool_decision_prompt}
        ]
    )

    content = response.choices[0].message.content.strip()
    print("🤖 GPT response:\n", content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        continue

    # Step 3: Handle tools or direct answer
    if isinstance(parsed, list):  # Multi-tool plan
        for step in parsed:
            payload = step["parameters"]
            payload["session_id"] = session_id
            tool_name = step["tool_name"]
            print(f"\n🔧 Calling tool: {tool_name}")
            res = requests.post(f"http://localhost:8080/tools/{tool_name}", json=payload)
            print("🧠 Tool response:\n", res.json()["output"])
    elif isinstance(parsed, dict):
        if parsed.get("use_tool"):  # Single tool call
            tool_name = parsed["tool_name"]
            payload = parsed["parameters"]
            payload["session_id"] = session_id
            print(f"\n🔧 Calling tool: {tool_name}")
            res = requests.post(f"http://localhost:8080/tools/{tool_name}", json=payload)
            print("🧠 Tool response:\n", res.json()["output"])
        else:  # Direct LLM answer
            print("\n💬 Answer:\n", parsed["answer"])
    else:
        print("❓ Unexpected response format.")
        continue

        # Step 4: Print concise memory
    print("\n📚 Memory (last 3 entries):")
    try:
        memory = requests.get(f"http://localhost:8080/memory/{session_id}").json()
        for entry in memory[-3:]:
            short_output = entry['output'].strip().replace("\n", " ")
            short_output = short_output[:120] + "..." if len(short_output) > 120 else short_output
            print(f"- [{entry['tool']}] {short_output}")
    except Exception as e:
        print(f"⚠️ Failed to load memory: {e}")
