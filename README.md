🤖 LeetCode GitHub MCP Assistant

**Turn your personal LeetCode solutions repo into a queryable AI tool — right inside Claude Desktop.**

GitHub Repo → Metadata Index → MCP Server → Claude Desktop (natural language queries)

Python 3.x | MCP SDK | GitHub REST API | LeetCode GraphQL API | MIT License

---

## 🧠 What is this?

This project connects a personal GitHub repository of solved LeetCode problems directly to **Claude Desktop** using the **Model Context Protocol (MCP)**. Instead of manually browsing GitHub to find "all array problems I've solved" or hunting for one specific solution file, you can just ask Claude Desktop in plain language — and it answers using live data pulled straight from your repo.

*Built as a personal productivity tool to make DSA/LeetCode practice searchable and reviewable through conversation, instead of manual file digging.*

It surfaces:
- Every solved problem tagged by **topic** (array, dynamic-programming, graph, etc.)
- Each problem's **difficulty** (easy/medium/hard), pulled from LeetCode itself
- The **full solution code**, fetched live from GitHub on demand

---

## ✨ Features

| Capability | Description |
|---|---|
| 🔍 **Topic-based search** | Ask for any topic (e.g. "array", "dynamic-programming") and get every matching solved problem with its difficulty |
| 📄 **Live code retrieval** | Fetch the complete solution code for any problem by name or slug, straight from GitHub |
| 🏷️ **Auto-tagging** | Difficulty and topic tags are pulled automatically from LeetCode's own GraphQL API — no manual tagging needed |
| ⚡ **Fast parallel indexing** | Uses multithreading to fetch metadata for every problem concurrently instead of one-by-one |
| 🔌 **Native Claude Desktop integration** | Runs as a local MCP server — no browser tab switching, no copy-pasting links |

---

## 🏗️ Architecture & Pipeline

```
┌─────────────────────────┐
│   GitHub Repo            │   → your solved LeetCode .py/.cpp/.java files
│   Daily_leet_code         │
└────────────┬─────────────┘
             │  GitHub REST API (recursive file listing)
             ▼
┌─────────────────────────┐
│  build_index_github.py   │   → extracts slug from filename
│      (Indexer)            │   → queries LeetCode GraphQL for
└────────────┬─────────────┘     difficulty + topic tags (parallel)
             │  writes
             ▼
┌─────────────────────────┐
│      index.json           │   → local structured metadata store
└────────────┬─────────────┘
             │  loaded at startup
             ▼
┌─────────────────────────┐
│    mcp_server.py          │   → exposes 2 tools over stdio:
│   (MCP Server)             │     search_by_topic, get_solution_code
└────────────┬─────────────┘
             │  MCP / JSON-RPC over stdio
             ▼
┌─────────────────────────┐
│     Claude Desktop        │   → "array topic ke problems batao"
│   (spawns server locally) │   → "0877-stone-game ka code dikhao"
└─────────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.x |
| MCP Server | `mcp` SDK (`mcp.server.Server`, stdio transport) |
| Data Source | GitHub REST API, LeetCode GraphQL API |
| Concurrency | `concurrent.futures.ThreadPoolExecutor` |
| HTTP Client | `requests` |
| Client | Claude Desktop (local MCP server config) |

---

## 📁 Project Structure

```
Leetcode_mcp_server/
├── build_index_github.py   # Indexer: scans GitHub repo, builds index.json
├── mcp_server.py            # MCP server: exposes search_by_topic & get_solution_code
├── index.json                # Auto-generated metadata index (gitignored)
├── requirements.txt          # Python dependencies
└── .gitignore
```

---

## 🔌 Tool Reference (MCP Tools)

| Tool | Input | Description |
|---|---|---|
| `search_by_topic` | `topic: string` (e.g. `"array"`) | Returns all solved problems tagged with that topic, with difficulty |
| `get_solution_code` | `problem_name: string` (e.g. `"0877-stone-game.py"` or `"stone-game"`) | Fetches and returns the full solution code live from GitHub |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A GitHub repo of your own solved LeetCode problems (public, or add a token for private repos)
- [Claude Desktop](https://claude.ai/download) installed

### 1. Clone & install dependencies
```bash
git clone https://github.com/<your-username>/<this-repo>.git
cd <this-repo>
pip install -r requirements.txt
```

### 2. Configure your repo name
Open `build_index_github.py` and set:
```python
GITHUB_REPO = "your-username/your-leetcode-repo"
```

### 3. Build the index
```bash
python build_index_github.py
```
This creates `index.json` with every problem's difficulty and topic tags.

### 4. Connect to Claude Desktop
Open Claude Desktop → **Settings → Developer → Edit Config**, and add:
```json
{
  "mcpServers": {
    "leetcode-github-assistant": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

> 💡 On Windows, use double backslashes in the path (e.g. `"D:\\Leetcode_mcp_server\\mcp_server.py"`), and use `python.exe`'s full path if `python` isn't on your system PATH.

### 5. Restart Claude Desktop
Fully quit (End Task in Task Manager, not just close the window) and reopen. Check **Settings → Developer** — the server should show status `running`.

### 6. Ask away
```
"array topic ke problems batao"
"show me the code for two-sum"
```

---

## 🗺️ Roadmap Ideas

- [ ] Add difficulty-based filtering tool (e.g. "show me all hard problems")
- [ ] Add a "random problem suggestion" tool for practice
- [ ] Auto-sync index whenever new commits are pushed to the repo (webhook or scheduled rebuild)
- [ ] Support private repos via GitHub personal access token
- [ ] Add retry/caching logic for LeetCode GraphQL calls to reduce indexing time

---

## 🤝 Contributing

This is a personal learning project, but issues and suggestions are welcome — feel free to open a PR or an issue.

---

*Built to make personal LeetCode practice conversational — instead of digging through GitHub folders, just ask.*
