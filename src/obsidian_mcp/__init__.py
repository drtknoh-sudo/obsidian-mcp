"""
Obsidian MCP Server - Read and write Obsidian vault files

A fast, local MCP server that provides full read/write access to your 
Obsidian vault. No API keys, no rate limits, works offline.
"""

import os
import json
import asyncio
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Vault path from environment variable or default
DEFAULT_VAULT_PATH = os.path.expanduser("~/Obsidian Vault")
VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", DEFAULT_VAULT_PATH)

server = Server("obsidian-mcp")


def get_vault_path() -> Path:
    """Get the configured vault path."""
    return Path(VAULT_PATH)


def is_hidden_or_system(path: Path) -> bool:
    """Check if path should be excluded (hidden, .obsidian, .trash)."""
    path_str = str(path)
    return ".obsidian" in path_str or ".trash" in path_str or any(
        part.startswith(".") for part in path.parts
    )


def list_markdown_files(folder: Optional[str] = None, limit: int = 50) -> list[dict]:
    """List markdown files in the vault."""
    vault = get_vault_path()
    search_path = vault / folder if folder else vault
    
    if not search_path.exists():
        return []
    
    files = []
    for md_file in search_path.rglob("*.md"):
        if is_hidden_or_system(md_file):
            continue
        
        try:
            stat = md_file.stat()
            files.append({
                "name": md_file.stem,
                "path": str(md_file.relative_to(vault)),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size
            })
        except (OSError, ValueError):
            continue
        
        if len(files) >= limit:
            break
    
    return sorted(files, key=lambda x: x["modified"], reverse=True)


def read_note(path: str) -> dict:
    """Read a note's content."""
    vault = get_vault_path()
    file_path = vault / path
    
    if not file_path.exists():
        return {"error": f"File not found: {path}"}
    
    if not str(file_path.resolve()).startswith(str(vault.resolve())):
        return {"error": "Access denied: path outside vault"}
    
    try:
        content = file_path.read_text(encoding="utf-8")
        stat = file_path.stat()
        
        return {
            "name": file_path.stem,
            "path": path,
            "content": content,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size": stat.st_size
        }
    except Exception as e:
        return {"error": str(e)}


def write_note(path: str, content: str) -> dict:
    """Write content to a note (create or update)."""
    vault = get_vault_path()
    
    # Ensure .md extension
    if not path.endswith(".md"):
        path = path + ".md"
    
    file_path = vault / path
    
    # Security check
    if not str(file_path.resolve()).startswith(str(vault.resolve())):
        return {"error": "Access denied: path outside vault"}
    
    try:
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        
        return {
            "success": True,
            "path": path,
            "message": f"Note saved: {path}"
        }
    except Exception as e:
        return {"error": str(e)}


