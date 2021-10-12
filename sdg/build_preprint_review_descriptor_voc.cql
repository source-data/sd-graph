MATCH (t:PreprintReviewDescriptor) DETACH DELETE t;
MATCH (f:PRDField) DETACH DELETE f;
MATCH (v:PRDVal) DETACH DELETE v;


CREATE CONSTRAINT unique_prd_value IF NOT EXISTS ON (v:PRDVal) ASSERT v.prd_id IS UNIQUE;

MERGE
    (t:PreprintReviewDescriptor {
        version: "1.0.0",
        source: "https://asapbio.org/developing-a-taxonomy-to-describe-preprint-review-processes"
    })
WITH t
MERGE
  (t)-[:child]->(review_requested_by:PRDField {
      name: "Review requested by",
      key: "review_requested_by",
      help: "Who submits or initiates the feedback process?",
      prd_id: 1
      })
MERGE 
    (t)-[:child]->(review_selected_by:PRDField {
      name: "Reviewer selected by",
      key: "reviewer_selected_by",
      help: "Who selects the feedback providers?",
      prd_id: 2
      })
MERGE
  (t)-[:child]->(review_coverage:PRDField {
      name: "Review coverage",
      key: "review_coverage",
      help: "Does the feedback cover the entire paper or only a certain section or aspect?",
      prd_id: 3
      })
MERGE
  (t)-[:child]->(reviewer_identity_known_to:PRDField {
      name: "Reviewer identity known to",
      key: "reviewer_identity_known_to",
      help: "Are the identities of reviewers known to everyone (public), editors or service, or noone?",
      prd_id: 4
      })
MERGE
  (t)-[:child]->(competing_interests:PRDField {
      name: "Competing interests",
      key: "competing_interests",
      help: "Is a declaration of competing interest required?",
      prd_id: 5
      })
MERGE
  (t)-[:child]->(public_interaction:PRDField {
      name: "Public interaction",
      key: "public_interaction",
      help: "Is there an opportunity for the public to engage as an integral part of the process?",
      prd_id: 6
      })
MERGE
  (t)-[:child]->(opportunity_for_author_response:PRDField {
      name: "Opportunity for author response",
      key: "opportunity_for_author_response",
      help: "Is the author’s response included as an integral part of the process?",
      prd_id: 7
      })
MERGE
  (t)-[:child]->(recommendation:PRDField {
      name: "Recommendation",
      key: "recommendation",
      help: "Does the service provide a binary decision (accept/reject or recommendation) or a scalar rating after the review process?",
      prd_id: 8
      })
WITH
    t,
    review_requested_by,
    review_selected_by,
    review_coverage,
    reviewer_identity_known_to,
    competing_interests,
    public_interaction,
    opportunity_for_author_response,
    recommendation
MERGE
    (review_requested_by)-[:child]->(review_requested_by_authors:PRDVal {
        value: "Authors",
        prd_id: 9
    })
MERGE
    (review_requested_by)-[:child]->(review_requested_by_non_authors:PRDVal {
        value: "Non-authors",
        prd_id: 10
    })
MERGE

    (review_selected_by)-[:child]->(review_selected_by_authors:PRDVal {
        value: "Authors",
        prd_id: 11
    })
MERGE
    (review_selected_by)-[:child]->(review_selected_by_service:PRDVal {
        value: "Editor, service, or community",
        prd_id: 12
    })
MERGE
    (review_selected_by)-[:child]->(review_selected_by_self:PRDVal {
        value: "Self-nominated",
        prd_id: 13
    })
MERGE

    (review_coverage)-[:child]->(review_coverage_full_paper:PRDVal {
        value: "Full paper",
        prd_id: 14
    })
MERGE
    (review_coverage)-[:child]->(review_coverage_specific:PRDVal {
        value: "Specific aspects",
        prd_id: 15
    })
MERGE

    (reviewer_identity_known_to)-[:child]->(reviewer_identity_known_to_public:PRDVal {
        value: "Public",
        prd_id: 16
    })
MERGE
    (reviewer_identity_known_to)-[:child]->(reviewer_identity_known_to_editor:PRDVal {
        value: "Editor or service",
        prd_id: 17
    })
MERGE
    (reviewer_identity_known_to)-[:child]->(reviewer_identity_known_to_none:PRDVal {
        value: "No one",
        prd_id: 18
    })
MERGE


    (competing_interests)-[:child]->(competing_interests_displayed:PRDVal {
        value: "Displayed",
        prd_id: 19
    })
MERGE
    (competing_interests)-[:child]->(competing_interests_checked:PRDVal {
        value: "Checked",
        prd_id: 20
    })
MERGE
    (competing_interests)-[:child]->(competing_interests_not_included:PRDVal {
        value: "Not included",
        prd_id: 21
    })
MERGE


    (public_interaction)-[:child]->(public_interaction_included:PRDVal {
        value: "Included",
        prd_id: 22
    })
MERGE
    (public_interaction)-[:child]->(public_interaction_not_included:PRDVal {
        value: "Not included",
        prd_id: 23
    })
MERGE

    (opportunity_for_author_response)-[:child]->(opportunity_for_author_response_included:PRDVal {
        value: "Included",
        prd_id: 24
    })
MERGE
    (opportunity_for_author_response)-[:child]->(opportunity_for_author_response_not_included:PRDVal {
        value: "Not included",
        prd_id: 25
    })
MERGE


    (recommendation)-[:child]->(recommendation_binary_decision:PRDVal {
        value: "Binary decision",
        prd_id: 26
    })
MERGE
    (recommendation)-[:child]->(recommendation_scale:PRDVal {
        value: "Other scale or rating",
        prd_id: 27
    })
MERGE
    (recommendation)-[:child]->(recommendation_none:PRDVal {
        value: "None",
        prd_id: 28
    })

RETURN
    t,
    review_requested_by,
    review_selected_by,
    review_coverage,
    reviewer_identity_known_to,
    competing_interests,
    public_interaction,
    opportunity_for_author_response,
    recommendation,
    review_requested_by_authors,
    review_requested_by_non_authors,
    review_selected_by_authors,
    review_selected_by_service,
    review_selected_by_self,
    review_coverage_full_paper,
    review_coverage_specific,
    reviewer_identity_known_to_public,
    reviewer_identity_known_to_editor,
    reviewer_identity_known_to_none,
    competing_interests_displayed,
    competing_interests_checked,
    competing_interests_not_included,
    public_interaction_included,
    public_interaction_not_included,
    opportunity_for_author_response_included,
    opportunity_for_author_response_not_included,
    recommendation_binary_decision,
    recommendation_scale,
    recommendation_none;
