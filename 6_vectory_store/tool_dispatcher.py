# tool_dispatcher.py

import os
import json
import openai
import requests
from vector_memory import add_to_vector_store
from mcp_loader import load_mcp_tools


openai.api_key = os.getenv("OPENAI_API_KEY")

def handle_user_input(question, memory_context, session_id, client_id):
    tools_desc = load_mcp_tools()

    tool_prompt = f"""
        You are an agent that can either:
        1. Answer the question using your knowledge
        2. Or call one or more of these tools:
        
        {tools_desc}
        
        Memory:
        {memory_context}
        
        User: \"{question}\"
        
        If using tool(s), return JSON array like:
        [
          {{\"tool_name\": \"summarize_csv\", \"parameters\": {{...}} }},
          ...
        ]
        Otherwise, return: {{\"answer\": \"...\"}}
        
        Only return JSON. Use 'sample.csv' as filepath.
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful agent."},
                  {"role": "user", "content": tool_prompt}]
    )

    content = response.choices[0].message.content.strip()
    print("🔍 GPT response:\n", content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return

    if isinstance(parsed, dict) and "answer" in parsed:
        print("💬 Answer:", parsed["answer"])
        add_to_vector_store(question + "\n" + parsed["answer"])
    elif isinstance(parsed, list):
        for call in parsed:
            tool_name = call["tool_name"]
            payload = call["parameters"]
            payload["session_id"] = session_id
            print("🔧 Calling tool:", tool_name)
            res = requests.post(f"http://localhost:8080/tools/{tool_name}", json=payload)

            print('haha', res.json())
            print('hehe')
            
            output = res.json().get("summary", res.json())
            print(f"🧠 Tool response from {tool_name}:\n", output)
            add_to_vector_store(question + "\n" + json.dumps(output))
    else:
        print("⚠️ Unexpected structure:", parsed)