def search_by_title(query: str, limit: int = 20) -> list[dict]:
    """Search notes by title."""
    vault = get_vault_path()
    results = []
    query_lower = query.lower()
    
    for md_file in vault.rglob("*.md"):
        if is_hidden_or_system(md_file):
            continue
        
        if query_lower in md_file.stem.lower():
            try:
                stat = md_file.stat()
                results.append({
                    "name": md_file.stem,
                    "path": str(md_file.relative_to(vault)),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except (OSError, ValueError):
                continue
            
            if len(results) >= limit:
                break
    
    return results


def full_text_search(query: str, limit: int = 20) -> list[dict]:
    """Search within note content."""
    vault = get_vault_path()
    results = []
    query_lower = query.lower()
    
    for md_file in vault.rglob("*.md"):
        if is_hidden_or_system(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding="utf-8")
            if query_lower in content.lower():
                # Find snippet around the match
                idx = content.lower().find(query_lower)
                start = max(0, idx - 50)
                end = min(len(content), idx + len(query) + 50)
                snippet = content[start:end].replace("
", " ")
                
                stat = md_file.stat()
                results.append({
                    "name": md_file.stem,
                    "path": str(md_file.relative_to(vault)),
                    "snippet": f"...{snippet}...",
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
                
                if len(results) >= limit:
                    break
        except Exception:
            continue
    
    return results


def list_folders() -> list[str]:
    """List all folders in the vault."""
    vault = get_vault_path()
    folders = []
    
    for item in vault.rglob("*"):
        if item.is_dir() and not is_hidden_or_system(item):
            folders.append(str(item.relative_to(vault)))
    
    return sorted(folders)


def get_tags() -> dict:
    """Get all tags used in the vault."""
    vault = get_vault_path()
    tags = {}
    
    for md_file in vault.rglob("*.md"):
        if is_hidden_or_system(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding="utf-8")
            # Find hashtags (supports Korean and other Unicode)
            found_tags = re.findall(r"#([\w\u0080-\uffff]+)", content)
            for tag in found_tags:
                if tag not in tags:
                    tags[tag] = []
                tags[tag].append(md_file.stem)
        except Exception:
            continue
    
    return tags


def delete_note(path: str) -> dict:
    """Move a note to .trash folder."""
    vault = get_vault_path()
    file_path = vault / path
    
    if not file_path.exists():
        return {"error": f"File not found: {path}"}
    
    if not str(file_path.resolve()).startswith(str(vault.resolve())):
        return {"error": "Access denied: path outside vault"}
    
    try:
        trash_path = vault / ".trash" / path
        trash_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.rename(trash_path)
        return {"success": True, "message": f"Moved to trash: {path}"}
    except Exception as e:
        return {"error": str(e)}


def get_vault_info() -> dict:
    """Get vault statistics."""
    vault = get_vault_path()
    
    if not vault.exists():
        return {"error": f"Vault not found: {vault}"}
    
    notes = [f for f in vault.rglob("*.md") if not is_hidden_or_system(f)]
    folders = [d for d in vault.rglob("*") if d.is_dir() and not is_hidden_or_system(d)]
    
    return {
        "vault_path": str(vault),
        "note_count": len(notes),
        "folder_count": len(folders)
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_notes",
            description="List markdown notes in the Obsidian vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder": {"type": "string", "description": "Optional folder path to filter"},
                    "limit": {"type": "integer", "description": "Max results (default 50)", "default": 50}
                }
            }
        ),
        Tool(
            name="get_note",
            description="Read a note's content by path",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the note (e.g., 'folder/note.md')"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="create_note",
            description="Create a new note or overwrite existing",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path for the note (e.g., 'folder/note.md')"},
                    "content": {"type": "string", "description": "Markdown content"}
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="update_note",
            description="Update an existing note's content",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the note"},
                    "content": {"type": "string", "description": "New markdown content"}
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="search_notes",
            description="Search notes by title",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 20}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="full_text_search",
            description="Search within note content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 20}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_folders",
            description="List all folders in the vault",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_tags",
            description="Get all tags used in the vault",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="delete_note",
            description="Delete a note (moves to .trash)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the note to delete"}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_vault_info",
            description="Get vault statistics and info",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_notes":
            result = list_markdown_files(
                folder=arguments.get("folder"),
                limit=arguments.get("limit", 50)
            )
        elif name == "get_note":
            result = read_note(arguments["path"])
        elif name == "create_note":
            result = write_note(arguments["path"], arguments["content"])
        elif name == "update_note":
            result = write_note(arguments["path"], arguments["content"])
        elif name == "search_notes":
            result = search_by_title(
                arguments["query"],
                limit=arguments.get("limit", 20)
            )
        elif name == "full_text_search":
            result = full_text_search(
                arguments["query"],
                limit=arguments.get("limit", 20)
            )
        elif name == "list_folders":
            result = list_folders()
        elif name == "get_tags":
            result = get_tags()
        elif name == "delete_note":
            result = delete_note(arguments["path"])
        elif name == "get_vault_info":
            result = get_vault_info()
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


def main():
    """Main entry point."""
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
    
    asyncio.run(run())


if __name__ == "__main__":
    main()

