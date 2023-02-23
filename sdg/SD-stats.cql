MATCH (n)
RETURN LABELS(n), COUNT(n);

MATCH ()-[r]->()
RETURN TYPE(r), COUNT(r);

//statistics by entity type
MATCH (t:SDTag)
WHERE t.type<>""
RETURN  DISTINCT t.type AS type, COUNT(t) AS tags, COUNT(DISTINCT(t.text)) AS terms, COUNT(DISTINCT(t.ext_id)) AS ids 
ORDER BY tags DESC;

//statistics by entitiy role
MATCH (t:SDTag)
WHERE t.role <> ""
RETURN  DISTINCT t.role AS role, COUNT(t) AS tags, COUNT(DISTINCT(t.text)) AS terms, COUNT(DISTINCT(t.ext_id)) AS ids 
ORDER BY tags DESC;

//statistics by role and type
MATCH (t:SDTag)
WHERE t.type <> "" and t.role <> ""
WITH DISTINCT t.type AS type, t.role AS role, COUNT(DISTINCT t) AS N
RETURN type,reduce(s="",r in collect(role+":"+toString(N)) | s+r+" | ") AS list;

//most frequent tags by type
MATCH (tag:SDTag {type:"molecule"}) RETURN DISTINCT toLower(tag.text) AS small_mol, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;
MATCH (tag:SDTag {type:"gene"}) RETURN DISTINCT toLower(tag.text) AS gene, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;
MATCH (tag:SDTag {type:"protein"}) RETURN DISTINCT toLower(tag.text) AS protein, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;
MATCH (tag:SDTag {type:"subcellular"}) RETURN DISTINCT toLower(tag.text) AS subcellular_struct, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;
MATCH (tag:SDTag {type:"cell"}) RETURN DISTINCT toLower(tag.text) AS cell_type, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;
MATCH (tag:SDTag {type:"tissue"}) RETURN DISTINCT toLower(tag.text) AS tissues, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;
MATCH (tag:SDTag {type:"organism"}) RETURN DISTINCT toLower(tag.text) AS organism, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;
MATCH (tag:SDTag {type:"undefined"}) RETURN DISTINCT toLower(tag.text) AS undefine, COUNT(tag) AS n ORDER BY n DESC LIMIT 100;

//p(role|type) = p(type|role) * p(role) / p(type)
MATCH (tags:SDTag)
WHERE tags.role <> "" AND tags.type <> ""
WITH COUNT(tags) AS N
WITH N, ["intervention", "assayed", "normalizing", "reporter", "experimental", "biological"] AS roles
UNWIND roles as role
MATCH (t_role:SDTag {role:role}) 
WITH role, N, COUNT(t_role) AS N_role,
["molecule", "gene", "protein", "subcellular", "cell", "tissue", "organism"] AS types
UNWIND types as type
MATCH (t_type:SDTag {type:type})
WITH role, type, N, N_role,  COUNT(t_type) AS N_type
MATCH (t_type_with_role:SDTag {role:role, type:type})
WITH role, type, N, N_role, N_type, COUNT(t_type_with_role) AS N_type_with_role
WITH 
role, type,
1.0*N_role/N AS `p(role)`,
1.0*N_type/N AS `p(type)`,
1.0*N_type_with_role/N_role AS `p(type | role)`
WITH
role, type, 
`p(role)` * `p(type | role)` / `p(type)` AS `p(role | type)`, `p(role)`,`p(type | role)`,`p(type)`
RETURN role, type, `p(role | type)`, `p(role)`,`p(type | role)`,`p(type)`;

//fraction of panels with at least one intervention assayed pair
MATCH (p:SDPanel)
WITH COUNT(p) AS N
MATCH (intervention:SDTag {role:"intervention"})<--(p:SDPanel)-->(assayed:SDTag {role:"assayed"})
WITH COUNT(DISTINCT p) AS n,N
RETURN N as `total number of panels`, n AS `panel with hypothesis test`, tostring(ROUND(100*n/N)+"%") AS `fraction`;

//fraction of tags included in the text of the caption
MATCH (in_caption:SDTag {in_caption:true})
WITH COUNT(DISTINCT in_caption) AS c
MATCH (floating:SDTag {in_caption:false}) 
WITH c, COUNT(DISTINCT floating) AS f
RETURN c AS `in caption`, f AS `not in caption`, toString(ROUND(100*tofloat(c)/(c+f)))+"%" AS `%`;
