#!/bin/bash

# If any command fails, exit immediately with that command's exit status
set -eo pipefail

# use a bash array to pass multiple dirs as arguments
lintable_sources=(
    "peerreview/gpt.py"
    "peerreview/mecadoi.py"
    "peerreview/queries.py"
    "peerreview/summarization.py"
    "peerreview/test_mecadoi.py"
    "peerreview/test_summarization.py"
    "tests/"
)

echo "checking ${lintable_sources[@]}"

ruff check "${lintable_sources[@]}"
echo "ruff passed!"

# ca. 90 is the max line length for black & ruff
flake8 --max-line-length 90 "${lintable_sources[@]}"
echo "flake8 passed!"

black --check "${lintable_sources[@]}"
echo "black passed!"
