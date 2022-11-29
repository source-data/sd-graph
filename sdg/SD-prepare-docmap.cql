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
MATCH (n:PublishedArticle) DETACH DELETE n;
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
OPTIONAL MATCH (a)-[:HasReview]->(review:Review {reviewed_by: rs.name})
WITH rs, a, review
OPTIONAL MATCH (a)-[:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: rs.name})
WITH rs, a, review, annot
WHERE 
  (review is NOT NULL OR annot IS NOT NULL)
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
  publisher_url: rs.url,
  publisher_name: TOLOWER(rs.name),
  publisher_peer_review_policy: rs.peer_review_policy,
  id: "https://eeb.embo.org/api/v2/docmap/" + doi,
  first_step: first_step
})
MERGE (docmap)<-[:steps]-(step:Step {id: first_step})
MERGE (step)<-[:inputs]-(preprint)
RETURN COUNT(docmap) AS `docmap generated`;
:commit

// RefereeReports
:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
  (docmap:Docmap {publisher_url: rs.url})<-[:steps]-(step:Step)<-[:inputs]-(preprint:Preprint)
OPTIONAL MATCH
  (a:Article {doi: preprint.doi})-[r:HasReview]->(review:Review {reviewed_by: rs.name})
WITH rs, docmap, step, preprint, review
OPTIONAL MATCH
  (a:Article {doi: preprint.doi})-[r:HasAnnot]->(annot:PeerReviewMaterial {reviewed_by: rs.name})
// use aggregation to coerce individual peer review material documents as review
WITH DISTINCT
  preprint.uri AS preprint_uri, preprint.doi AS doi, docmap, step, COLLECT(DISTINCT review) + COLLECT(DISTINCT annot) AS reviews
UNWIND reviews as review
WITH DISTINCT
  preprint_uri, doi, docmap, step, review
WITH 
  preprint_uri, 
  doi,
  docmap,
  step,
  review, "_:b-"+apoc.create.uuid() AS action_uuid,
  // filtering NULLs to prevent error in MERGE
  CASE WHEN review.link_html IS NOT NULL
    THEN review.link_html
    ELSE ""
  END AS link_html,
  CASE WHEN review.hypothesis_id IS NOT NULL
    THEN review.hypothesis_id
    ELSE ""
  END AS hypothesis_id
MERGE (step)<-[:assertions]-(assertion:Assertion {
  item: preprint_uri,
  status: "reviewed"
})
MERGE (step)<-[:actions]-(action:Action {id: action_uuid})
MERGE (action)<-[:outputs]-(rev:RefereeReport {
  published: review.posting_date,
  type: "review",
  uri: "https://eeb.embo.org/api/v2/review_material/" + id(review)
})
// review.doi can be null and must therefore be set outside the merge query
ON CREATE SET rev.doi = review.doi
// realization on eeb as json
MERGE (rev)<-[:content]-(content_on_eeb:Content {
  type: "web-page", 
  url: "https://eeb.embo.org/api/v2/review_material/" + id(review),
  id: toString(id(review)),
  service: "https://eeb.embo.org/"
})
// realization on hypothesis as HTML
MERGE (rev)<-[:content]-(content_on_hypothesis:Content {
  type: "web-page", 
  url: link_html,
  id: hypothesis_id,
  service: "https://hypothes.is/"
})
// realization on biorxiv in context of the preprint
MERGE (rev)<-[:content]-(content_incontext:Content {
  type: "web-page", 
  url: "https://biorxiv.org/content/" + doi + "#review",
  id: doi,
  service: "https://biorxiv.org"
})
WITH DISTINCT action, review
WHERE review.review_idx IS NOT NULL
MERGE (action)<-[:participants]-(reviewer:Person {
  id : "reviewer #" + review.review_idx,
  name: "anonymous",
  role: "peer-reviewer"
})
SET action.index = review.review_idx
RETURN DISTINCT COUNT(DISTINCT review) AS `reviews linked`;
:commit


// Reply
:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
  (docmap:Docmap {publisher_url: rs.url})<-[:steps]-(reviewing_step:Step)<-[:actions]-(:Action)<-[:outputs]-(review:RefereeReport),
  (reviewing_step)<-[:inputs]-(preprint:Preprint),
  (a:Article {doi: preprint.doi})-[:HasResponse]->(response:Response {reviewed_by: rs.name})
WITH DISTINCT
  preprint.uri AS preprint_uri, preprint.doi AS doi, docmap, reviewing_step, COLLECT(DISTINCT review) AS reviews, response
WITH
  preprint_uri, doi, docmap, reviewing_step, reviews, response, "_:b-"+apoc.create.uuid() as reply_step
SET reviewing_step.next_step = reply_step
MERGE (docmap)<-[:steps]-(step:Step {id: reply_step, previous_step: reviewing_step.id})
MERGE (step)<-[:assertions]-(assertion:Assertion {
  item: preprint_uri,
  status: "" // in the future: a value to the effect that "authors-replied-to-reviewers"
})
WITH DISTINCT doi, docmap, reviews, response, step
UNWIND reviews as review
WITH DISTINCT doi, docmap, review, response, step
MERGE (step)<-[:inputs]-(review)
WITH DISTINCT doi, docmap, response, step
WITH
  doi, 
  docmap,
  response,
  step,
  "_:b-"+apoc.create.uuid() AS action_uuid,
  CASE WHEN response.link_html IS NOT NULL
    THEN response.link_html
    ELSE ""
  END AS link_html,
  CASE WHEN response.hypothesis_id IS NOT NULL
    THEN response.hypothesis_id
    ELSE ""
  END AS hypothesis_id
