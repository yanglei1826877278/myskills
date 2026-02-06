#!/bin/bash
set -e

# Markdown to X (Twitter) format converter
# Converts Markdown documents to X-compatible plain text format

show_help() {
    cat << EOF
Markdown to X Format Converter

USAGE:
    markdown-to-x <input> [OPTIONS]

ARGUMENTS:
    input                 Markdown content or .md file path

OPTIONS:
    -m, --mode            Output mode: article (default) or thread
    -l, --keep-links      Keep links (default: true)
    -c, --code-style      Code block style: inline (default), blockquote, plain
    -s, --max-length      Max section length for thread mode (default: 280)
    -o, --output          Output file path (optional)
    -h, --help            Show this help message

EXAMPLES:
    # Convert markdown file to X format (article mode)
    markdown-to-x article.md

    # Convert inline markdown text
    echo "# Hello" | markdown-to-x -

    # Thread mode with custom length
    markdown-to-x article.md --mode thread --max-length 250

    # Plain code style
    markdown-to-x article.md --code-style plain
EOF
}

# Parse arguments
INPUT=""
MODE="article"
KEEP_LINKS=true
CODE_STYLE="inline"
MAX_LENGTH=280
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -l|--keep-links)
            KEEP_LINKS="$2"
            shift 2
            ;;
        -c|--code-style)
            CODE_STYLE="$2"
            shift 2
            ;;
        -s|--max-length)
            MAX_LENGTH="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            INPUT="$1"
            shift
            ;;
    esac
done

# Read input
if [[ -z "$INPUT" ]]; then
    echo "Error: Input is required" >&2
    show_help
    exit 1
fi

if [[ "$INPUT" == "-" ]]; then
    # Read from stdin
    MARKDOWN=$(cat)
elif [[ -f "$INPUT" && "$INPUT" == *.md ]]; then
    MARKDOWN=$(cat "$INPUT")
else
    MARKDOWN="$INPUT"
fi

# Conversion functions
convert_title_h1() {
    echo "$1" | sed 's/^# \(.*\)/\1/'
}

convert_title_h2() {
    echo "$1" | sed 's/^## \(.*\)/【\1】/'
}

convert_title_h3() {
    echo "$1" | sed 's/^### \(.*\)/— \1 —/'
}

convert_unordered_list() {
    echo "$1" | sed 's/^-\s*/• /'
}

convert_ordered_list() {
    echo "$1" | sed -E 's/^([0-9]+)\)\s*/\1️⃣ /'
}

convert_code_inline() {
    local content="$1"
    local style="${2:-inline}"

    case "$style" in
        inline)
            echo "$content" | sed 's/`\([^`]*\)`/\1/g'
            ;;
        blockquote)
            echo "$content" | sed 's/`\([^`]*\)`/> \1/g'
            ;;
        plain|"")
            echo "$content" | sed 's/`\([^`]*\)`/\1/g'
            ;;
    esac
}

convert_code_block() {
    local content="$1"
    local style="${2:-inline}"

    # Extract code content between ``` and ```
    # First, remove the opening ```
    content=$(echo "$content" | sed '/^```/,/^```/d')

    case "$style" in
        inline)
            # Convert to "Code: ..." format
            content=$(echo "$content" | sed 's/^/代码示例：/')
            ;;
        blockquote)
            # Add > prefix
            content=$(echo "$content" | sed 's/^/> /')
            ;;
        plain|"")
            content=$(echo "$content" | sed 's/^/    /')
            ;;
    esac

    echo "$content"
}

convert_link() {
    local content="$1"
    local keep_links="${2:-true}"

    if [[ "$keep_links" == "true" ]]; then
        # Convert [text](url) to "text url"
        echo "$content" | sed -E 's/\[([^\]]+)\]\(([^)]+)\)/\1 \2/g'
    else
        # Keep only text
        echo "$content" | sed -E 's/\[([^\]]+)\]\(([^)]+)\)/\1/g'
    fi
}

convert_bold() {
    echo "$1" | sed 's/\*\*/【/g; s/\*\*/】/g'
}

convert_italic() {
    echo "$1" | sed 's/\*/👉 /g; s/\*/ /g'
}

convert_strikethrough() {
    echo "$1" | sed 's/~~//g'
}

