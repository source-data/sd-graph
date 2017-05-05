//Load gene-protein Map

//METHOD 1
//Extract all protein ids with 
//MATCH (t:Tag)
//WHERE t.type = "protein" AND t.ext_id <> ""
//WITH split(t.ext_id,"///") AS ids
//UNWIND ids as id
//RETURN DISTINCT id
//save to export.csv
//upload expert.csv at http://www.uniprot.org/uploadlists/ to generate a "UniProtKB AC/ID" to "GeneID (Entrez Gene)" mapping protein2gene.tab file
//run this in neo4j-shell or browser

//
//UPDATE FILE PATH!!!
//

LOAD CSV WITH HEADERS FROM "file:///protein2gene.tab" AS csvLine FIELDTERMINATOR "\t"
CREATE (m:Map {uniprot: csvLine.From, gene: csvLine.To})
RETURN COUNT(m) AS `mapped uniprot to gene ids`;

//or

//METHOD 2
//download the file from
//ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/idmapping_selected.tab.gz
//gunzip idmapping_selected.tab.gz
//adjust Java heap in neo4j-wrapper.conf
//neo4j/conf/wrapper.java.initmemory=5096
//neo4j/conf/wrapper.java.maxmemory=5096
//LOAD CSV FROM "file:///Users/lemberger/Documents/code/sd/sd_graph/excerpt_idmapping_selected.tab" AS csvLine FIELDTERMINATOR "\t"
//CREATE (m:Map {uniprot: csvLine[0], gene: csvLine[2]})
//RETURN COUNT(m) AS `mapped uniprot to gene ids`;

//Create gene2protein mapping relationships
MATCH (gene:H_Entity {type:"gene"}), (m:Map)
WHERE SPLIT(gene.ext_id,":")[1] = m.gene
WITH gene, m.uniprot AS uniprot
MATCH (protein:H_Entity {type:"protein", ext_id:"protein:"+uniprot})
MERGE (gene)-[r:gene2protein]->(protein)
RETURN COUNT(r) AS `gene2proteins links`;
