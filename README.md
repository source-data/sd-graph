

Set up .env from .env.example with appropriate credentials.

Build the SD graph:

    python -m sdg.neo2xml <collection_name>
    cat sdg/SD-constraints.cql | cypher-shell -a bolt://localhost:7687 -u <neo4j_username> -p <neo4j_password>
    cat sdg/SD-processing.cql | cypher-shell -a bolt://localhost:7687 -u <neo4j_username> -p <neo4j_password>


Download meca archives from bioRxiv S3:

    aws s3 cp --request-payer requester --recursive --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/March_2020 data/meca

Import JATS XML documents from meca archives:

    python -m neojats.xml2neo data/meca

Launch server for REST API:

    export FLASK_APP='neoflask.neoflask'; export FLASK_DEBUG=true; python -m flask run
