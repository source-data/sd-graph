//tag all nodes and relationships with attribute {original=True}
//if something goes wrong can delete stuff WHERE NOT n.origin
MATCH (n) SET n.original=True
RETURN COUNT(n) AS `tagged as original nodes`;

MATCH ()-[r]-() SET r.original=True
RETURN COUNT(DISTINCT r) AS `taggers as original relationships` ;

//tag indexes
CREATE INDEX ON :Tag(text);
CREATE INDEX ON :Tag(ext_id);
CREATE INDEX ON :Tag(Type);
CREATE INDEX ON :Tag(Role);
RETURN "indexed tags";

//A: condense tags with same ext id and role
MATCH (p:Panel)-->(t:Tag {category:""})
WHERE
    t.ext_id <> "" AND t.role <> ""
WITH DISTINCT p, t.role AS role, t.type as type, t.ext_id AS ext_id
    CREATE (c:CondTag {role:role, type:type, ext_id:ext_id})
    MERGE (p)-[rel:HasCondTag]->(c)
WITH p,c
MATCH 
    (p)-->(t:Tag)
WHERE
    t.role = c.role AND t.ext_id = c.ext_id AND t.type = c.type
MERGE (t)-[:Condensed_into]->(c)
RETURN COUNT(c)  AS `condensed tags`

UNION

//B: condense tags that have no ext_id but same text and same type and role
MATCH (p:Panel)-->(t:Tag)
WHERE
     t.role <> "" AND t.type <> "" AND t.ext_id = ""
WITH DISTINCT p, trim(lower(t.text)) AS text, t.role AS role, t.type AS type
    CREATE (c:CondTag {role:role, type:type, ext_id:"", text:text})
    MERGE (p)-[:HasCondTag]->(c)
WITH p,c
MATCH 
    (p)-->(t:Tag)
WHERE
     t.role = c.role AND t.type = c.type AND lower(t.text) = c.text AND 
     t.ext_id="" AND c.ext_id=""
MERGE (t)-[:Condensed_into]->(c)
RETURN COUNT(c) AS `condensed tags`;

//index condensed tags
CREATE INDEX ON :CondTag(ext_id);
RETURN "indexed condensed tags";

//Create hybrid entities
MATCH (ct:CondTag)
WHERE ct.ext_id <>""
WITH split(ct.ext_id,'///') as ids, ct.type AS type, ct
UNWIND ids AS id
//it should be ext_db instead of type
MERGE (hyb:H_Entity {ext_id: type + ":"+ id, type: type})
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities`

UNION

MATCH (ct:CondTag)
WHERE ct.text <>""
WITH trim(lower(ct.text)) AS text, ct.type AS type, ct
MERGE (hyb:H_Entity {ext_id:type + ":" + text, type: type}) 
MERGE (ct)-[:Identified_by]->(hyb)
RETURN COUNT(hyb) AS `unique hybrid entities`;

//Create unique terms
MATCH (t:Tag)-->(c:CondTag)-->(hyb:H_Entity)
WITH DISTINCT trim(lower(t.text)) AS text, hyb
MERGE (te:Term {text:text})
MERGE (hyb)-[r:Has_text]->(te)
RETURN COUNT(r) AS `unique terms`;

//infer tested hypotheses at condensed tag level
MATCH 
   (p:Panel)-->(intervention:CondTag {role:"intervention"}),
   (p:Panel)-->(assayed:CondTag {role:"assayed"})
MERGE (intervention)-[r:H]->(assayed)
RETURN COUNT(r) AS `hypotheses at tag level`;

//create hypotheses summaries at paper level
MATCH 
    (art:Article)-->(f1:Figure)-->(p1:Panel)-->(i1:CondTag)-[h1:H]->(a1:CondTag)<--(p1),
    (i1)-->(ih:H_Entity), (a1)-->(ah:H_Entity)
//RETURN art,ih,ah,COLLECT(f1),COLLECT(p1),COLLECT(i1),COLLECT(a1),COUNT(DISTINCT p1) AS N_p,COUNT(DISTINCT f1) AS N_f ORDER BY N_p DESC LIMIT 1
WITH art,ih,ah, COUNT(DISTINCT(p1)) AS N_p, COUNT(DISTINCT(f1)) AS N_f
    MERGE (ih)-[:Is_Intervention_of]->(h:Hypothesis)-[:Has_Assayed]->(ah)
    MERGE (art)-[:HasH {n_panels:N_p,n_figures:N_f}]->(h)
RETURN COUNT(DISTINCT h) AS `hypotheses at paper level`;

//ad weight to hypotheses
MATCH 
   (art:Article)-[rel:HasH]->(h:Hypothesis)
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

