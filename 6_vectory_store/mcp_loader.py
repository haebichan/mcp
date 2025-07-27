# mcp_loader.py

import yaml

def load_mcp_tools():
    with open("mcp_tools.yaml", "r") as f:
        tools_yaml = yaml.safe_load(f)
    descriptions = []
    for tool in tools_yaml.get("tools", []):
        param_str = ", ".join(f"{arg}: str" for arg in tool.get("args", []))
        descriptions.append(f"Tool: {tool['name']}({param_str})")
    return "\n\n".join(descriptions)