MERGE (step)<-[:actions]-(action:Action {id: action_uuid})
MERGE (action)<-[:outputs]-(reply:AuthorReply {
  published: response.posting_date,
  type: "author-response",
  uri: "https://eeb.embo.org/api/v2/review_material/" + id(response)
})
// as above with reviews, response.doi can be null and must be set outside the merge query
ON CREATE SET reply.doi = response.doi
MERGE (reply)<-[:content]-(content:Content {
  type: "web-page",
  url: "https://eeb.embo.org/api/v2/review_material/" + id(response),
  id: toString(id(response)),
  service: "https://eeb.embo.org"
})
MERGE (reply)<-[:content]-(content_on_hypothesis:Content {
  type: "web-page", 
  url: link_html,
  id: hypothesis_id,
  service: "https://hypothes.is"
})
MERGE (reply)<-[:content]-(content_incontext:Content {
  type: "web-page", 
  url: "https://biorxiv.org/content/" + doi + "#review",
  id: doi,
  service: "https://biorxiv.org"
})
RETURN COUNT(DISTINCT response) AS `response linked`;
:commit


// Authors
:begin
MATCH (rs:ReviewingService)
WITH rs
MATCH
  (docmap:Docmap {publisher_url: rs.url})<-[:steps]-(replying_step:Step)<-[:actions]-(reply_action:Action)<-[:outputs]-(reply:AuthorReply),
  (docmap)<-[:steps]-(reviwing_step:Step)<-[:inputs]-(preprint:Preprint)
WITH DISTINCT docmap, preprint, reply_action
MATCH (a:Article {doi: preprint.doi})-[:has_author]->(author:Contrib)
OPTIONAL MATCH (author)-[:has_orcid]->(orcid:Contrib_id)
WITH DISTINCT
  reply_action, author, preprint,
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
MERGE (preprint)-[:has_author]->(person)
RETURN COUNT(person) AS `authors linked to replies`;
:commit

// Create Docmaps or add steps for published articles
:begin
MATCH
  (a:Article),
  (Docmap)<-[:steps]-(Step)<-[:inputs]-(preprint:Preprint)
WHERE
  // only update or create docmaps for preprints that have reviews/replies from one of the reviewing services.
  // If they do, a Docmap has been created above in the first step, and that is the one found here.
  a.doi = preprint.doi
  // these are fields needed to construct the new docmap.
  AND a.journal_doi IS NOT NULL
  AND a.published_journal_title IS NOT NULL
  AND a.publication_date IS NOT NULL
WITH DISTINCT
  preprint,
  a.publication_date as preprint_publication_date,
  a.journal_doi as published_article_doi,
  apoc.convert.toString(a.published_journal_title) as publisher_title
// order by and collect (below) to get the newest version
ORDER BY DATETIME(preprint_publication_date)
WITH DISTINCT
  preprint,
  COLLECT(preprint_publication_date)[0] as preprint_publication_date,
  published_article_doi,
  publisher_title,
  "_:b-"+apoc.create.uuid() as id_step,
  "_:b-"+apoc.create.uuid() AS id_action
MERGE (docmap:Docmap {
  type: "docmap",
  provider: "https://eeb.embo.org",
  publisher_name: TOLOWER(publisher_title),
  id: "https://eeb.embo.org/api/v2/docmap/" + preprint.doi
})
// if no docmap for this publisher exists, set the necessary properties
ON CREATE
  SET
    docmap.created = toString(DATETIME()),
    docmap.generatedAt = toString(DATETIME()),
    docmap.first_step = id_step
MERGE (docmap)<-[:steps]-(step:Step {id: id_step})
MERGE (step)<-[:inputs]-(preprint)
MERGE (step)<-[:assertions]-(assertion:Assertion {
  item: preprint.uri,
  status: "published"
})
MERGE (step)<-[:actions]-(action:Action {id: id_action})
MERGE (action)<-[:outputs]-(pub:PublishedArticle {
  doi: published_article_doi,
  type: "journal-publication",
  uri: "https://doi.org/" + published_article_doi
})
MERGE (rev)<-[:content]-(doi:Content {
  type: "web-page", 
  url: pub.uri,
  id: published_article_doi,
  service: "https://doi.org/"
})
// If we updated an existing docmap, add our newly added step as the next step after the so-far final step.
WITH
  COUNT(docmap) AS num_docmaps_updated_or_created,
  docmap,
  step AS new_step
OPTIONAL MATCH (docmap)<-[:steps]-(existing_step:Step)
WHERE
  ID(existing_step) <> ID(new_step)
  AND existing_step.next_step IS NULL
SET existing_step.next_step = new_step.id
RETURN num_docmaps_updated_or_created AS `docmap generated or updated with publication`;
:commit

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

//try 
// :POST /rdf/neo4j/cypher
// {"cypher": "MATCH path=(preprint:Preprint)-[:inputs]->(action1:Action)<-[:outputs]-(ref:RefereeReport)-[:inputs]->(actions2:Action)<-[:outputs]-(reply:AuthorReply), (docmap)<-[:actions]-(action_1) RETURN path LIMIT 1", "format": "JSON-LD"}