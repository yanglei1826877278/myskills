#!/usr/bin/env python3
"""
Markdown to X (Twitter) Format Converter

Cleans Markdown syntax while preserving layout for posting to X/Twitter.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def show_help():
    print("""Markdown to X Format Converter

USAGE:
    python markdown-to-x.py <input> [OPTIONS]

ARGUMENTS:
    input                 Markdown file path (required)

OPTIONS:
    -o, --output          Output file path (optional)
    -h, --help            Show this help message

EXAMPLES:
    # Convert markdown file (output: article-twitter.md)
    python markdown-to-x.py article.md

    # Custom output path
    python markdown-to-x.py article.md -o output.txt
""")


def clean_markdown(text: str) -> str:
    """Clean markdown syntax while preserving layout"""

    # 1. 去掉标题 #
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

    # 2. 去掉加粗/斜体
    text = re.sub(r'\*\*|__|\*', '', text)

    # 3. 去掉图片 ![...](...)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # 4. 优化链接格式 [text](url) -> text url
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 \2', text)

    # 5. 去掉代码块标记 ```bash 等
    text = re.sub(r'```[\w]*|```', '', text)

    # 6. 去掉行内代码标记 `
    text = text.replace('`', '')

    # Remove all blank lines (X will auto-adjust spacing)
    lines = [line for line in text.split('\n') if line.strip()]
    text = '\n'.join(lines)

    return text.strip()


def get_default_output_path(input_path: str) -> str:
    """Generate default output path based on input file"""
    path = Path(input_path)
    return str(path.with_name(path.stem + '-twitter.md'))


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('input', nargs='?', default='')
    parser.add_argument('-o', '--output', default='')
    parser.add_argument('-h', '--help', action='store_true')

    args = parser.parse_args()

    if args.help:
        show_help()
        return 0

    if not args.input:
        print("Error: Input file is required", file=sys.stderr)
        show_help()
        return 1

    # Read input
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1

    markdown = Path(args.input).read_text(encoding='utf-8')

    # Clean markdown
    cleaned = clean_markdown(markdown)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = get_default_output_path(args.input)

    # Write output
    Path(output_path).write_text(cleaned, encoding='utf-8')
    print(f"Output written to: {output_path}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
