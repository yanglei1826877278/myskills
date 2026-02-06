---
name: markdown-to-x
description: Convert Markdown documents to X (Twitter) compatible plain text format. Use when users need to post Markdown content to X (formerly Twitter), including threads, articles, or long-form posts. Triggers include "convert markdown to X", "md to twitter format", "post markdown to X", or any request involving Markdown and X/Twitter publishing.
allowed-tools: Bash(markdown-to-x:*)
---

# Markdown to X Format Converter

Convert Markdown documents to X-compatible plain text format.

## Basic Usage

```bash
# Convert a markdown file
markdown-to-x article.md

# Convert inline text
markdown-to-x "# Hello World"

# Read from stdin
echo "# My Post" | markdown-to-x -
```

## Options

| Option | Description |
|--------|-------------|
| `-m, --mode` | Output mode: `article` (default) or `thread` |
| `-l, --keep-links` | Keep links (default: true) |
| `-c, --code-style` | Code block style: `inline` (default), `blockquote`, `plain` |
| `-s, --max-length` | Max characters per tweet in thread mode (default: 280) |
| `-o, --output` | Output to file instead of stdout |

## Conversion Rules

### Headings

| Markdown | X Format |
|----------|----------|
| `# Title` | `Title` |
| `## Section` | `【Section】` |
| `### Subsection` | `— Subsection —` |

### Lists

| Markdown | X Format |
|----------|----------|
| `- Item` | `• Item` |
| `1. Step` | `1️⃣ Step` |

### Code

```markdown
`inline code`
```

⬇️

```
inline code
```

Code blocks are converted based on style:
- `inline`: Prefixed with "代码示例："
- `blockquote`: Prepended with `>`
- `plain`: Indented with spaces

### Links

```markdown
[OpenAI](https://openai.com)
```

⬇️

```
OpenAI https://openai.com
```

### Emphasis

| Markdown | X Format |
|----------|----------|
| `**bold**` | `【bold】` |
| `*italic*` | `👉 italic` |
| `~~deleted~~` | `deleted` |

## Examples

### Article Mode (Default)

Input:
```markdown
# Why X Doesn't Support Markdown

- Markdown is for documents
- X is for streaming reads

Conclusion: **Conversion needed**
```

Output:
```
Why X Doesn't Support Markdown

• Markdown is for documents
• X is for streaming reads

结论：【Conversion needed】
```

### Thread Mode

```bash
markdown-to-x long-article.md --mode thread
```

Output (array format):
```
[
  "First paragraph...",
  "Second paragraph...",
  "Third paragraph..."
]
```

## Common Use Cases

1. **X Premium Articles**: Convert full Markdown documents
2. **Twitter Threads**: Auto-split long content into tweet-sized chunks
3. **Technical Posts**: Share code snippets with proper formatting
4. **Blog Imports**: Republish Markdown blog posts to X

## Tips

- Use `--code-style plain` for minimal formatting
- Use `--mode thread` for Twitter threads (auto-splits)
- Use `-o output.txt` to save to file
