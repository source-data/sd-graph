
// Delete article where abstract is missing

// Delete first related SDNodes
MATCH (a:Article)
WHERE
  NOT EXISTS(a.abstract)
WITH a
MATCH  (sda:SDArticle {doi: a.doi})-->(sdf:SDFigure)-->(sdp:SDPanel)-->(sdt:SDTag)-->(sdct:CondTag)
//RETURN sda, sdf, sdp, sdt, sdct
DETACH DELETE sda, sdf, sdp, sdt, sdct;

// Check for orphan entities
MATCH (h:H_Entity)
WHERE NOT EXISTS((h)<-[:Identified_by]-(:CondTag))
DETACH DELETE h;

// Check for orphan terms
MATCH (te:Term)
WHERE NOT EXISTS((te)<-[:Has_text]-(:H_Entity))
DETACH DELETE te;

// Remove article, figs and authors with id
MATCH (a:Article)-->(f:Fig), (a)-->(c:Contrib)
WHERE NOT EXISTS(a.abstract) 
OPTIONAL MATCH
  (c)-->(id:Contrib_id)
DETACH DELETE id
DETACH DELETE c
DETACH DELETE f
DETACH DELETE a;

// General check for orphan
MATCH (n)
WHERE NOT EXISTS((n)--())
RETURN DISTINCT labels(n) AS `orphan types`, COUNT(n) AS `orphan nodes`;

