MATCH (a:Article)
WHERE toLower(a.journal_title) IN ["biorxiv", "medrxiv"]
WITH COUNT(DISTINCT a.doi) AS num_preprints
MATCH (:VizCollection {name: "refereed-preprints"})-[:HasSubCol]->(:VizSubCollection)-[:HasPaper]->(a:VizPaper)
WITH COUNT(DISTINCT a.doi) AS num_refereed_preprints, num_preprints
MATCH (a:SDArticle {source: "eebapi"})
WITH COUNT(DISTINCT a.doi) AS num_autoannotated_preprints, num_refereed_preprints, num_preprints
MATCH (n)
WITH COUNT(n) AS total_nodes, num_autoannotated_preprints, num_refereed_preprints, num_preprints
MATCH (h:UpdateStatus)
SET
  h.current_total_nodes = total_nodes,
  h.current_num_preprints = num_preprints,
  h.current_num_refereed_preprints = num_refereed_preprints,
  h.current_num_autoannotated_preprints = num_autoannotated_preprints,
  h.update_completed = toString(DATETIME());
RETURN h.update_completed as `time of update completion`;