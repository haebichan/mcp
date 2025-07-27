# client_loop.py

import uuid
from mcp_loader import load_mcp_tools
from memory_utils import fetch_memory_summary
from vector_memory import check_similarity
from tool_dispatcher import handle_user_input

SESSION_ID = str(uuid.uuid4())
print(f"\U0001F4D8 New Session: {SESSION_ID}")

tools_description = load_mcp_tools()

while True:
    user_question = input("\nEnter your question (or type 'exit'): ").strip()
    if user_question.lower() in ("exit", "quit"):
        break

    # Optional: Vector similarity check
    similar_entry = check_similarity(user_question)
    if similar_entry:
        print("\U0001F50E Found similar prior query. Response:")
        print(similar_entry)
        continue

    # Build memory context
    memory_context = fetch_memory_summary(SESSION_ID)

    # Handle input with tool planning + execution
    handle_user_input(user_question, tools_description, memory_context, SESSION_ID)
