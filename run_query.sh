#!/bin/bash
# Wrapper script to run query with the correct Python version

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Find python3.14 in the venv or system
if [ -f "/Users/periscopelabs/RagOnBLD/Data/.venv/bin/python3.14" ]; then
    PYTHON="/Users/periscopelabs/RagOnBLD/Data/.venv/bin/python3.14"
elif command -v python3.14 &> /dev/null; then
    PYTHON="python3.14"
else
    echo "Python 3.14 not found. Please install it first."
    exit 1
fi

# Run the query script
cd "$SCRIPT_DIR"
$PYTHON rag_query.py "$@"
