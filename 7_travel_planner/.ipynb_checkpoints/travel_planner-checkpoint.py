# travel_planner/client_loop.py

import uuid
from mcp_loader import load_mcp_tools
from tool_dispatcher import handle_user_input

SESSION_ID = str(uuid.uuid4())
print(f"📘 New Session: {SESSION_ID}\n")

# Load MCP tools from YAML
tools_description = load_mcp_tools("mcp_tools.yaml")
memory_context = []  # Optional: vector memory to persist preferences

while True:
    user_question = input("Enter your travel request (or type 'exit'): ")
    if user_question.lower() == 'exit':
        break

    try:
        handle_user_input(user_question, tools_description, memory_context, SESSION_ID)
    except Exception as e:
        print(f"❌ Error: {e}")
