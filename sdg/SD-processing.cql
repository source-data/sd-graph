/////PROCESSING THE GRAPH//////
//tag all nodes and relationships with attribute {original=True}
//if something goes wrong can delete stuff WHERE NOT n.origin

MATCH (n) 
SET n.original=True
RETURN COUNT(n) AS `tagged as original nodes`;

MATCH ()-[r]-() SET r.original=True
RETURN COUNT(DISTINCT r) AS `taggers as original relationships` ;

//tag indexes

CREATE INDEX ON :SDTag(text);
CREATE INDEX ON :SDTag(ext_ids);
CREATE INDEX ON :SDTag(type);
CREATE INDEX ON :SDTag(role);
RETURN "indexed tags";

//fill in ext names for tags that would miss it

MATCH (t1:SDTag)
WHERE 
    t1.ext_names = ""
WITH t1
MATCH (t2:SDTag {ext_ids: t1.ext_ids})
WHERE t2.ext_names <> ""
WITH DISTINCT t1, t2.ext_names as names
SET t1.ext_names = names
RETURN COUNT(t1) AS `tags with filled in names`;

//A: condense tags with same ext id and role

MATCH (p:SDPanel)-->(t:SDTag)
WHERE
    t.ext_ids <> ""
WITH DISTINCT p, t.role AS role, t.type as type, t.category as category, t.ext_ids AS ext_ids, t.ext_names as ext_names
    CREATE (c:CondTag {role: role, type: type, category: category, ext_ids: ext_ids, text: ext_names}) //check if p has cond tag with same ext id but different names
    MERGE (p)-[rel:HasCondTag]->(c)
WITH p,c
MATCH 
    (p)-->(t:SDTag)
WHERE
    t.role = c.role AND t.ext_ids = c.ext_ids AND t.type = c.type AND t.ext_names = c.text
MERGE (t)-[:Condensed_into]->(c)
RETURN COUNT(c)  AS `condensed tags`

UNION

//B: condense tags that have no ext_ids but same text and same type and role

MATCH (p:SDPanel)-->(t:SDTag {ext_ids: ""})
WHERE
    t.category <> "" OR t.type <> ""
WITH DISTINCT p, trim(lower(t.text)) AS text, t.role AS role, t.type AS type, t.category AS category
    CREATE (c:CondTag {role: role, type:type, category: category, ext_ids: "", text: text})
    MERGE (p)-[:HasCondTag]->(c)
WITH p,c
MATCH 
    (p)-->(t:SDTag)
WHERE
    t.role = c.role AND t.type = c.type AND t.category = c.category AND trim(lower(t.text)) = c.text AND 
    t.ext_ids = ""
MERGE (t)-[:Condensed_into]->(c)
RETURN COUNT(c) AS `condensed tags`;

//index condensed tags

CREATE INDEX ON :CondTag(ext_ids);
RETURN "indexed condensed tags";

//Create hybrid entities

MATCH (ct:CondTag)
WHERE ct.ext_ids <> ""
WITH split(ct.ext_ids,'///') as ids, ct.type AS type, ct.text AS text, ct.category AS category, ct
UNWIND ids AS id
MERGE (hyb:H_Entity {ext_ids: category + type + ":" + id, type: type, name: text})
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities`

UNION

MATCH (ct:CondTag)
WHERE ct.ext_ids = ""
WITH trim(lower(ct.text)) AS text, ct.type AS type, ct.category AS category, ct
MERGE (hyb:H_Entity {ext_ids: category + type + ":" + text, type: type, name: text}) 
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities`;

//Create unique terms

MATCH (t:SDTag)-->(c:CondTag)-->(hyb:H_Entity)
WITH DISTINCT trim(toLower(t.text)) AS text, hyb
MERGE (te:Term {text:text})
MERGE (hyb)-[r:Has_text]->(te)
RETURN COUNT(r) AS `unique terms`;

// Filling in missing names

MATCH (h:H_Entity)-->(t:Term)
WHERE h.name = ""
WITH h, COLLECT(DISTINCT t.text)[0] AS some_name
SET h.name = some_name
RETURN COUNT(h) AS `entities updated to fill in with a name`;

//infer tested hypotheses at condensed tag level

MATCH 
   (p:SDPanel)-->(intervention:CondTag {role: "intervention"}),
   (p:SDPanel)-->(assayed:CondTag {role: "assayed"})
MERGE (intervention)-[r:H]->(assayed)
RETURN COUNT(r) AS `hypotheses at tag level`;

//create hypotheses summaries at paper level

MATCH 
    (art:SDArticle)-->(f1:SDFigure)-->(p1:SDPanel)-->(i1:CondTag)-[h1:H]->(a1:CondTag)<--(p1),
    (i1)-->(ih:H_Entity), (a1)-->(ah:H_Entity)
//RETURN art,ih,ah,COLLECT(f1),COLLECT(p1),COLLECT(i1),COLLECT(a1),COUNT(DISTINCT p1) AS N_p,COUNT(DISTINCT f1) AS N_f ORDER BY N_p DESC LIMIT 1
WITH art,ih,ah, COUNT(DISTINCT(p1)) AS N_p, COUNT(DISTINCT(f1)) AS N_f
    MERGE (ih)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah)
    MERGE (art)-[:HasH {n_panels:N_p,n_figures:N_f}]->(h)
RETURN COUNT(DISTINCT h) AS `hypotheses at paper level`;

//ad weight to hypotheses

MATCH 
   (art:SDArticle)-[rel:HasH]->(h:Hypothesis)
WITH h, COUNT(DISTINCT art) AS N
SET h.N = N;
RETURN "added weight to hypotheses";

//link entities with hypothesis links

MATCH
   (ih:H_Entity)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah:H_Entity)
MERGE (ih)-[tested:Tested]->(ah)
RETURN COUNT(tested) AS `hypotheses at entity level`;

//transfer hypothesis weight to :Tested links

MATCH (i:H_Entity)-->(h:Hypothesis)-->(a:H_Entity), (i)-[r:Tested]->(a)
SET r.N = h.N;
RETURN "transferred hypothesis weight to :Tested links";

//add scale to entities

MATCH (e:H_Entity {type:"molecule"}) SET e.scale = 1;
MATCH (e:H_Entity {type:"gene"}) SET e.scale = 2;
MATCH (e:H_Entity {type:"protein"}) SET e.scale = 2;
MATCH (e:H_Entity {type:"subcellular"}) SET e.scale = 3;
MATCH (e:H_Entity {type:"cell"}) SET e.scale = 4;
MATCH (e:H_Entity {type:"tissue"}) SET e.scale = 5;
MATCH (e:H_Entity {type:"organism"}) SET e.scale = 6;
RETURN "added scales to entities";

//Full text indexing

CALL db.index.fulltext.createNodeIndex("titles_captions_names",["SDArticle", "SDPanel", "H_Entity"],["title", "formatted_caption", "name"]);