//////////////DEMO////////////

//demo data model
MATCH (a:SDArticle)
WITH a
MATCH (a:SDArticle)-[fr]->(f:SDFigure)
WITH
    a,f,
    fr
MATCH (f:SDFigure)-[pr]->(p:SDPanel)
WITH
    a,f,p,
    fr,pr
MATCH 
    (p)-[tr1]->(t1:SDTag),(p)-[tr2]->(t2:SDTag),
    (p)-[tr3]->(t3:SDTag)
WITH 
    a,f,p,t1,t2,t3,
    fr,pr,tr1,tr2,tr3 
MATCH 
    (t1)-[ctr1]->(ct1:CondTag),
    (t2)-[ctr2]->(ct1:CondTag),
    (t3)-[ctr3]->(ct2:CondTag)
WHERE ct1.role="assayed" AND ct2.role="intervention" AND ct2.type = "gene"
WITH 
    a,f,p,t1,t2,t3,ct1,ct2,
    fr,pr,tr1,tr2,tr3,ctr1,ctr2,ctr3
MATCH 
    (ct1)-[er1:Identified_by]->(e1:H_Entity),
    (ct2)-[er2:Identified_by]->(e2:H_Entity)
WHERE ct1.ext_id <>"" AND ct2.ext_id=""
WITH 
    a,f,p,t1,t2,t3,ct1,ct2,e1,e2,
    fr,pr,tr1,tr2,tr3,ctr1,ctr2,ctr3,er1,er2 LIMIT 1
MATCH
   (e1)-[ert1:Has_text]->(te1:Term),
   (e2)-[ert2:Has_text]->(te2:Term)
RETURN
    a,f,p,t1,t2,t3,ct1,ct2,e1,e2,te1,te2,
    fr,pr,tr1,tr2,tr3,ctr1,ctr2,ctr3,er1,er2,ert1,ert2;
//Tested

//////////GLOBAL STATS/////////////////

//global database statistics
MATCH (n)
RETURN labels(n), COUNT(n)

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
RETURN type,reduce(s="",r in collect(role+":"+toString(N)) | s+r+" | ") AS list

//most frequent tags by type
MATCH (tag:SDTag {type:"molecule"}) RETURN DISTINCT lower(tag.text) AS small_mol, COUNT(tag) AS n ORDER BY n DESC;
MATCH (tag:SDTag {type:"gene"}) RETURN DISTINCT lower(tag.text) AS gene, COUNT(tag) AS n ORDER BY n DESC;
MATCH (tag:SDTag {type:"protein"}) RETURN DISTINCT lower(tag.text) AS protein, COUNT(tag) AS n ORDER BY n DESC;
MATCH (tag:SDTag {type:"subcellular"}) RETURN DISTINCT lower(tag.text) AS subcellular_struct, COUNT(tag) AS n ORDER BY n DESC;
MATCH (tag:SDTag {type:"cell"}) RETURN DISTINCT lower(tag.text) AS cell_type, COUNT(tag) AS n ORDER BY n DESC;
MATCH (tag:SDTag {type:"tissue"}) RETURN DISTINCT lower(tag.text) AS tissues, COUNT(tag) AS n ORDER BY n DESC;
MATCH (tag:SDTag {type:"organism"}) RETURN DISTINCT lower(tag.text) AS organism, COUNT(tag) AS n ORDER BY n DESC;
MATCH (tag:SDTag {type:"undefined"}) RETURN DISTINCT lower(tag.text) AS undefine, COUNT(tag) AS n ORDER BY n DESC;

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
RETURN N as `total number of panels`, n AS `panel with hypothesis test`, tostring(ROUND(100*n/N)+"%") AS `fraction`

//fraction of tags included in the text of the caption
MATCH (in_caption:SDTag {in_caption:true})
WITH COUNT(DISTINCT in_caption) AS c
MATCH (floating:SDTag {in_caption:false}) 
WITH c, COUNT(DISTINCT floating) AS f
RETURN c AS `in caption`, f AS `not in caption`, toString(ROUND(100*tofloat(c)/(c+f)))+"%" AS `%`

///////////HYPOTHESIS SEARCH/////////////////////

//convergent-divergent 'master regulator' motif
//master regulator --> many intermediate genes or proteins <--> proteins --> common target
//requires gene2protein mapping
// 
// In this demo, we illustrate the search for network motifs. Consider a motif that 
// includes a specific gene that was tested across multiple studies for its impact on 
// multiple gene products which, in turn, have all been tested for their converging effect 
// on a specific cellular structure or cell type. This kind of divergent-convergent motif 
// might be expected for regulators of cellular processes, whereby a ‘master regulator’ 
// controls a series of intermediate gene products which are all involved in regulating a 
// given biological function (e.g. SREBP controlling several enzymes that are all involved 
// in cholesterol biosynthesis). When such a query is run on our dataset using 
// “mitochondria” as endpoint of the motif, it is able to prioritize known regulators of 
// mitochondrial fission Drp1 and Fis1.  Similarly, when querying the system with 
// “autophagosomes” as target, key regulators of autophagy such as Atg5, LC3 and beclin-1 
// are prioritized.

