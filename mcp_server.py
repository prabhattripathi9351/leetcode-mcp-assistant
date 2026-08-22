import json
import os
import asyncio
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# ---------- CONFIG ----------
import os
INDEX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.json")
# ---------------------------

# Index load karein
if not os.path.exists(INDEX_FILE):
    raise FileNotFoundError(f"❌ {INDEX_FILE} nahi mila. Pehle build_index_github.py chalao!")

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    ALL_PROBLEMS = json.load(f)

import sys
print(f"MCP Server starting... {len(ALL_PROBLEMS)} problems loaded.", file=sys.stderr)

# MCP Server instanceprint(f"✅ MCP Server starting... {len(ALL_PROBLEMS)} problems loaded.")
app = Server("leetcode-github-assistant")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_by_topic",
            description="Search solved problems by topic (e.g., 'array', 'dynamic-programming').",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic slug (e.g., 'array', 'dp', 'string')"
                    }
                },
                "required": ["topic"]
            }
        ),
        types.Tool(
            name="get_solution_code",
            description="Get the full code of a specific problem by filename (e.g., 'two-sum.cpp').",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem_name": {
                        "type": "string",
                        "description": "Filename or slug (e.g., '0877-stone-game.cpp' or 'stone-game')"
                    }
                },
                "required": ["problem_name"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "search_by_topic":
        topic = arguments.get("topic", "").lower()
        results = [p for p in ALL_PROBLEMS if topic in [t.lower() for t in p.get("tags", [])]]
        
        if not results:
            return [types.TextContent(type="text", text=f"❌ Topic '{topic}' se koi problem nahi mili.")]
        
        output = f"🔍 **{topic.upper()}** ({len(results)} problems):\n\n"
        for p in results:
            output += f"• {p['name']} (Difficulty: {p['difficulty']})\n"
        
        return [types.TextContent(type="text", text=output)]
    
    elif name == "get_solution_code":
        query = arguments.get("problem_name", "").lower()
        target = None
        
        # Exact match
        for p in ALL_PROBLEMS:
            if query == p['name'].lower() or query == p.get('slug', '').lower():
                target = p
                break
        
        # Partial match
        if not target:
            for p in ALL_PROBLEMS:
                if query in p['name'].lower() or query in p.get('slug', '').lower():
                    target = p
                    break
        
        if not target:
            return [types.TextContent(type="text", text=f"❌ Problem '{arguments.get('problem_name', '')}' nahi mili.")]
        
        # GitHub se code fetch karein
        url = target.get('download_url')
        if not url:
            return [types.TextContent(type="text", text="❌ Download URL nahi mila.")]
        
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                return [types.TextContent(type="text", text=f"❌ Code fetch fail: {resp.status_code}")]
            code = resp.text
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error: {str(e)}")]
        
        # Language detect
        ext = os.path.splitext(target['name'])[1].replace('.', '')
        lang_map = {
            "py": "python", "cpp": "cpp", "java": "java",
            "js": "javascript", "go": "go", "rb": "ruby", "c": "c"
        }
        lang = lang_map.get(ext, "text")
        
        return [types.TextContent(
            type="text",
            text=f"📄 **{target['name']}** (Difficulty: {target['difficulty']})\n\n```{lang}\n{code}\n```"
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

# ---------- SERVER RUN ----------
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())