// PURGE PRECOMPUTED
:begin
RETURN "purging docmap graph" as `preparation step`;
:commit

:begin
MATCH (n:Resource) DETACH DELETE n;
MATCH (n:Docmap) DETACH DELETE n;
MATCH (n:Preprint) DETACH DELETE n;
MATCH (n:RefereeReport) DETACH DELETE n;
MATCH (n:AuthorReply) DETACH DELETE n;
MATCH (n:Person) DETACH DELETE n;
MATCH (n:Creator) DETACH DELETE n;
MATCH (n:Content) DETACH DELETE n;
MATCH (n:Assertion) DETACH DELETE n;
MATCH (n:Action) DETACH DELETE n;
RETURN "purge" as `completed`;
:commit

:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH (a:Article)
OPTIONAL MATCH (a)-[r:HasReview]->(review:Review {reviewed_by: rs.name})
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: rs.name})
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response {reviewed_by: rs.name})
WITH rs, a, review, annot, response
WHERE 
    (review is NOT NULL OR response is NOT NULL OR annot IS NOT NULL)
    AND a.journal_title IN ['bioRxiv', 'medRxiv']
WITH DISTINCT rs, a.doi as doi, a.publication_date as published
ORDER BY DATETIME(published)
// keep oldest published date
WITH DISTINCT rs, doi, COLLECT(published)[0] as published
MERGE (preprint:Preprint {
  uri: "https://doi/org/" + doi,
  doi: doi,
  published: toString(DATETIME(published))
})
MERGE (docmap:Docmap {
  description: "This is a Docmap description of a refereed preprint.",
  created: toString(DATETIME()),
  provenance: "Early Evidence Base aggregator.",
  creator: "https://eeb.embo.org",
  publisher: rs.url,
  doi: doi,
  uri: "https://eeb.embo.org/api/v2.1/docmap/" + doi
})
MERGE (docmap)<-[:actions]-(action:Action {uri: "bnode://genid-"+apoc.create.uuid()})<-[:inputs]-(preprint)
RETURN COUNT(docmap) AS `docmap isStatusHeldBy`;
:commit

:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
    (docmap:Docmap {publisher: rs.url})<-[:actions]-(action:Action),
    (a:Article {doi: docmap.doi})-[r:HasReview]->(review:Review {reviewed_by: rs.name})
WHERE review is NOT NULL
WITH DISTINCT
  docmap, action, review
MERGE (action)<-[:outputs]-(rev:RefereeReport {
  creator: "reviewer #" + review.review_idx,
  published: review.posting_date,
  uri: "https://eeb.embo.org/api/v2/review_material/"+id(review),
  content: "https://eeb.embo.org/api/v2/review_material/"+id(review)
})
RETURN COUNT(DISTINCT rev) AS `review linked`;
:commit

:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
    (docmap:Docmap {publisher: rs.url})<-[:actions]-(:Action)<-[:outputs]-(review:RefereeReport),
    (a:Article {doi: docmap.doi})
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response {reviewed_by: rs.name})
WITH docmap, review, response
WHERE response is NOT NULL
WITH DISTINCT
  docmap, COLLECT(DISTINCT review) AS reviews, response
MERGE (docmap)<-[:actions]-(action:Action {uri: "bnode://genid-" + apoc.create.uuid()})
WITH DISTINCT docmap, reviews, response, action
UNWIND reviews as review
WITH DISTINCT docmap, review, response, action
MERGE (review)-[:inputs]->(action)
MERGE (action)<-[:outputs]-(resp:AuthorReply {
  published: response.posting_date,
  uri: "https://eeb.embo.org/api/v2/review_material/"+id(response),
  content: "https://eeb.embo.org/api/v2/review_material/"+id(response)
})
RETURN COUNT(DISTINCT response) AS `response linked`;
:commit

:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
    (docmap:Docmap {publisher: rs.url})<-[:actions]-(reply_action:Action)<-[:outputs]-(reply:AuthorReply),
    (docmap)<-[:actions]-(review_action:Action)<-[:inputs]-(preprint:Preprint)
WITH DISTINCT docmap, preprint, reply
MATCH (a:Article {doi: preprint.doi})-[:has_author]->(author:Contrib)
OPTIONAL MATCH (author)-[:has_orcid]->(orcid:Contrib_id)
WITH DISTINCT
    reply, author,
    CASE 
        WHEN orcid IS NULL THEN "null"
        ELSE orcid.text
    END AS orcid
