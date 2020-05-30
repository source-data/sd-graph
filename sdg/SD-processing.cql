/////PROCESSING THE GRAPH//////

//indices and constraints
CREATE INDEX ON :SDTag(text);
CREATE INDEX ON :SDTag(ext_ids);
CREATE INDEX ON :SDTag(type);
CREATE INDEX ON :SDTag(role);
CREATE INDEX ON :SDTag(ext_names);
CREATE INDEX ON :SDTag(norm_text);
CREATE INDEX ON :CondTag(ext_ids);
CREATE INDEX ON :CondTag(text);
CREATE INDEX ON :CondTag(ext_tax_names);
CREATE INDEX ON :H_Entity(ext_ids);
CREATE INDEX ON :H_Entity(type);
CREATE INDEX ON :CondTag(category);
CREATE INDEX ON :CondTag(name);
CREATE CONSTRAINT ON (h:H_Entity) ASSERT h.combo_id IS UNIQUE;
//CREATE CONSTRAINT ON (h:H_Entity) ASSERT (h.ext_id, h.type, h.category, h.name) IS NODE KEY; //only neo4j Enterprise!
CREATE CONSTRAINT ON (te:Term) ASSERT te.text IS UNIQUE;

//journal name to lower case
MATCH (a:SDArticle)
SET a.journalName = toLower(a.journalName)

//trim and tolower text
MATCH(t:SDTag)
WHERE t.text <> ""
SET t.norm_text = toLower(trim(t.text));

//replace NULL by "" for consistency 
MATCH(t:SDTag)
WHERE
    t.ext_names IS NULL
SET t.ext_names = ""
RETURN COUNT(t) AS `ext name NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.ext_ids IS NULL
SET t.ext_ids = ""
RETURN COUNT(t) AS `ext ids NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.ext_dbs IS NULL
SET t.ext_dbs = ""
RETURN COUNT(t) AS `ext_dbs NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.type IS NULL
SET t.type = ""
RETURN COUNT(t) AS `type NULL into ""`;

MATCH(t:SDTag)
WHERE
    t.role IS NULL
SET t.role = ""
RETURN COUNT(t) AS `role NULL into ""`;


//A: condense tags with same ext id and role
MATCH (p:SDPanel)-->(t:SDTag)
WHERE
    t.ext_ids <> ""
WITH DISTINCT p, t.role AS role, t.type as type, t.category as category, t.ext_ids AS ext_ids, COLLECT(DISTINCT (t.norm_text)) AS text, COUNT(DISTINCT t) AS N
ORDER BY N DESC
WITH DISTINCT p, role, type, category, ext_ids, text[0] AS most_used_text
CREATE (c:CondTag {role: role, type: type, category: category, ext_ids: ext_ids, text: most_used_text})
CREATE (p)-[rel:HasCondTag]->(c);

MATCH 
   (p:SDPanel)-[:has_tag]->(t:SDTag), (p)-[:HasCondTag]->(c:CondTag)
WHERE
    t.role = c.role AND t.ext_ids = c.ext_ids AND t.type = c.type
WITH DISTINCT t, c
CREATE (t)-[:Condensed_into]->(c)
RETURN COUNT(c)  AS `condensed tags`;


//B: condense tags that have no ext_ids but same text and same type and role
MATCH (p:SDPanel)-->(t:SDTag)
WHERE
    t.ext_ids = "" AND
    (t.category <> "" OR t.type <> "")
WITH DISTINCT p, t.norm_text AS text, t.role AS role, t.type AS type, t.category AS category
CREATE (c:CondTag {role: role, type:type, category: category, ext_ids: "", text: text})
CREATE (p)-[:HasCondTag]->(c);

MATCH 
    (p:SDPanel)-[:has_tag]->(t:SDTag), (p)-[:HasCondTag]->(c:CondTag)
WHERE
    c.ext_ids = "" AND t.ext_ids = "" AND
    t.role = c.role AND t.type = c.type AND t.category = c.category AND t.norm_text = c.text
WITH DISTINCT t, c
CREATE (t)-[:Condensed_into]->(c)
RETURN COUNT(c) AS `condensed tags`;


// Confirm that no SDTag is linked to multiple CondTag
MATCH (t:SDTag)-[r:Condensed_into]->(ct:CondTag)
WITH t, COUNT(DISTINCT ct) AS N
WHERE N > 1
RETURN COUNT(t) AS `SDTag associated with multiple CondTag`;


// Confirm that all CondTag have a non-empty text property
MATCH (ct:CondTag)
WHERE ct.text = "" OR ct.text IS NULL
RETURN COUNT(ct) AS `CondTag with no text`;


//A: Create hybrid entities from CondTag with ext_id
MATCH (ct:CondTag)
WHERE ct.ext_ids <> ""
WITH DISTINCT split(ct.ext_ids,'///') as ids, ct.type AS type, ct.text AS text, ct.category AS category, ct
UNWIND ids AS id
MERGE (hyb:H_Entity {combo_id: category + ":" + type + ":" + id})
ON CREATE SET hyb.ext_ids = id, hyb.type = type, hyb.category = category, hyb.name = text
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities with ext_ids`;


