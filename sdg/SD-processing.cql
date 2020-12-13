/////PROCESSING THE GRAPH//////


CREATE CONSTRAINT h_entity_id IF NOT EXISTS ON (h:H_Entity) ASSERT h.combo_id IS UNIQUE;
//CREATE CONSTRAINT ON (h:H_Entity) ASSERT (h.ext_id, h.type, h.category, h.name) IS NODE KEY; //only neo4j Enterprise!
CREATE CONSTRAINT term_text_ IF NOT EXISTS ON (te:Term) ASSERT te.text IS UNIQUE;

// purge processed nodes
// prelimin solution before proper combined keys are implemented that will allow using MERGE instead of CREATE cond Tags
:begin
MATCH (ct:CondTag)-[r]-()
DETACH DELETE ct
RETURN COUNT(DISTINCT ct) AS `deleted CondTag`;
:commit
:begin
MATCH (ct:CondTag)
RETURN COUNT(ct) AS `remaining CondTag`;
:commit
:begin
MATCH (h:H_Entity)-[r]-()
DETACH DELETE h
RETURN COUNT(DISTINCT h) AS `deleted H_Entity`;
:commit
:begin
MATCH (h:H_Entity)
RETURN COUNT(h) AS `remaining H_Entity`;
:commit
:begin
MATCH (t:Term)
DETACH DELETE t
RETURN COUNT(DISTINCT t) AS `deleted Term`;
:commit
:begin
MATCH (t:Term)
RETURN COUNT(t) AS `remaining Term`;
:commit
:begin
//journal name to lower case
MATCH (a:SDArticle)
SET a.journalName = toLower(a.journalName);
:commit
:begin
//trim and tolower text
MATCH(t:SDTag)
SET t.norm_text = toLower(trim(t.text));
:commit
:begin
//add text if none there
MATCH(t:SDTag)
WHERE t.text = ""
SET t.text = toLower(t.ext_names)
RETURN COUNT(t) AS `added ext_names instead of emtpy text tag`;
:commit
:begin
//remove sick tags with no name and no ext_names
MATCH(t:SDTag)-[r]-()
WHERE t.text = "" AND t.ext_names = ""
DELETE r, t
RETURN COUNT(t) AS `deleted empty tags`;
:commit
:begin
//replace NULL by "" for consistency 
MATCH(t:SDTag)
WHERE
    t.ext_names IS NULL
SET t.ext_names = ""
RETURN COUNT(t) AS `ext name NULL into ""`;
:commit
:begin
MATCH(t:SDTag)
WHERE
    t.ext_ids IS NULL
SET t.ext_ids = ""
RETURN COUNT(t) AS `ext ids NULL into ""`;
:commit
:begin
MATCH(t:SDTag)
WHERE
    t.ext_dbs IS NULL
SET t.ext_dbs = ""
RETURN COUNT(t) AS `ext_dbs NULL into ""`;
:commit
:begin
MATCH(t:SDTag)
WHERE
    t.type IS NULL
SET t.type = ""
RETURN COUNT(t) AS `type NULL into ""`;
:commit
:begin
MATCH(t:SDTag)
WHERE
    t.role IS NULL
SET t.role = ""
RETURN COUNT(t) AS `role NULL into ""`;
:commit
:begin
MATCH(f:Fig)
WHERE NOT EXISTS(f.position_idx)
SET  f.position_idx = ""
RETURN COUNT(f) AS `NULL fig position_idx set to ""`;
:commit
:begin
MATCH(p:SDPanel)
WHERE p.panel_id IS NULL
SET p.panel_id = ""
RETURN COUNT(p) AS `NULL panel_id set to ""`;
:commit
:begin
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
:commit
:begin
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
:commit
:begin
// Confirm that no SDTag is linked to multiple CondTag
MATCH (t:SDTag)-[r:Condensed_into]->(ct:CondTag)
WITH t, COUNT(DISTINCT ct) AS N
WHERE N > 1
RETURN COUNT(t) AS `SDTag associated with multiple CondTag`;
:commit
:begin
// Confirm that all CondTag have a non-empty text property
MATCH (ct:CondTag)
WHERE ct.text = "" OR ct.text IS NULL
RETURN COUNT(ct) AS `CondTag with no text`;
:commit
:begin
//A: Create hybrid entities from CondTag with ext_id
MATCH (ct:CondTag)
WHERE ct.ext_ids <> ""
WITH DISTINCT split(ct.ext_ids,'///') as ids, ct.type AS type, ct.text AS text, ct.category AS category, ct
UNWIND ids AS id
MERGE (hyb:H_Entity {combo_id: category + ":" + type + ":" + id})
ON CREATE SET hyb.ext_ids = id, hyb.type = type, hyb.category = category, hyb.name = text
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities with ext_ids`;
:commit
:begin
//B: Create hybrid entities from CondTag without an ext_id
MATCH (ct:CondTag)
WHERE ct.ext_ids = ""
WITH ct.text AS text, ct.type AS type, ct.category AS category, ct
MERGE (hyb:H_Entity {combo_id: category + ":" + type + ":" + text})
ON CREATE SET hyb.ext_ids = "", hyb.type = type, hyb.category = category, hyb.name = text 
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities without ext_ids`;
:commit
:begin
//report H_Entity with no names
MATCH (h:H_Entity)
WHERE 
    h.name = ""
