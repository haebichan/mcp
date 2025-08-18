# introspect_jsonrpc.py
import requests, json

MCP_RPC_URL = "http://127.0.0.1:8080/mcp/rpc"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def call(method, params=None, _id=1):
    payload = {"jsonrpc": "2.0", "method": method, "params": params or {}, "id": _id}
    resp = requests.post(MCP_RPC_URL, json=payload, headers=HEADERS)

    # Handle SSE or JSON body
    body = resp.text.strip()
    if body.startswith("data:"):
        for line in body.splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:])
    try:
        return resp.json()
    except Exception:
        print("Raw body:", body[:300])
        return None

def pretty(title, obj):
    print(f"\n=== {title} ===")
    print(json.dumps(obj, indent=2))

if __name__ == "__main__":
    tools = call("tools/list", _id=1)
    pretty("tools/list", tools)

    resources = call("resources/list", _id=2)
    pretty("resources/list", resources)

    read_csv = call("resources/read", {"uri": "resource://sample-csv"}, _id=3)
    pretty("resources/read (resource://sample-csv)", read_csv)
