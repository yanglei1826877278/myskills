---
name: markdown-to-x
description: Convert Markdown documents to X (Twitter) compatible plain text format. Use when users need to post Markdown content to X (formerly Twitter), including threads, articles, or code snippets. Triggers include "convert markdown to X", "md to twitter format", "post markdown to X", or any request involving Markdown and X publishing.
allowed-tools: Bash(skills/markdown-to-x/scripts/markdown-to-x.py:*)
---

# Markdown to X Format Converter

Cleans Markdown syntax while preserving layout for posting to X/Twitter.

## Basic Usage

```bash
# Convert markdown file (output: article-twitter.md)
skills/markdown-to-x/scripts/markdown-to-x.py article.md

# Custom output path
skills/markdown-to-x/scripts/markdown-to-x.py article.md -o output.txt
```

## Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path (optional) |
| `-h, --help` | Show help message |

## Conversion Rules

### Headings
- `# Title` → `Title` (removed)

### Lists
- Unordered `- item` → stays as `- item`
- Ordered `1. step` → stays as `1. step`

### Code
- Code blocks ``` → removed
- Inline `code` → `code` (backticks removed)

### Links
- `[text](url)` → `text url`

### Emphasis
- `**bold**` → `bold`
- `*italic*` → `italic`
- `~~deleted~~` → `deleted`

### Images
- `![alt](url)` → removed

## Example

Input:
```markdown
# Why X Doesn't Support Markdown

- Markdown is for documents
- X is for streaming reads

Conclusion: **Conversion needed**
```

Output (`article-twitter.md`):
```
Why X Doesn't Support Markdown

- Markdown is for documents
- X is for streaming reads

结论: Conversion needed
```

## Common Use Cases

1. **X Premium Articles**: Convert full Markdown documents
2. **Technical Posts**: Share code snippets without markdown formatting
3. **Blog Imports**: Republish Markdown blog posts to X

## Tips

- Output file: `xxx-twitter.md` (auto-generated)
- Use `-o` to specify custom output path
