MATCH (h:UpdateStatus)
SET h.update_started = toString(DATETIME())