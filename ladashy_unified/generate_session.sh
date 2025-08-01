#!/bin/bash
SECTION=$1

if [ -z "$SECTION" ]; then
    echo "Usage: ./generate_session.sh [01|02|03|04|05]"
    echo "  01 - Backend API"
    echo "  02 - Frontend"
    echo "  03 - Icons"
    echo "  04 - Dashboard"
    echo "  05 - Collectors"
    exit 1
fi

OUTPUT="SESSION_CONTEXT_$(date +%Y%m%d_%H%M%S).md"

echo "# LaDashy Session Context" > $OUTPUT
echo "## Working on: SECTION_$SECTION" >> $OUTPUT
echo "## Generated: $(date)" >> $OUTPUT
echo "" >> $OUTPUT
echo "Tell the AI you're working on Section $SECTION" >> $OUTPUT
echo "Ask it to check PROJECT_MANAGER.md for details" >> $OUTPUT

echo "✅ Created: $OUTPUT"
echo "📋 Upload this file to your AI chat!"
