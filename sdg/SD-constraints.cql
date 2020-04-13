////////CONSTRAINTS////////
CREATE CONSTRAINT ON (a:SDArticle) ASSERT a.doi IS unique;
RETURN "constraint unique_article_doi created";

//unique terms
CREATE CONSTRAINT ON (te:Term) ASSERT te.text IS UNIQUE;
RETURN "constraint unique_term_text created";