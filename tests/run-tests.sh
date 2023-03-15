#!/bin/zsh

set -o errexit
set -o pipefail
set -o nounset

set -o allexport
source .env.ci
set +o allexport

eeb() {
    docker-compose -f docker-compose.deploy.yml -f docker-compose.arm64.yml -f docker-compose.tests.yml $@
}

eeb up -d
# wait for neo4j to be ready
eeb exec neo4j bash -c "until echo 'MATCH(n) RETURN COUNT(n);' | cypher-shell -a $NEO_URI -u $NEO_USERNAME -p $NEO_PASSWORD; do echo 'waiting...'; sleep 1; done"
eeb exec flask pip install pytest
eeb exec flask python -m unittest
