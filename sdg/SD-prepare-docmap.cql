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
MATCH (n:Step) DETACH DELETE n;
MATCH (n:WebPage) DETACH DELETE n;
RETURN "purge" as `completed`;
:commit


// Preprint and Docmap backbone
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
WITH rs, doi, published, "_:b-"+apoc.create.uuid() as first_step
MERGE (preprint:Preprint {
  uri: "https://doi.org/" + doi,
  doi: doi,
  published: toString(DATETIME(published))
})
MERGE (docmap:Docmap {
  type: "docmap",
  created: toString(DATETIME()),
  generatedAt: toString(DATETIME()),
  provider: "https://eeb.embo.org",
  publisher: rs.url,
  id: "https://eeb.embo.org/api/v2.1/docmap/" + doi,
  first_step: first_step
})
// MERGE (docmap)<-[:actions]-(action:Action {uri: "bnode://genid-"+apoc.create.uuid()})<-[:inputs]-(preprint)
MERGE (docmap)<-[:steps]-(step:Step {id: first_step})
MERGE (step)<-[:inputs]-(preprint)
RETURN COUNT(docmap) AS `docmap generated`;
:commit


// RefereeReports
:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
  (docmap:Docmap {publisher: rs.url})<-[:steps]-(step:Step)<-[:inputs]-(preprint:Preprint),
  (a:Article {doi: preprint.doi})-[r:HasReview]->(review:Review {reviewed_by: rs.name})
WHERE review is NOT NULL
WITH DISTINCT
  preprint.uri AS preprint_uri, docmap, step, review
WITH preprint_uri, docmap, step, review, "_:b-"+apoc.create.uuid() AS action_uuid
MERGE (step)<-[:assertions]-(assertion:Assertion {
  item: preprint_uri,
  status: "reviewed"
})
MERGE (step)<-[:actions]-(action:Action {id: action_uuid, index: review.review_idx})
MERGE (action)<-[:participants]-(reviewer:Person {
  id : "reviewer #" + review.review_idx,
  name: "anonymous",
  role: "peer-reviewer"
})
MERGE (action)<-[:outputs]-(rev:RefereeReport {
  published: review.posting_date,
  uri: "https://eeb.embo.org/api/v2/review_material/"+id(review)
})
MERGE (rev)<-[:content]-(content:Content {
  type: "web-page", 
  url: "https://eeb.embo.org/api/v2/review_material/"+id(review)
})
RETURN COUNT(DISTINCT rev) AS `review linked`;
:commit


// Reply
:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
  (docmap:Docmap {publisher: rs.url})<-[:steps]-(reviewing_step:Step)<-[:actions]-(:Action)<-[:outputs]-(review:RefereeReport),
  (reviewing_step)<-[:inputs]-(preprint:Preprint),
  (a:Article {doi: preprint.doi})
OPTIONAL MATCH (a)-[:HasResponse]->(response:Response {reviewed_by: rs.name})
WITH DISTINCT preprint.uri AS preprint_uri, docmap, reviewing_step, review, response
WHERE response is NOT NULL
WITH DISTINCT
  preprint_uri, docmap, reviewing_step, COLLECT(DISTINCT review) AS reviews, response
WITH
  preprint_uri, docmap, reviewing_step, reviews, response, "_:b-"+apoc.create.uuid() as reply_step
SET reviewing_step.next_step = reply_step
MERGE (docmap)<-[:steps]-(step:Step {id: reply_step, previous_step: reviewing_step.id})
MERGE (step)<-[:assertions]-(assertion:Assertion {
  item: preprint_uri,
  status: "authors-replied-to-reviewers"
})
WITH DISTINCT docmap, reviews, response, step
UNWIND reviews as review
WITH DISTINCT docmap, review, response, step
MERGE (step)<-[:inputs]-(review)
WITH DISTINCT docmap, response, step
WITh docmap, response, step, "_:b-"+apoc.create.uuid() AS action_uuid
MERGE (step)<-[:actions]-(action:Action {id: action_uuid})
MERGE (action)<-[:outputs]-(reply:AuthorReply {
  published: response.posting_date,
  uri: "https://eeb.embo.org/api/v2/review_material/"+id(response)
})
MERGE (reply)<-[:content]-(content:Content {
  type: "web-page",
  url: "https://eeb.embo.org/api/v2/review_material/"+id(response)
})
RETURN COUNT(DISTINCT response) AS `response linked`;
:commit


// Authors
:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
  (docmap:Docmap {publisher: rs.url})<-[:steps]-(replying_step:Step)<-[:actions]-(reply_action:Action)<-[:outputs]-(reply:AuthorReply),
  (docmap)<-[:steps]-(reviwing_step:Step)<-[:inputs]-(preprint:Preprint)
