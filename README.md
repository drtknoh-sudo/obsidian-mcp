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
| 📅 **Auto frontmatter** | Automatically adds created/modified dates |

## 🆕 Auto Frontmatter (v0.2.0)

When creating a new note, the MCP automatically adds YAML frontmatter with:

```yaml
---
created: 2026-01-29
modified: 2026-01-29
tags: []
---
```

- **create_note**: Auto-generates `created` and `modified` dates
- **update_note**: Auto-updates `modified` date when editing
- Can be disabled with `auto_frontmatter: false`

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

### ⚡ Performance (Estimated)

| Operation | 20,000 notes |
|-----------|-------------|
| List notes | **0.17 sec** |
| Full content read | 0.63 sec |
| Full-text search | 0.66 sec |

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
%APPDATA%\Claude\claude_desktop_config.json
```

Add the obsidian server configuration:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/path/to/obsidian-mcp", "obsidian-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/your/vault"
      }
    }
  }
}
```

**Important:** Replace the paths with your actual paths:
- `/path/to/uv` → Find with `which uv` (e.g., `/Users/yourname/.local/bin/uv`)
- `/path/to/obsidian-mcp` → Where you cloned this repo
- `/path/to/your/vault` → Your Obsidian vault folder

### Step 4: Restart Claude Desktop

Completely quit and reopen Claude Desktop.

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `list_notes` | List notes (optional: filter by folder) |
| `get_note` | Read a specific note's content |
| `create_note` | Create a new note (auto-adds frontmatter with date) |
| `update_note` | Update an existing note (auto-updates modified date) |
| `delete_note` | Move a note to .trash |
| `search_notes` | Search by title |
| `full_text_search` | Search note content |
| `list_folders` | List all folders |
| `get_tags` | Get all tags |
| `get_vault_info` | Get vault statistics |

## 💬 Example Usage

Once configured, you can ask Claude:

- "List my recent notes"
- "Find notes about 'project planning'"
- "Create a new note called 'Meeting Notes' with today's date"
- "Search for notes containing 'API documentation'"
- "What tags do I use in my vault?"
- "Update my TODO note with a new item"

## 🔒 Security

- **100% Local**: All data stays on your machine
- **No API keys**: No external services required
- **Vault-sandboxed**: Cannot access files outside your vault
- **Safe delete**: Deletes move to .trash, not permanent

## 🐛 Troubleshooting

### "Vault not found"
Make sure `OBSIDIAN_VAULT_PATH` points to a valid Obsidian vault folder.

### "Server disconnected" in Claude Desktop
1. Check that `uv` path is correct (use full path)
2. Verify the obsidian-mcp directory path is correct
3. Check Claude Desktop logs for errors

### Permission denied (macOS)
Grant Full Disk Access to your terminal:
System Preferences → Security & Privacy → Privacy → Full Disk Access

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 🙏 Acknowledgments

- Built with [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- Inspired by the Obsidian community

