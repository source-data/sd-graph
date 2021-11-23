// orphan nodes
MATCH (n)
WHERE NOT EXISTS((n)--())
RETURN DISTINCT labels(n) AS `orphan types`, COUNT(n) AS `orphan nodes`;

// critical fields empty
MATCH (a:Article)
WHERE NOT EXISTS(a.abstract) OR a.abstract = ""
RETURN COUNT(a) AS `article without or with empty abstract`;

MATCH (a:Article)
WHERE NOT EXISTS(a.doi) OR a.doi = ""
RETURN COUNT(a) AS `article without or with empty doi`;

MATCH (sda:SDArticle)
WHERE NOT EXISTS(sda.doi) OR sda.doi = ""
RETURN COUNT(sda) AS `SDArticle without or with empty doi`;

MATCH (sda:SDArticle)
WHERE NOT EXISTS(sda.title) OR sda.title = ""
RETURN COUNT(sda) AS `SDArticle without or with empty title`;

// duplicates
MATCH (a:Article)
WITH DISTINCT a.doi AS doi, a.version AS version, a.source AS meca, COUNT(a) AS N
WHERE N > 1
RETURN COUNT(DISTINCT doi) AS `duplicate meca imports`;

MATCH (a:SDArticle)
WITH DISTINCT a.doi  AS doi, COUNT(a) AS N
WHERE N > 1
RETURN COUNT(DISTINCT doi) AS `duplicate doi SDArticle`;

MATCH (orcid:Contrib_id)
WITH DISTINCT orcid.text, COUNT(DISTINCT orcid) AS duplicates
WHERE duplicates > 1
RETURN COUNT(DISTINCT text) AS `orcid with duplicate nodes`;


// check number of preprints imported by year and month
WITH
  [2020, 2021] as years,
  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] AS months
UNWIND years as year
UNWIND months as month
MATCH (a:Article)
WHERE
  date(a.publication_date).year = year AND 
  date(a.publication_date).month = month
RETURN
  year, 
  month, 
  COUNT(DISTINCT a);

// detecting reviews posted multiple times
MATCH (a:Article)-->(rev:Review), (a)-->(resp:Response)
WITH DISTINCT a.doi AS doi, COUNT(DISTINCT rev) AS N_review, COUNT(DISTINCT resp) AS N_resp
WHERE N_review > 3 AND N_resp > 1
RETURN DISTINCT doi AS `preprint with suspiciously more than 3 reviews and 1 response`;

// What kind of nodes exist
// Sample some nodes, reporting on property and relationship counts per node.
MATCH (n) WHERE rand() <= 0.1
RETURN
DISTINCT
  labels(n),
  count(*) AS SampleSize,
  avg(size(keys(n))) as Avg_PropertyCount,
  min(size(keys(n))) as Min_PropertyCount,
  max(size(keys(n))) as Max_PropertyCount,
  avg(size( (n)-[]-() ) ) as Avg_RelationshipCount,
  min(size( (n)-[]-() ) ) as Min_RelationshipCount,
  max(size( (n)-[]-() ) ) as Max_RelationshipCount;