#!/bin/zsh

set -o errexit
set -o pipefail
set -o nounset

# check if we're on an arm64 machine (specifically an M1/M2/etc Macbook), and use the corresponding file in that case
arch_flag=""
architecture=`uname -m`
if [[ "$architecture" == "arm64" ]]; then
    echo "Running on an arm64 machine, using docker-compose.arm64.yml"
    arch_flag="--file=docker-compose.arm64.yml"
fi
alias eeb="docker-compose --file=docker-compose.deploy.yml ${arch_flag} --file=docker-compose.tests.yml"

docker-compose --version

env_file=.env.ci
echo "Setting up environment variables from $env_file"
set -o allexport
source "$env_file"
set +o allexport

echo "Starting docker-compose service"
eeb up -d

echo "Waiting for Neo4j to be ready"
eeb exec --no-TTY neo4j bash -c "until echo 'MATCH(n) RETURN COUNT(n);' | cypher-shell -a $NEO_URI -u $NEO_USERNAME -p $NEO_PASSWORD; do echo 'waiting...'; sleep 1; done"

echo "Installing test dependencies"
eeb exec --no-TTY flask pip install pytest

echo "Running tests"
eeb exec --no-TTY flask python -m unittest
