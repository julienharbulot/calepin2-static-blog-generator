#!/bin/bash

# path to directory containing this script
# see https://stackoverflow.com/a/246128
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

python -m calepin "$SCRIPT_DIR/input" "$SCRIPT_DIR/output"