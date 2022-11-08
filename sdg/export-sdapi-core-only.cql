// from https://neo4j.com/developer/kb/export-sub-graph-to-cypher-and-import/
// doc https://neo4j.com/labs/apoc/4.1/export/cypher/
// exports the whole database incl. indexes as cypher statements to the provided file
// CALL apoc.export.cypher.all('/tmp/export.cypher',{format:'cypher-shell'})
// NOTE: need NEO4J_apoc_export_file_enabled=true in .env
// NOTE: need to map ./data/neo4j-import:/import for neo4j service

// exports given nodes and relationships incl. indexes as cypher statements to the provided file
MATCH
  (sd:SDCollection {name: "PUBLICSEARCH"})-[r1]->(a:SDArticle {source: "sdapi"})-[r2]->(f:SDFigure)-[r3]->(p:SDPanel)-[r4]->(t:SDTag)-[r5]->(ct:CondTag)-[r6]->(h:H_Entity)-[r7]->(te:Term)
WITH
  sd, a, f, p, t, ct, h, te,
  r1, r2, r3, r4, r5, r6, r7
LIMIT 100
WITH collect(DISTINCT sd)+collect(DISTINCT p)+collect(DISTINCT f)+collect(DISTINCT p)+collect(DISTINCT t)+collect(DISTINCT ct)+collect(DISTINCT h)+collect(DISTINCT te) as export_nodes,
collect(DISTINCT r1)+collect(DISTINCT r2)+collect(DISTINCT r3)+collect(DISTINCT r4)+collect(DISTINCT r5)+collect(DISTINCT r6)+collect(DISTINCT r7) as export_rels
CALL apoc.export.cypher.data(export_nodes, export_rels, 'export.cypher', {format:'cypher-shell'})
YIELD file, source, format, nodes, relationships, properties, time
RETURN nodes, relationships, time;

// exports given graph object incl. indexes as cypher statements to the provided file
// MATCH
//   path = (sd:SDCollection {name: "PUBLICSEARCH"})-[r1]->(a:SDArticle {source: "sdapi"})-[r2]->(f:SDFigure)-[r3]->(p:SDPanel)-[r4]->(t:SDTag)-[r5]->(ct:CondTag)-[r6]->(h:H_Entity)-[r7]->(te:Term)
// WITH
//   COLLECT(path) AS paths
// CALL apoc.graph.fromPaths(paths,'export_graph',{}) YIELD graph
// CALL apoc.export.cypher.graph(graph,'export.cypher',{format:'cypher-shell'}) YIELD time
// RETURN time;

// exports nodes and relationships from the cypher statement incl. indexes as cypher statements to the provided file
// CALL apoc.export.cypher.query(
// 'MATCH (p1:Person)-[r:KNOWS]->(p2:Person) RETURN *',
// '/tmp/export.cypher',{format:'cypher-shell'}); 