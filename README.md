

Set up .env from .env.example with appropriate credentials.

Optional: download meca archives from bioRxiv S3:

    aws s3 cp --request-payer requester --recursive --exclude "*" --include "*.meca" s3://biorxiv-src-monthly/Current_Content/March_2020 data/meca

or select meca archives to be processed and place into data/meca

Build the SD graph:

    python -m sdg.sdneo <collection_name>
    cat sdg/SD-processing.cql | cypher-shell -a bolt://localhost:7687 -u <neo4j_username> -p <neo4j_password>

Import JATS XML documents from meca archives:

    python -m neojats.xml2neo path/to/meca

Launch server for REST API:

    export FLASK_APP='neoflask.neoflask'; export FLASK_DEBUG=true; python -m flask run
