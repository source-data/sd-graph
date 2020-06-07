//indices and constraints

CREATE INDEX ON :SDArticle(doi);
CREATE INDEX ON :SDTag(text);
CREATE INDEX ON :SDTag(ext_ids);
CREATE INDEX ON :SDTag(type);
CREATE INDEX ON :SDTag(role);
CREATE INDEX ON :SDTag(ext_names);
CREATE INDEX ON :SDTag(norm_text);
CREATE INDEX ON :CondTag(ext_ids);
CREATE INDEX ON :CondTag(text);
CREATE INDEX ON :CondTag(ext_tax_names);
CREATE INDEX ON :H_Entity(ext_ids);
CREATE INDEX ON :H_Entity(type);
CREATE INDEX ON :CondTag(category);
CREATE INDEX ON :CondTag(name);

//Full text indexing
CALL db.index.fulltext.createNodeIndex("name",["Contrib"], ["surname", "given_names"]);
CALL db.index.fulltext.createNodeIndex("entity_name",["H_Entity"],["name"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("synonym",["Term"],["text"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("title", ["SDArticle"], ["title"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("abstract", ["SDArticle"], ["abstract"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("caption", ["SDPanel"], ["caption"], {analyzer: "english"});