MERGE (reply)<-[:created]-(person_author:Author {
  identifier: orcid,
  firstName: author.given_names,
  familyName: author.surname
})
RETURN COUNT(person_author) AS `authors linked to replies`;
:commit


:begin
// setup for semantic mapping

CALL n10s.graphconfig.init({handleVocabUris: 'MAP'});
:commit

:begin
CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS ON (r:Resource)
ASSERT r.uri IS UNIQUE;
:commit

:begin
// prefixes
CALL n10s.nsprefixes.add("dct", "http://purl.org/dc/terms/");
CALL n10s.nsprefixes.add("foaf", "http://xmlns.com/foaf/0.1/");
CALL n10s.nsprefixes.add("part", "http://www.ontologydesignpatterns.org/cp/owl/participation.owl#");
CALL n10s.nsprefixes.add("fabio", "http://purl.org/spar/fabio/");
CALL n10s.nsprefixes.add("pso", "http://purl.org/spar/pso/");
CALL n10s.nsprefixes.add("pwo", "http://purl.org/spar/pwo/");
CALL n10s.nsprefixes.add("xsd", "http://www.w3.org/2001/XMLSchema#");
CALL n10s.nsprefixes.add("prism", "http://prismstandard.org/namespaces/basic/2.0/");
:commit


:begin
// mappings
WITH [
    { internal: "Docmap", uri: "http://purl.org/spar/pwo/", pub: "WorkflowExecution"},
    { internal: "Action", uri: "http://purl.org/spar/pwo/", pub: "Action"},
    { internal: "created", uri: "http://purl.org/dc/terms/", pub: "created"},
    { internal: "title", uri: "http://purl.org/dc/terms/", pub: "title" },
    { internal: "doi", uri: "http://purl.org/dc/terms/", pub: "doi" },
    { internal: "Creator", uri: "http://purl.org/spar/fabio/", pub: "creator" },
    { internal: "published", uri: "http://prismstandard.org/namespaces/basic/2.0/", pub: "publicationDate" },
    { internal: "name", uri: "http://xmlns.com/foaf/0.1/", pub: "name" },
    { internal: "Author", uri: "http://xmlns.com/foaf/0.1/", pub: "Person" },
    { internal: "Preprint", uri: "http://purl.org/spar/fabio/", pub: "Preprint"},
    { internal: "RefereeReport", uri: "http://purl.org/spar/fabio/", pub: "ProductReview"},
    { internal: "AuthorReply", uri: "http://purl.org/spar/fabio/", pub: "Reply"},
    { internal: "publisher", uri: "http://purl.org/dc/terms/", pub: "publisher" },
    { internal: "provenance", uri: "http://purl.org/dc/terms/", pub: "provenance" },
    { internal: "inputs", uri: "http://purl.org/spar/pwo/", pub: "needs" },
    { internal: "outputs", uri: "http://purl.org/spar/pwo/", pub: "produces" },
    { internal: "assertions", uri: "http://purl.org/spar/pso/", pub: "resultsInAcquiring" },
    { internal: "involved", uri: "http://www.ontologydesignpatterns.org/cp/owl/participation.owl#", pub: "hasParticipant" },
    { internal: "actions", uri: "http://purl.org/spar/pwo/", pub: "involvesAction" },
    { internal: "item", uri: "http://purl.org/spar/pso/", pub: "isStatusHeldBy" },
    { internal: "status", uri: "http://purl.org/spar/pso/", pub: "withStatus" },
    { internal: "content", uri: "http://purl.org/spar/fabio/", pub: "hasManifestation" },
    { internal: "hasUrl", uri: "http://purl.org/spar/fabio/", pub: "hasURL" }
] as mappings

UNWIND mappings as m
    CALL n10s.mapping.add(m.uri + m.pub, m.internal) YIELD schemaElement
RETURN
    count(schemaElement) AS mappingsDefined;
:commit

//try 
// :POST /rdf/neo4j/cypher
// {"cypher": "MATCH path=(preprint:Preprint)-[:inputs]->(action1:Action)<-[:outputs]-(ref:RefereeReport)-[:inputs]->(actions2:Action)<-[:outputs]-(reply:AuthorReply), (docmap)<-[:actions]-(action_1) RETURN path LIMIT 1", "format": "JSON-LD"}