# Main conversion function
convert_markdown() {
    local markdown="$1"
    local code_style="${2:-inline}"
    local keep_links="${3:-true}"

    # Store result
    local result=""

    # Process line by line
    while IFS= read -r line; do
        local converted="$line"

        # Skip code block markers (they'll be handled specially)
        if [[ "$line" == "```"* ]]; then
            continue
        fi

        # Convert headings
        if [[ "$line" =~ ^#\  ]]; then
            converted=$(convert_title_h1 "$line")
        elif [[ "$line" =~ ^##\  ]]; then
            converted=$(convert_title_h2 "$line")
        elif [[ "$line" =~ ^###\  ]]; then
            converted=$(convert_title_h3 "$line")
        # Convert lists
        elif [[ "$line" =~ ^-\  ]]; then
            converted=$(convert_unordered_list "$line")
        elif [[ "$line" =~ ^[0-9]+\)\  ]]; then
            converted=$(convert_ordered_list "$line")
        else
            # Inline conversions
            converted=$(convert_link "$converted" "$keep_links")
            converted=$(convert_code_inline "$converted" "$code_style")
            converted=$(convert_bold "$converted")
            converted=$(convert_italic "$converted")
            converted=$(convert_strikethrough "$converted")
        fi

        echo "$converted"
    done <<< "$markdown"
}

# Handle code blocks specially
convert_full() {
    local markdown="$1"
    local code_style="${2:-inline}"
    local keep_links="${3:-true}"

    # Check if we're inside a code block
    local in_code_block=false
    local code_content=""

    while IFS= read -r line; do
        if [[ "$line" == "```"* ]]; then
            if [[ "$in_code_block" == "false" ]]; then
                # Starting code block
                in_code_block=true
                code_content=""
            else
                # Ending code block - convert and output
                in_code_block=false
                echo "$code_content" | convert_code_block "" "$code_style"
            fi
        elif [[ "$in_code_block" == "true" ]]; then
            # Inside code block - accumulate content
            code_content="${code_content}${line}"$'\n'
        else
            # Outside code block - normal conversion
            local converted="$line"

            # Convert headings
            if [[ "$line" =~ ^#\  ]]; then
                converted=$(convert_title_h1 "$line")
            elif [[ "$line" =~ ^##\  ]]; then
                converted=$(convert_title_h2 "$line")
            elif [[ "$line" =~ ^###\  ]]; then
                converted=$(convert_title_h3 "$line")
            # Convert lists
            elif [[ "$line" =~ ^-\  ]]; then
                converted=$(convert_unordered_list "$line")
            elif [[ "$line" =~ ^[0-9]+\)\  ]]; then
                converted=$(convert_ordered_list "$line")
            else
                # Inline conversions
                converted=$(convert_link "$converted" "$keep_links")
                converted=$(convert_code_inline "$converted" "$code_style")
                converted=$(convert_bold "$converted")
                converted=$(convert_italic "$converted")
                converted=$(convert_strikethrough "$converted")
            fi

            echo "$converted"
        fi
    done <<< "$markdown"
}

# Normalize blank lines
normalize_blank_lines() {
    # Replace multiple blank lines with single blank line
    awk '
    /^[[:space:]]*$/ { blank++; next }
    {
        while (blank > 0) { print ""; blank-- }
        print
    }
    '
}

# Thread mode - split into chunks
split_into_thread() {
    local max_len="${1:-280}"

    # This is a simplified implementation
    # Split by double newlines (paragraphs) first
    awk -v RS= -v ORS='\n\n' '1' | \
    awk -v max="$max_len" '
    {
        # If paragraph fits in one tweet
        if (length($0) <= max) {
            print
            next
        }

        # Split long paragraph by sentences
        gsub(/\. /, ".\n", $0)
        gsub(/\? /, "?\n", $0)
        gsub(/! /, "!\n", $0)

        current=""
        n = split($0, sentences, "\n")
        for (i = 1; i <= n; i++) {
            if (length(current) + length(sentences[i]) + 1 <= max) {
                if (current != "") current = current " " sentences[i]
                else current = sentences[i]
            } else {
                if (current != "") print current
                current = sentences[i]
            }
        }
        if (current != "") print current
    }
    '
}

# Execute conversion
convert() {
    local mode="${1:-article}"
    local code_style="${2:-inline}"
    local keep_links="${3:-true}"
    local max_len="${4:-280}"

    if [[ "$mode" == "thread" ]]; then
        echo "$MARKDOWN" | convert_full "$code_style" "$keep_links" | \
        normalize_blank_lines | \
        split_into_thread "$max_len"
    else
        echo "$MARKDOWN" | convert_full "$code_style" "$keep_links" | \
        normalize_blank_lines
    fi
}

# Run conversion
OUTPUT=$(convert "$MODE" "$CODE_STYLE" "$KEEP_LINKS" "$MAX_LENGTH")

# Output
if [[ -n "$OUTPUT_FILE" ]]; then
    echo "$OUTPUT" > "$OUTPUT_FILE"
    echo "Output written to: $OUTPUT_FILE"
else
    echo "$OUTPUT"
fi
