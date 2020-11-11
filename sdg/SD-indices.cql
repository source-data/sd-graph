//indices and constraints
//create
CREATE INDEX sdarticle_doi IF NOT EXISTS FOR (n:SDArticle) ON (n.doi);
CREATE INDEX sdtga_text IF NOT EXISTS FOR (n:SDTag) ON (n.text);
CREATE INDEX sdtag_ext_ids IF NOT EXISTS FOR (n:SDTag) ON (n.ext_ids);
CREATE INDEX sdtag_type IF NOT EXISTS FOR (n:SDTag) ON (n.type);
CREATE INDEX sdtag_role IF NOT EXISTS FOR (n:SDTag) ON (n.role);
CREATE INDEX sdtag_ext_names IF NOT EXISTS FOR (n:SDTag) ON (n.ext_names);
CREATE INDEX sdtag_norm_text IF NOT EXISTS FOR (n:SDTag) ON (n.norm_text);
CREATE INDEX condtag_ext_ids IF NOT EXISTS FOR (n:CondTag) ON (n.ext_ids);
CREATE INDEX condtag_text IF NOT EXISTS FOR (n:CondTag) ON (n.text);
CREATE INDEX condtag_ext_tax_names IF NOT EXISTS FOR (n:CondTag) ON (n.ext_tax_names);
CREATE INDEX h_entity_ext_ids IF NOT EXISTS FOR (n:H_Entity) ON (n.ext_ids);
CREATE INDEX h_entity_typ IF NOT EXISTS FOR (n:H_Entity) ON (n.type);
CREATE INDEX condtag_category IF NOT EXISTS FOR (n:CondTag) ON (n.category);
CREATE INDEX condtag_name IF NOT EXISTS FOR (n:CondTag) ON (n.name);
CREATE INDEX vizpaper_doi IF NOT EXISTS FOR (n:VizPaper) ON (n.doi);


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