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


# check if we're on an arm64 machine (specifically an M1/M2/etc Macbook), and use the corresponding file in that case
arch_flag=""
architecture=`uname -m`
if [[ "$architecture" == "arm64" ]]; then
    echo "Running on an arm64 machine, using docker-compose.arm64.yml"
    arch_flag="--file=docker-compose.arm64.yml"
fi
alias eeb="docker-compose --file=docker-compose.deploy.yml ${arch_flag} --file=docker-compose.tests.yml"

# output the docker-compose version for debugging
docker-compose --version

env_file=.env.ci
echo "Setting up environment variables from $env_file"
set -o allexport
source "$env_file"
set +o allexport

echo "Starting docker-compose service"
eeb up -d flask

# waits until neo4j is ready by trying to execute a cypher query using the cypher-shell interface
wait_for_neo4j=$(
cat <<'END_HEREDOC'
t=0
until echo "MATCH(n) RETURN COUNT(n);" | cypher-shell -a $NEO_URI -u $NEO_USERNAME -p $NEO_PASSWORD;
do
    if [[ $t -gt 60 ]]; then
        echo "Neo4j not ready after 60 seconds, aborting"
        exit 1
    fi
    t=$((t+1))
    echo -ne "\r"
    echo -ne "Waiting for Neo4j to be ready... ($t s)"
    sleep 1
done

echo -ne "\r"
if [[ $t -gt 0 ]]; then
    echo "Neo4j ready after $t seconds"
else
    echo "Neo4j already up"
fi
END_HEREDOC
)
eeb exec --no-TTY neo4j bash -c "$wait_for_neo4j"

echo "Installing test dependencies"
eeb exec --no-TTY flask pip install pytest

echo "Running tests"
eeb exec --no-TTY flask python -m unittest $@ 1>&3 2>&4  # redirect stdout/stderr to file descriptors 3 and 4, defined above. We always want to display test results, even when running in quiet mode.