WITH DISTINCT docmap, preprint, reply_action
MATCH (a:Article {doi: preprint.doi})-[:has_author]->(author:Contrib)
OPTIONAL MATCH (author)-[:has_orcid]->(orcid:Contrib_id)
WITH DISTINCT
  reply_action, author,
  CASE 
    WHEN orcid IS NULL THEN "null"
    ELSE orcid.text
  END AS orcid
MERGE (reply_action)<-[:participants]-(person:Person {
  identifier: orcid,
  firstName: author.given_names,
  familyName: author.surname,
  role: "author"
})
RETURN COUNT(person) AS `authors linked to replies`;
:commit


// :begin
// // setup for semantic mapping

// CALL n10s.graphconfig.init({handleVocabUris: 'MAP'});
// :commit

// :begin
// CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS ON (r:Resource)
// ASSERT r.uri IS UNIQUE;
// :commit

// :begin
// // prefixes
// CALL n10s.nsprefixes.add("dct", "http://purl.org/dc/terms/");
// CALL n10s.nsprefixes.add("foaf", "http://xmlns.com/foaf/0.1/");
// CALL n10s.nsprefixes.add("part", "http://www.ontologydesignpatterns.org/cp/owl/participation.owl#");
// CALL n10s.nsprefixes.add("fabio", "http://purl.org/spar/fabio/");
// CALL n10s.nsprefixes.add("pso", "http://purl.org/spar/pso/");
// CALL n10s.nsprefixes.add("pwo", "http://purl.org/spar/pwo/");
// CALL n10s.nsprefixes.add("xsd", "http://www.w3.org/2001/XMLSchema#");
// CALL n10s.nsprefixes.add("prism", "http://prismstandard.org/namespaces/basic/2.0/");
// :commit


// :begin
// // mappings
// WITH [
//     { internal: "Docmap", uri: "http://purl.org/spar/pwo/", pub: "WorkflowExecution"},
//     { internal: "Action", uri: "http://purl.org/spar/pwo/", pub: "Action"},
//     { internal: "created", uri: "http://purl.org/dc/terms/", pub: "created"},
//     { internal: "title", uri: "http://purl.org/dc/terms/", pub: "title" },
//     { internal: "doi", uri: "http://purl.org/dc/terms/", pub: "doi" },
//     { internal: "Creator", uri: "http://purl.org/spar/fabio/", pub: "creator" },
//     { internal: "published", uri: "http://prismstandard.org/namespaces/basic/2.0/", pub: "publicationDate" },
//     { internal: "name", uri: "http://xmlns.com/foaf/0.1/", pub: "name" },
//     { internal: "Author", uri: "http://xmlns.com/foaf/0.1/", pub: "Person" },
//     { internal: "Preprint", uri: "http://purl.org/spar/fabio/", pub: "Preprint"},
//     { internal: "RefereeReport", uri: "http://purl.org/spar/fabio/", pub: "ProductReview"},
//     { internal: "AuthorReply", uri: "http://purl.org/spar/fabio/", pub: "Reply"},
//     { internal: "publisher", uri: "http://purl.org/dc/terms/", pub: "publisher" },
//     { internal: "provenance", uri: "http://purl.org/dc/terms/", pub: "provenance" },
//     { internal: "inputs", uri: "http://purl.org/spar/pwo/", pub: "needs" },
//     { internal: "outputs", uri: "http://purl.org/spar/pwo/", pub: "produces" },
//     { internal: "assertions", uri: "http://purl.org/spar/pso/", pub: "resultsInAcquiring" },
//     { internal: "involved", uri: "http://www.ontologydesignpatterns.org/cp/owl/participation.owl#", pub: "hasParticipant" },
//     { internal: "actions", uri: "http://purl.org/spar/pwo/", pub: "involvesAction" },
//     { internal: "item", uri: "http://purl.org/spar/pso/", pub: "isStatusHeldBy" },
//     { internal: "status", uri: "http://purl.org/spar/pso/", pub: "withStatus" },
//     { internal: "content", uri: "http://purl.org/spar/fabio/", pub: "hasManifestation" },
//     { internal: "hasUrl", uri: "http://purl.org/spar/fabio/", pub: "hasURL" }
// ] as mappings

// UNWIND mappings as m
//     CALL n10s.mapping.add(m.uri + m.pub, m.internal) YIELD schemaElement
// RETURN
//     count(schemaElement) AS mappingsDefined;
// :commit

//try 
// :POST /rdf/neo4j/cypher
// {"cypher": "MATCH path=(preprint:Preprint)-[:inputs]->(action1:Action)<-[:outputs]-(ref:RefereeReport)-[:inputs]->(actions2:Action)<-[:outputs]-(reply:AuthorReply), (docmap)<-[:actions]-(action_1) RETURN path LIMIT 1", "format": "JSON-LD"}