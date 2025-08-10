import requests
import json
import os
import openai

openai.api_key = os.environ['OPENAI_API_KEY']

MCP_URL = "http://localhost:8080/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def parse_sse_response(response_text):
    """Extract JSON from Server-Sent Events response."""
    for line in response_text.strip().split('\n'):
        if line.startswith('data: '):
            return json.loads(line[6:])
    return None

def mcp_call(method, params=None):
    """Make a call to the MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": 1
    }
    resp = requests.post(MCP_URL, json=payload, headers=HEADERS)
    if resp.status_code == 200:
        return parse_sse_response(resp.text)
    return None

def get_tools():
    """Get available tools."""
    result = mcp_call("tools/list")
    return result.get("result", {}).get("tools", []) if result else []

def get_resources():
    """Get available resources."""
    result = mcp_call("resources/list")
    return result.get("result", {}).get("resources", []) if result else []

def call_tool(tool_name, args):
    """Call a tool."""
    result = mcp_call("tools/call", {"name": tool_name, "arguments": args})
    if result and "result" in result and "content" in result["result"]:
        return result["result"]["content"][0]["text"]
    return None

def get_csv_data():
    """Get CSV data from resource."""
    result = mcp_call("resources/read", {"uri": "resource://sample-csv"})
    if result and "result" in result and "contents" in result["result"]:
        return result["result"]["contents"][0]["text"]
    return None

def agent_loop(user_question):
    tools = get_tools()
    resources = get_resources()
    
    # Format available tools and resources for GPT
    tools_desc = "\n".join([f"- {t['name']}: {t.get('description', '')}" for t in tools])
    resources_desc = "\n".join([f"- {r['uri']}: {r.get('description', '')}" for r in resources])
    
    context = f"User question: {user_question}\n"
    
    for turn in range(5):  # Max 5 turns
        prompt = f"""
        You have these tools: {tools_desc}
        You have these resources: {resources_desc}
        
        Context: {context}
        
        User asked: "{user_question}"
        
        Choose the best tool to answer this question. If the question is answered, return {{"tool": "none"}}.
        
        Return JSON: {{"tool": "tool_name", "args": {{"param": "value"}}}}
        """
        print('Prompt: ', prompt)
        
        # Get GPT's decision
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            plan = json.loads(response.choices[0].message.content.strip())
        except:
            print("Failed to parse GPT response")
            break

        print('Plan: ', plan)
        
        tool_name = plan.get("tool")
        args = plan.get("args", {})
        
        if tool_name == "none":
            print("Task completed!")
            break
            
        print(f"Calling {tool_name} with {args}")
        
        # Auto-inject CSV data if needed
        if "csv_text" in args:
            csv_data = get_csv_data()
            if csv_data:
                args["csv_text"] = csv_data
                print("Injected CSV data")

        
        # Call the tool
        result = call_tool(tool_name, args)
        if not result:
            print(f"Tool {tool_name} failed")
            break
            
        print(f"Result: {result}\n")
        context += f"Tool {tool_name} returned: {result}\n"
        
        # Stop if we got a good summary
        if len(result) > 200 and any(word in result.lower() for word in ["summary", "analysis", "total"]):
            print("Got comprehensive answer, stopping.")
            break

if __name__ == "__main__":
    question = input("Enter your question: ")
    agent_loop(question)