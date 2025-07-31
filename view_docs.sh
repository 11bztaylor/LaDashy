#!/bin/bash
# Open the generated documentation

DOCS_DIR="${1:-test_docs}"

if [ ! -d "$DOCS_DIR" ]; then
    echo "Documentation directory not found: $DOCS_DIR"
    echo "Usage: ./view_docs.sh [docs_directory]"
    exit 1
fi

# Check if dashboard.html exists
if [ -f "$DOCS_DIR/dashboard.html" ]; then
    echo "Opening HTML dashboard..."
    xdg-open "$DOCS_DIR/dashboard.html" 2>/dev/null || open "$DOCS_DIR/dashboard.html" 2>/dev/null || echo "Please open $DOCS_DIR/dashboard.html in your browser"
else
    echo "Opening documentation directory..."
    xdg-open "$DOCS_DIR" 2>/dev/null || open "$DOCS_DIR" 2>/dev/null || echo "Documentation is in: $DOCS_DIR"
fi
