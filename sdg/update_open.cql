MERGE (h:UpdateStatus)
SET
  h.update_started = toString(DATETIME()),
  h.old_total_nodes = h.current_total_nodes,
  h.current_total_nodes = NULL,
  h.old_num_preprints = h.current_num_preprints,
  h.current_num_preprints = NULL,
  h.old_num_refereed_preprints = h.current_num_refereed_preprints,
  h.current_num_refereed_preprints = NULL,
  h.old_num_autoannotated_preprints = h.current_num_autoannotated_preprints,
  h.current_num_autoannotated_preprints = NULL,
  h.current_num_reviews = h.current_num_reviews,
  h.current_num_reviews = h.current_num_reviews = NULL,
  h.old_num_docmaps = h.current_num_docmaps,
  h.current_num_docmaps = NULL
RETURN h.update_started as `update start time`;