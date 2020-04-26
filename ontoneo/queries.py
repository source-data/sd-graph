from neotools.db import Query

CONTRAINT_CLASS_UNIQUE = Query(
    code='''
CREATE CONSTRAINT ON (c:Class) ASSERT c.about IS UNIQUE;
    '''
)

REMOVE_DEPRECATED = Query(
    code='''
MATCH (:Class {deprecated:'true'})-[r]-()
DELETE (r)
RETURN COUNT(r) AS N
UNION
MATCH (c:Class {deprecated:'true'})
DELETE (c)
RETURN COUNT(c) AS N
    ''',
    returns=['N']
)

MAKE = Query(
    code='''
MATCH (sub_class:Class)
WHERE 
    EXISTS(sub_class.subClassOf)
WITH sub_class
MATCH
(super_class:Class)
WHERE
    super_class.about IN sub_class.subClassOf
MERGE (super_class)-[r:super]->(sub_class)
RETURN COUNT(r) AS N
    ''',
    returns=['N']
)