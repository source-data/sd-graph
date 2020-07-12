// purge preliminary entries obtained from the biorxiv and crossref api
MATCH (a:Article {source: "biorxiv_crossref"})-[au_link]-(au:Author)-[orcid_link]->(orcid:Contrib_id)
WITH au, orcid_link
DELETE orcid_link
WITH au
DELETE au
WITH COUNT(DISTINCT au) AS `author with ORCID`
MATCH (a:Article {source: "biorxiv_crossref"})-[au_link]-(au:Author)
WITH au_link, au
DELETE au_link
WITH au
DELETE au
WITH COUNT(DISTINCT au) AS `author without ORCID`
MATCH (a:Article {source: "biorxiv_crossref"})-[r]-()
WITH a, r
DELETE r
WITH a
DELETE a
RETURN 'done' AS `deleted prelim article and their authors and reviews`;

MATCH (orcid:Contrib_id)
WHERE NOT EXISTS((orcid)-[:has_orcid]-())
DELETE orcid
RETURN COUNT(orcid) AS `deleted unlinked Contrib_id`;
