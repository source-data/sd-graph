////////CONSTRAINTS////////
CREATE CONSTRAINT ON (a:Article) ASSERT a.doi IS unique;

//NOTE it is the compound keys text,type OR ext_id,type that should be unique. 
//hybrid entity unique for text
CREATE CONSTRAINT ON (hyb:H_Entity) ASSERT hyb.text IS UNIQUE;

//hybrid entity unique for ext_id
CREATE CONSTRAINT ON (hyb:H_Entity) ASSERT hyb.ext_id IS UNIQUE;

//unique terms
CREATE CONSTRAINT ON (te:Term) ASSERT te.text IS UNIQUE;