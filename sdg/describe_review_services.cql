// Describe reviewing services
MERGE (r:ReviewingService {
    name: "review commons",
    url: "https://reviewcommons.org",
    peer_review_policy: "https://reviewcommons.org/reviewers",
    author_driven_submissions: true,
    post_review_decision: false,
    pre_review_triage: true
});
MERGE (r:ReviewingService {
    name: "elife",
    url: "https://elifesciences.org",
    peer_review_policy: "https://elifesciences.org/about/peer-review",
    author_driven_submissions: true,
    post_review_decision: true,
    pre_review_triage: true
});
MERGE (r:ReviewingService {
    name: "Peer Community In",
    url: "https://peercommunityin.org",
    peer_review_policy: "https://peercommunityin.org/how-does-it-work-2/",
    author_driven_submissions: true,
    post_review_decision: true,
    pre_review_triage: true
});
MERGE (r:ReviewingService {
    name: "MIT Press - Journals",
    url: "https://rapidreviewscovid19.mitpress.mit.edu/",
    peer_review_policy: "https://rapidreviewscovid19.mitpress.mit.edu/guidelines",
    author_driven_submissions: false,
    post_review_decision: true,
    pre_review_triage: true
});
MERGE (r:ReviewingService {
    name: "embo press",
    url: "https://embopress.org/",
    peer_review_policy: "https://www.embopress.org/page/journal/17444292/refereeguide",
    author_driven_submissions: true,
    post_review_decision: true,
    pre_review_triage: true
});
MERGE (r:ReviewingService {
    name: "peerage of science",
    url: "https://www.peerageofscience.org/",
    peer_review_policy: "",
    author_driven_submissions: true,
    post_review_decision: true,
    pre_review_triage: false
});