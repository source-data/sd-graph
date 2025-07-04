#!/bin/zsh

set -o errexit
set -o pipefail
set -o nounset

# duplicate stdout and stderr to other file descriptors so we can output the test results later.
exec 3>&1
exec 4>&2

# parse the first argument. If it's -v or -vv we're running in verbose/very verbose mode.
if [[ $# -gt 0 ]]; then
    case $1 in
        -vv)  # very verbose: output everything, don't redirect stdout/stderr
            shift
            ;;
        -v)  # verbose: output errors, redirect stdout
            exec 1>/dev/null
            shift
            ;;
        *)  # default: output nothing except test results, redirect stdout/stderr
            exec 1>/dev/null
            exec 2>/dev/null
            ;;
    esac
else
    exec 1>/dev/null
    exec 2>/dev/null
fi

alias eeb="docker compose --file=docker-compose.deploy.yml --file=docker-compose.tests.yml"

# output the docker compose version for debugging
docker compose --version

env_file=.env.ci
echo "Setting up environment variables from $env_file"
set -o allexport
source "$env_file"
set +o allexport

echo "Building docker compose service"
docker compose --file=docker-compose.ci.yml build flask_deploy

echo "Starting docker compose service"
eeb up -d flask

echo "Running tests"
eeb exec --no-TTY flask python -m unittest $@ 1>&3 2>&4  # redirect stdout/stderr to file descriptors 3 and 4, defined above. We always want to display test results, even when running in quiet mode.
