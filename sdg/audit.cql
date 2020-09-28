// orphan nodes
MATCH (n)
WHERE NOT EXISTS((n)--())
RETURN DISTINCT labels(n) AS `orphan types`, COUNT(n) AS `orphan nodes`;

// critical fields empty
MATCH (a:Article)
WHERE NOT EXISTS(a.abstract)
RETURN COUNT(a) AS `article without abstract`

MATCH (a:Article)
WHERE NOT EXISTS(a.doi)
RETURN COUNT(a) AS `article without doi`

// duplicates