MATCH 
    (mr:H_Entity)-[divergent_H:Tested]->(intermediate1:H_Entity),
    (intermediate2:H_Entity)-[convergent_H:Tested]->(target:H_Entity),
    (intermediate2)-[:gene2protein]->(intermediate1),
    (mr)-->(mrte:Term), (target)-->(targette:Term)

WHERE 
    mr.scale = 2 AND target.scale >= mr.scale AND
    mr <> intermediate1 AND mr <> target AND target<>intermediate2 AND
    mr <> intermediate2 AND target <> intermediate1 AND
    (intermediate1.type = "gene" OR intermediate1.type = "protein") AND
    (intermediate2.type = "gene" OR intermediate2.type = "protein") AND
    substring(mrte.text,1,4) <> substring(targette.text,1,4)
    //AND lower(targette.text) =~ ".*mitochondria.*" 
    AND lower(targette.text) =~ ".*autophag.*" 

WITH 
    mr, target, 
    COLLECT(DISTINCT mrte)[0] AS mr_tag, COLLECT(DISTINCT targette)[0] AS target_tag,
    COLLECT(DISTINCT intermediate1) + COLLECT(DISTINCT intermediate2) AS intermediates,
    COLLECT(DISTINCT divergent_H) AS divergent_Hs,
    COLLECT(DISTINCT convergent_H) AS convergent_Hs,
    COUNT(DISTINCT intermediate1) AS N //this is metric to be maximized

OPTIONAL MATCH
    (mr)-[divergent_H_direct:Tested]->(direct:H_Entity)-[convergent_H_direct:Tested]->(target)
WHERE 
   (direct.type = "gene" OR direct.type = "protein") AND 
   mr <> direct AND mr <> target AND target <> direct
WITH 
   mr, target, mr_tag, target_tag,
   COLLECT(DISTINCT divergent_H_direct)  AS additional_divergent_Hs,
   COLLECT(DISTINCT convergent_H_direct) AS additional_convergent_Hs,
   intermediates, divergent_Hs, convergent_Hs, N, 
   COLLECT(DISTINCT direct) AS direct_intermediates, COUNT(DISTINCT direct) AS N_d

WITH 
   DISTINCT //mr,
   //target, 
   mr_tag, 
   target_tag,
   //intermediates, 
   //divergent_Hs, 
   //convergent_Hs,
   //direct_intermediates, additional_divergent_Hs, additional_convergent_Hs,
   N,
   N_d,
   N + N_d AS score
WHERE score > 5
RETURN mr_tag, target_tag, score
ORDER BY score DESC 
SKIP 0 LIMIT 100;

//drug-->protein<-->gene-->subcellular structure
//In this demo, we search whether a given entity X was tested for its effect on a gene 
// product Y which was in turn tested for its effect on larger biological structure Z. For 
// example, using infliximab, a TNF-α inhibitor, as starting point of the query (X), the 
// system can identify experiments testing the effect of this drug on Amyloid ß (Y) and 
// the effect of presenilin on dendrites or axons (Z), thus providing a set of articles 
// and data delineating a potential mechanistic path (X-->Y-->Z) from the small molecule 
// to a cellular structure. 

MATCH
   (small_mol:H_Entity {type:"molecule"})-->(h1:Hypothesis)-->(protein:H_Entity {type:"protein"}),
   (gene)-[:gene2protein]->(protein),
   (gene:H_Entity {type:"gene"})-->(h2:Hypothesis)-->(subcell:H_Entity {type:"subcellular"})
WITH h1, h2, small_mol, gene, protein, subcell
MATCH
   (small_mol)-->(t1:Term), (gene)-->(t2:Term), (protein)-->(t3:Term), (subcell)-->(t4:Term)
WHERE t1.text<>"nutrient" AND t1.text =~ "(?i)infliximab"
WITH DISTINCT
   h1, h2,
   small_mol, COLLECT(DISTINCT t1.text) AS txt_small_mol, 
   gene, COLLECT(DISTINCT t2.text) AS txt_gene,
   protein, COLLECT(DISTINCT t3.text) AS txt_protein,
   subcell, COLLECT(DISTINCT t4.text) AS text_subcell
MATCH
   (a1:SDArticle)-->(h1:Hypothesis),
   (a2:SDArticle)-->(h2:Hypothesis)
//enforcing results from different papers, only a few possibilities left
WHERE a1<>a2
RETURN DISTINCT
   small_mol, txt_small_mol, 
   gene, txt_gene,
   protein, txt_protein,
   subcell, text_subcell,
   COLLECT(DISTINCT a1.doi) AS drug_papers,
   COLLECT(DISTINCT a2.doi) AS phenotype_papers;
   
   
   
   


