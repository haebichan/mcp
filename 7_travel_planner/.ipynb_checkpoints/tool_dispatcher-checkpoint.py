# tool_dispatcher.py

import json
import requests
import importlib

TOOL_FUNCTIONS = {
    "flight_search": "flight_search",
    "hotel_finder": "hotel_finder",
    "weather_lookup": "weather_lookup",
    "budget_estimator": "budget_estimator"
}

def handle_user_input(user_question, tools_description):
    from openai import OpenAI
    import os
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Build the prompt
    prompt = f"""
You are a tool planner. Given a user's travel question, select the right tools and call them with the proper parameters.
Respond in JSON list format. Only use available tools. User question: "{user_question}"
Tools:
{json.dumps(tools_description, indent=2)}
"""

    print("\U0001F50D GPT response:")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    tool_plan = json.loads(response.choices[0].message.content)
    print(json.dumps(tool_plan, indent=2))

    # Execute tools
    for tool in tool_plan:
        tool_name = tool["tool_name"]
        params = tool["parameters"]

        if tool_name in TOOL_FUNCTIONS:
            module = importlib.import_module(TOOL_FUNCTIONS[tool_name])
            result = module.run(params)
            print(f"\U0001F9E0 Tool response from {tool_name}:\n", result)
        else:
            print(f"Unknown tool: {tool_name}")
