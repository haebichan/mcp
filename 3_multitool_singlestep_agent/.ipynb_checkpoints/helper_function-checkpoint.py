from jsonschema import validate, ValidationError

# === Helper: validate RPC params against tool schema ===
def validate_params_against_args(tool_name, params, mcp_tools):
    tool = next((t for t in mcp_tools["tools"] if t["name"] == tool_name), None)
    if not tool:
        raise ValueError(f"❌ Tool '{tool_name}' not found in mcp_tools.yaml.")

    expected_args = set(tool.get("args", []))
    given_args = set(params.keys())

    missing = expected_args - given_args
    extra = given_args - expected_args

    if missing:
        raise ValueError(f"❌ Missing required args for '{tool_name}': {missing}")
    if extra:
        raise ValueError(f"❌ Unexpected args for '{tool_name}': {extra}")
