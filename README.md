# obsidian-mcp

[한국어](README.ko.md)

A fast MCP (Model Context Protocol) server that gives AI assistants **full read/write access** to your Obsidian vault.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📖 **Read notes** | Get content from any note in your vault |
| ✏️ **Create notes** | Create new notes with markdown content |
| 📝 **Update notes** | Modify existing notes |
| 🗑️ **Delete notes** | Safely move notes to trash |
| 🔍 **Search by title** | Find notes by their filename |
| 📄 **Full-text search** | Search within note content |
| 📁 **Browse folders** | Navigate your vault structure |
| 🏷️ **Get tags** | List all tags used across your vault |

## 🚀 Why This?

| | obsidian-mcp | Cloud APIs |
|---|:---:|:---:|
| Read notes | ✅ | ✅ |
| **Write notes** | ✅ | ❌ |
| Speed | ⚡ Instant | 🐌 Network delay |
| Offline | ✅ | ❌ |
| Rate limits | None | Yes |
| API keys | Not needed | Required |
| Privacy | 100% local | Cloud sync |

## 📋 Requirements

- Python 3.10+
- [Obsidian](https://obsidian.md/) installed
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

## 📦 Installation

### Step 1: Clone this repository

```bash
git clone https://github.com/drtknoh-sudo/obsidian-mcp.git
cd obsidian-mcp
```

### Step 2: Install dependencies

```bash
uv sync
```

### Step 3: Configure Claude Desktop

Open your Claude Desktop config file:

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude