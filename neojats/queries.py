
from neotools.db import Cypher


SOURCE_BY_UUID = Cypher(
    code='''MATCH (n:Article {source: $source}) RETURN n;''',
    params={'source': ['source', '']},
    returns=['n']
)

CREAT_FULLTEXT_INDICES = Cypher(
    code='''
CALL db.index.fulltext.createNodeIndex("title_abstract_caption",["Title", 
    "Abstract", "Caption"],["text"]);
//CALL db.index.fulltext.createNodeIndex("names",["Given_names", "Surname"],
    ["text"]);
'''
)