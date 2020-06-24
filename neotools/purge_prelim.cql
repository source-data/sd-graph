// purge preliminary entries obtained from the biorxiv and crossref api
MATCH (a:Article {source: "biorxiv_crossref"})-[r]-() DELETE r;

MATCH (a:Article {source: "biorxiv_crossref"}) DELETE a;

MATCH (unlinked_author:Contrib)
OPTIONAL MATCH (unlinked_author)-[r]-()
WHERE NOT EXISTS((a:Article)-->(unlinked_author))
DELETE r, unlinked;

MATCH (unlinked_orcid)
WHERE NOT EXISTS ((au:Contrib)-->(unlinked_orcid))
DELETE unlinked_orcid;