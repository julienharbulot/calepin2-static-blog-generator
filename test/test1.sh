#!/bin/bash
set -euo pipefail

# path to directory containing this script
# see https://stackoverflow.com/a/246128
TEST_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

EXAMPLE_DIR="$TEST_DIR/../example"

"$EXAMPLE_DIR/compile.sh"
DIFF="$(diff "$EXAMPLE_DIR/output/example.html" "$TEST_DIR/data/expected.html")"

[ -z "$DIFF" ] && echo "ok" || (echo "Error" && echo "$DIFF")