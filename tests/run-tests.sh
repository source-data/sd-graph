#!/bin/zsh

set -o errexit
set -o pipefail
set -o nounset

set -o allexport
source .env.ci
set +o allexport

eeb() {
    # check if we're on an arm64 machine (specifically an M1/M2/etc Macbook), and use the corresponding file in that case
    local arch_flag=""
    local architecture=`uname -m`
    if [[ "$architecture" == "arm64" ]]; then
        local arch_flag="--file=docker-compose.arm64.yml"
    fi
    docker-compose --file=docker-compose.deploy.yml ${arch_flag} --file=docker-compose.tests.yml $@
}

eeb up -d
# wait for neo4j to be ready
eeb exec neo4j bash -c "until echo 'MATCH(n) RETURN COUNT(n);' | cypher-shell -a $NEO_URI -u $NEO_USERNAME -p $NEO_PASSWORD; do echo 'waiting...'; sleep 1; done"
eeb exec flask pip install pytest
eeb exec flask python -m unittest