RETURN COUNT(h) AS `H_Entity remaining without a name`;
:commit
:begin
//Create unique terms
MATCH (t:SDTag)-->(c:CondTag)-->(hyb:H_Entity)
WITH DISTINCT t.norm_text AS text, hyb
MERGE (te:Term {text: text})
MERGE (hyb)-[r:Has_text]->(te)
RETURN COUNT(r) AS `unique terms`;
:commit
:begin
// Compute popularity of terms
MATCH (sd:SDArticle)-->(f:SDFigure)-->(p:SDPanel)-->(ct:CondTag)-->(h:H_Entity)-->(t:Term)
WITH t, COUNT(DISTINCT p) AS freq
SET t.freq_in_panel = freq
RETURN COUNT (t) as `tags with popularity frequency added`;
:commit
:begin
//infer tested hypotheses at condensed tag level
MATCH 
  (p:SDPanel)-->(intervention:CondTag {role: "intervention"}),
  (p:SDPanel)-->(assayed:CondTag {role: "assayed"})
MERGE (intervention)-[r:H]->(assayed)
RETURN COUNT(r) AS `hypotheses at cond tag level`;
:commit
:begin
//add scale to entities
MATCH (e:H_Entity {type:"molecule"}) SET e.scale = 1;
MATCH (e:H_Entity {type:"gene"}) SET e.scale = 2;
MATCH (e:H_Entity {type:"protein"}) SET e.scale = 2;
MATCH (e:H_Entity {type:"geneprod"}) SET e.scale = 2;
MATCH (e:H_Entity {type:"subcellular"}) SET e.scale = 3;
MATCH (e:H_Entity {type:"cell"}) SET e.scale = 4;
MATCH (e:H_Entity {type:"tissue"}) SET e.scale = 5;
MATCH (e:H_Entity {type:"organism"}) SET e.scale = 6;
RETURN "added scales to entities";
:commit
:begin
//copy publication date and abstract from jats articles to SDArticles
MATCH (jats:Article), (a:SDArticle)
WHERE jats.doi = a.doi
WITH DISTINCT 
  jats.doi AS doi, 
  jats.publication_date AS pub_date, 
  jats.abstract AS abstract, 
  a
ORDER BY pub_date DESC // most recent first
WITH DISTINCT doi, COLLECT(pub_date)[0] AS most_recent, COLLECT(abstract)[0] AS abstr, a
SET a += {pub_date: most_recent, abstract: abstr}
RETURN COUNT(DISTINCT a) AS `SDArticles with pub date`;
:commit
:begin
//Link to authors via Contrib nodes
MATCH (jats:Article), (sd:SDArticle)
WHERE jats.doi = sd.doi
WITH DISTINCT
  sd.doi AS doi,
  sd,
  jats
ORDER BY jats.publication_date DESC
WITH DISTINCT
  doi,
  sd,
  COLLECT(jats)[0] AS most_recent
MATCH
  (most_recent)-[:has_author]->(au:Contrib)
WITH DISTINCT
  doi,
  sd,
  au
MERGE (sd)-[r:has_author]->(au)
RETURN COUNT(DISTINCT r) AS `SDArticle author relationships`;
:commit