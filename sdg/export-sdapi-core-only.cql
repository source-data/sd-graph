// from https://neo4j.com/developer/kb/export-sub-graph-to-cypher-and-import/
// doc https://neo4j.com/labs/apoc/4.1/export/cypher/
// exports the whole database incl. indexes as cypher statements to the provided file
// NOTE: need NEO4J_apoc_export_file_enabled=true in .env
// NOTE: need to map ./data/neo4j-import:/import for neo4j service

CALL apoc.export.cypher.query(
    'MATCH (sd:SDCollection {name: "PUBLICSEARCH"})-[r1]->(a:SDArticle {source: "sdapi"})-[r2]->(f:SDFigure)-[r3]->(p:SDPanel)-[r4]->(t:SDTag)-[r5]->(ct:CondTag)-[r6]->(h:H_Entity)-[r7]->(te:Term) RETURN *',
    'export.cypher',
    {format:'cypher-shell'}
)