//B: Create hybrid entities from CondTag without an ext_id
MATCH (ct:CondTag)
WHERE ct.ext_ids = ""
WITH ct.text AS text, ct.type AS type, ct.category AS category, ct
MERGE (hyb:H_Entity {combo_id: category + ":" + type + ":" + text})
ON CREATE SET hyb.ext_ids = "", hyb.type = type, hyb.category = category, hyb.name = text 
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities without ext_ids`;


//report H_Entity with no names
MATCH (h:H_Entity)
WHERE 
    h.name = ""
RETURN COUNT(h) AS `H_Entity remaining without a name`;


//Create unique terms
MATCH (t:SDTag)-->(c:CondTag)-->(hyb:H_Entity)
WITH DISTINCT t.norm_text AS text, hyb
MERGE (te:Term {text: text})
MERGE (hyb)-[r:Has_text]->(te)
RETURN COUNT(r) AS `unique terms`;


//infer tested hypotheses at condensed tag level
MATCH 
   (p:SDPanel)-->(intervention:CondTag {role: "intervention"}),
   (p:SDPanel)-->(assayed:CondTag {role: "assayed"})
MERGE (intervention)-[r:H]->(assayed)
RETURN COUNT(r) AS `hypotheses at cond tag level`;


//copy publication date from jats articles to SDArticles
MATCH (jats:Article), (a:SDArticle)
WHERE jats.doi = a.doi
WITH DISTINCT jats.doi AS doi, jats.publication_date AS pub_date, a
ORDER BY pub_date DESC // most recent first
WITH DISTINCT doi, COLLECT(pub_date)[0] AS most_recent, a
SET a.pub_date = most_recent
RETURN COUNT(DISTINCT a);

//create hypotheses summaries at paper level

//MATCH 
//    (art:SDArticle)-->(f1:SDFigure)-->(p1:SDPanel)-->(i1:CondTag)-[h1:H]->(a1:CondTag)<--(p1),
//    (i1)-->(ih:H_Entity), (a1)-->(ah:H_Entity)
//RETURN art,ih,ah,COLLECT(f1),COLLECT(p1),COLLECT(i1),COLLECT(a1),COUNT(DISTINCT p1) AS N_p,COUNT(DISTINCT f1) AS N_f ORDER BY N_p DESC LIMIT 1
//WITH art,ih,ah, COUNT(DISTINCT(p1)) AS N_p, COUNT(DISTINCT(f1)) AS N_f
//    MERGE (ih)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah)
//    MERGE (art)-[:HasH {n_panels:N_p,n_figures:N_f}]->(h)
//RETURN COUNT(DISTINCT h) AS `hypotheses at paper level`;

//ad weight to hypotheses

//MATCH 
//   (art:SDArticle)-[rel:HasH]->(h:Hypothesis)
//WITH h, COUNT(DISTINCT art) AS N
//SET h.N = N;
//RETURN "added weight to hypotheses";

//link entities with hypothesis links

//MATCH
//   (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity)
//MERGE (ih)-[tested:Tested]->(ah)
//RETURN COUNT(tested) AS `hypotheses at entity level`;

//transfer hypothesis weight to :Tested links

//MATCH (i:H_Entity)-->(h:Hypothesis)-->(a:H_Entity), (i)-[r:Tested]->(a)
//SET r.N = h.N;
//RETURN "transferred hypothesis weight to :Tested links";

//add scale to entities

//MATCH (e:H_Entity {type:"molecule"}) SET e.scale = 1;
//MATCH (e:H_Entity {type:"gene"}) SET e.scale = 2;
//MATCH (e:H_Entity {type:"protein"}) SET e.scale = 2;
//MATCH (e:H_Entity {type:"subcellular"}) SET e.scale = 3;
//MATCH (e:H_Entity {type:"cell"}) SET e.scale = 4;
//MATCH (e:H_Entity {type:"tissue"}) SET e.scale = 5;
//MATCH (e:H_Entity {type:"organism"}) SET e.scale = 6;
//RETURN "added scales to entities";

// resolver nodes to map resource to base url and possibly to id regex pattern (according to identifiers.org)
// need to provide a recipe to transform in to compact identifier and just use identifiers.org
MERGE(:Resolver {name: "NCBI gene", url: "http://www.ncbi.nlm.nih.gov/gene/"}); // 59272
MERGE(:Resolver {name: "NCBI taxon", url: "http://www.ncbi.nlm.nih.gov/taxonomy/"}); // 10090
MERGE(:Resolver {name: "OBI", url: "https://bioportal.bioontology.org/ontologies/OBI/?p=classes&conceptid=http://purl.obolibrary.org/obo/", about: "http://purl.obolibrary.org/obo/"}); // OBI_0000445
MERGE(:Resolver {name: "Uberon", url: "http://purl.bioontology.org/ontology/UBERON/"}); // UBERON:0000955
MERGE(:Resolver {name: "CVCL", url: "https://identifiers.org/cellosaurus:"}); // CVCL_0574
MERGE(:Resolver {name: "BAO", url: "http://bioportal.bioontology.org/ontologies/BAO/bao:", about: "http://www.bioassayontology.org/bao#"}); // BAO_0000134
MERGE(:Resolver {name: "Gene Ontology", url: "http://purl.bioontology.org/ontology/GO/"}); // GO:0071735
MERGE(:Resolver {name: "CL", url: "http://purl.bioontology.org/ontology/CL/"}); // CL:0000583
MERGE(:Resolver {name: "Uniprot", url: "https://www.uniprot.org/uniprot/"}); // P0DTC2
MERGE(:Resolver {name: "ChEBI", url: "http://www.ebi.ac.uk/chebi/searchId.do?chebiId="}); // CHEBI:29687
MERGE(:Resolver {name: "Disease ontology", url: "http://purl.bioontology.org/ontology/DOID/"}); // DOID:2801


//Link H_Entity to ontologies

//Full text indexing
CALL db.index.fulltext.createNodeIndex("entity_name",["H_Entity"],["name"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("synonym",["Term"],["text"], {analyzer: "english"});
