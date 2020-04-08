python -m sdneo Sars-CoV-2
cat SD-constraints.cql | cypher-shell -a bolt://localhost:7687 -u neo4j -p sourcedata
cat SD-processing.cql | cypher-shell -a bolt://localhost:7687 -u neo4j -p sourcedata
