// purge
MATCH (r:ReviewingService) DETACH DELETE r;


// Describe reviewing services
CREATE (review_commons:ReviewingService {
    name: "review commons",
    url: "https://reviewcommons.org",
    peer_review_policy: "https://reviewcommons.org/reviewers"
})
CREATE (elife:ReviewingService {
    name: "elife",
    url: "https://elifesciences.org",
    peer_review_policy: "https://elifesciences.org/about/peer-review"
})
CREATE (pci:ReviewingService {
    name: "Peer Community In",
    url: "https://peercommunityin.org",
    peer_review_policy: "https://peercommunityin.org/how-does-it-work-2/"
})
CREATE (rrc19:ReviewingService {
    name: "MIT Press - Journals",
    url: "https://rapidreviewscovid19.mitpress.mit.edu/",
    peer_review_policy: "https://rapidreviewscovid19.mitpress.mit.edu/guidelines"
})
CREATE (embo_press:ReviewingService {
    name: "embo press",
    url: "https://embopress.org/",
    peer_review_policy: "https://www.embopress.org/page/journal/17444292/refereeguide"
})
CREATE (peerage_of_science:ReviewingService {
    name: "peerage of science",
    url: "https://www.peerageofscience.org/",
    peer_review_policy: NULL
})

RETURN
    review_commons,
    elife,
    pci,
    rrc19,
    embo_press,
    peerage_of_science;

// link to preprint peer review descriptor
WITH [
    {
        service_name: "review commons",
        review_requested_by: "Authors",
        reviewer_selected_by: "Editor, service, or community",
        review_coverage: "Full paper",
        reviewer_identity_known_to: "Editor or service",
        competing_interests: "Checked",
        public_interaction: "Not included",
        opportunity_for_author_response: "Included",
        recommendation: "None"
    },
    {
        service_name: "elife",
        review_requested_by: "Authors",
        reviewer_selected_by: "Editor, service, or community",
        review_coverage: "Full paper",
        reviewer_identity_known_to: "Editor or service",
        competing_interests: "Checked",
        public_interaction: "Not included",
        opportunity_for_author_response: "Included",
        recommendation: "Binary decision"
    },
    {
        service_name: "embo press",
        review_requested_by: "Authors",
        reviewer_selected_by: "Editor, service, or community",
        review_coverage: "Full paper",
        reviewer_identity_known_to: "Editor or service",
        competing_interests: "Checked",
        public_interaction: "Not included",
        opportunity_for_author_response: "Included",
        recommendation: "Binary decision"
    },
    {
        service_name: "MIT Press - Journals",
        review_requested_by: "Non-authors",
        reviewer_selected_by: "Editor, service, or community",
        review_coverage: "Full paper",
        reviewer_identity_known_to: "Public",
        competing_interests: "Checked",
        public_interaction: "Not included",
        opportunity_for_author_response: "Not included",
        recommendation: "Scale or rating"
    },
    {
        service_name: "Peer Community In",
        review_requested_by: "Authors",
        reviewer_selected_by: "Editor, service, or community",
        review_coverage: "Full paper",
        reviewer_identity_known_to: "Editor or service",
        competing_interests: "Checked",
        public_interaction: "Not included",
        opportunity_for_author_response: "Included",
        recommendation: "Binary decision"
    },
    {
        service_name: "peerage of science",
        review_requested_by: "Authors",
        reviewer_selected_by: "Self-nominated",
        review_coverage: "Full paper",
        reviewer_identity_known_to: "Editor or service",
        competing_interests: "Checked",
        public_interaction: "Not included",
        opportunity_for_author_response: "Not included",
        recommendation: "Binary decision"
    }
] AS descriptors
UNWIND descriptors AS descriptor
MATCH
    (rev_service:ReviewingService {name: descriptor.service_name}),
    (t:PreprintReviewDescriptor),
    (t)-->(f1:PRDField {key: "review_requested_by"})-->(v1:PRDVal {value: descriptor.review_requested_by}),
    (t)-->(f2:PRDField {key: "reviewer_selected_by"})-->(v2:PRDVal {value: descriptor.reviewer_selected_by}),
    (t)-->(f3:PRDField {key: "review_coverage"})-->(v3:PRDVal {value: descriptor.review_coverage}),
    (t)-->(f4:PRDField {key: "reviewer_identity_known_to"})-->(v4:PRDVal {value: descriptor.reviewer_identity_known_to}),
    (t)-->(f5:PRDField {key: "competing_interests"})-->(v5:PRDVal {value: descriptor.competing_interests}),
    (t)-->(f6:PRDField {key: "public_interaction"})-->(v6:PRDVal {value: descriptor.public_interaction}),
    (t)-->(f7:PRDField {key: "opportunity_for_author_response"})-->(v7:PRDVal {value: descriptor.opportunity_for_author_response}),
    (t)-->(f8:PRDField {key: "recommendation"})-->(v8:PRDVal {value: descriptor.recommendation})
MERGE (rev_service)-[:review_requested_by]->(v1)
MERGE (rev_service)-[:reviewer_selected_by]->(v2)
MERGE (rev_service)-[:review_coverage]->(v3)
MERGE (rev_service)-[:reviewer_identity_known_to]->(v4)
MERGE (rev_service)-[:competing_interests]->(v5)
MERGE (rev_service)-[:public_interaction]->(v6)
MERGE (rev_service)-[:opportunity_for_author_response]->(v7)
MERGE (rev_service)-[:recommendation]->(v8)
RETURN
    rev_service,
    f1, f2, f3, f4, f5, f6, f7, f8,
    v1, v2, v3, v4, v5, v6, v7, v8;
