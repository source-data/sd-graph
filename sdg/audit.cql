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