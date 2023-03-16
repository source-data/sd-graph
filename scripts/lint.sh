#!/bin/bash

# If any command fails, exit immediately with that command's exit status
set -eo pipefail

# use a bash array to pass multiple dirs as arguments
sources=(
    "peerreview/summarization.py"
    "peerreview/gpt.py"
    "peerreview/test_summarization.py"
    "peerreview/queries.py"
)

ruff check "${sources[@]}"
echo "ruff passed!"

# ca. 90 is the max line length for black & ruff
flake8 --max-line-length 90 "${sources[@]}"
echo "flake8 passed!"

black --check "${sources[@]}"
echo "black passed!"
