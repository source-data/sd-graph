// purge preliminary entries obtained from the biorxiv and crossref api
MATCH (a:Article {source: "biorxiv_crossref"})-[r1]-(au:Author)
OPTIONAL MATCH (au)-[r2:HasOrcid]->(orcid:Contrib_id) 
DELETE r2, r1, au, a
RETURN COUNT(DISTINCT a) AS `deleted prelim article and their authors`;

MATCH (orcid:Contrib_id)
WHERE NOT EXISTS((orcid)-[:has_orcid]-())
DELETE orcid
RETURN COUNT(orcid) AS `deleted unlinked Contrib_id`;
