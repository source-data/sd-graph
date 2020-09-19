//indices and constraints
// drop all
DROP INDEX ON :SDArticle(doi);
DROP INDEX ON :SDTag(text);
DROP INDEX ON :SDTag(ext_ids);
DROP INDEX ON :SDTag(type);
DROP INDEX ON :SDTag(role);
DROP INDEX ON :SDTag(ext_names);
DROP INDEX ON :SDTag(norm_text);
DROP INDEX ON :CondTag(ext_ids);
DROP INDEX ON :CondTag(text);
DROP INDEX ON :CondTag(ext_tax_names);
DROP INDEX ON :H_Entity(ext_ids);
DROP INDEX ON :H_Entity(type);
DROP INDEX ON :CondTag(category);
DROP INDEX ON :CondTag(name);
DROP INDEX ON :VizPaper(doi);

//create
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
CREATE INDEX ON :VizPaper(doi);


//Full text indexing
//drop all
CALL db.index.fulltext.drop("name");
CALL db.index.fulltext.drop("entity_name");
CALL db.index.fulltext.drop("synonym");
CALL db.index.fulltext.drop("title");
CALL db.index.fulltext.drop("abstract");
CALL db.index.fulltext.drop("abstract_jats");
CALL db.index.fulltext.drop("title_jats");
CALL db.index.fulltext.drop("caption");

// create
CALL db.index.fulltext.createNodeIndex("name",["Contrib"], ["surname", "given_names"]);
CALL db.index.fulltext.createNodeIndex("entity_name",["H_Entity"],["name"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("synonym",["Term"],["text"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("title", ["SDArticle"], ["title"], {analyzer: "english"});
CALL db.index.fulltext.createNodeIndex("abstract", ["SDArticle"], ["abstract"], {analyzer: "english"});
// second index on abstract used to search JATS/MECA and create COVID-19 collection
CALL db.index.fulltext.createNodeIndex("abstract_jats", ["Article"], ["abstract"], {analyzer: "simple"});
CALL db.index.fulltext.createNodeIndex("title_jats", ["Article"], ["title"], {analyzer: "simple"});
CALL db.index.fulltext.createNodeIndex("caption", ["SDPanel"], ["caption"], {analyzer: "english"});