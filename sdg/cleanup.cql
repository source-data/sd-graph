
// Delete article where abstract is missing

// Delete first related SDNodes
MATCH (a:Article)
WHERE
  NOT EXISTS(a.abstract)
WITH a
MATCH  (sda:SDArticle {doi: a.doi})-->(sdf:SDFigure)-->(sdp:SDPanel)-->(sdt:SDTag)-->(sdct:CondTag)
//RETURN sda, sdf, sdp, sdt, sdct
DETACH DELETE sda, sdf, sdp, sdt, sdct
RETURN COUNT(DISTINCT sda) AS `Deleted SDArticle linked to article without abstract`;

// Check for orphan entities
MATCH (h:H_Entity)
WHERE NOT EXISTS((h)<-[:Identified_by]-(:CondTag))
DETACH DELETE h
RETURN COUNT(DISTINCT h) AS `orphan entities deleted`;

// Check for orphan terms
MATCH (te:Term)
WHERE NOT EXISTS((te)<-[:Has_text]-(:H_Entity))
DETACH DELETE te
RETURN COUNT(DISTiNCT te) AS `orphan terms deleted`;

// Remove article, figs and authors with id
MATCH (a:Article)
WHERE NOT EXISTS(a.abstract)
OPTIONAL MATCH
  (a)-->(f:Fig)
OPTIONAL MATCH
  (a)-->(c:Contrib)
OPTIONAL MATCH
  (c)-->(:Contrib)-->(id:Contrib_id)
DETACH DELETE id
DETACH DELETE c
DETACH DELETE f
DETACH DELETE a
RETURN COUNT(DISTINCT a) AS `article without abstracts deleted`;

