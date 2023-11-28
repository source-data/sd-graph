import connexion
import six

from swagger_server.models.reviewing_service_collection import ReviewingServiceCollection  # noqa: E501
from swagger_server import util


def reviewing_services_get():  # noqa: E501
    """Get information about available reviewing services

     # noqa: E501


    :rtype: ReviewingServiceCollection
    """
    return [
      {
        "id": "embo press",
        "reviewing_service_description": {
          "peer_review_policy": "https://www.embopress.org/page/journal/17444292/refereeguide",
          "name": "embo press",
          "competing_interests": "Checked",
          "opportunity_for_author_response": "Included",
          "reviewer_selected_by": "Editor, service, or community",
          "recommendation": "Binary decision",
          "public_interaction": "Not included",
          "review_coverage": "Full paper",
          "review_requested_by": "Authors",
          "url": "https://embopress.org/",
          "reviewer_identity_known_to": "Editor or service"
        }
      },
      {
        "id": "elife",
        "reviewing_service_description": {
          "peer_review_policy": "https://elifesciences.org/about/peer-review",
          "name": "elife",
          "competing_interests": "Checked",
          "opportunity_for_author_response": "Included",
          "reviewer_selected_by": "Editor, service, or community",
          "recommendation": "Binary decision",
          "public_interaction": "Not included",
          "review_coverage": "Full paper",
          "review_requested_by": "Authors",
          "url": "https://elifesciences.org",
          "reviewer_identity_known_to": "Editor or service"
        }
      },
      {
        "id": "MIT Press - Journals",
        "reviewing_service_description": {
          "peer_review_policy": "https://rapidreviewscovid19.mitpress.mit.edu/guidelines",
          "name": "MIT Press - Journals",
          "competing_interests": "Checked",
          "opportunity_for_author_response": "Not included",
          "reviewer_selected_by": "Editor, service, or community",
          "recommendation": "Scale or rating",
          "public_interaction": "Not included",
          "review_coverage": "Full paper",
          "review_requested_by": "Non-authors",
          "url": "https://rapidreviewscovid19.mitpress.mit.edu/",
          "reviewer_identity_known_to": "Public"
        }
      },
      {
        "id": "review commons",
        "reviewing_service_description": {
          "peer_review_policy": "https://reviewcommons.org/reviewers",
          "name": "review commons",
          "competing_interests": "Checked",
          "opportunity_for_author_response": "Included",
          "reviewer_selected_by": "Editor, service, or community",
          "recommendation": "None",
          "public_interaction": "Not included",
          "review_coverage": "Full paper",
          "review_requested_by": "Authors",
          "url": "https://reviewcommons.org",
          "reviewer_identity_known_to": "Editor or service"
        }
      },
      {
        "id": "peer ref",
        "reviewing_service_description": {
          "peer_review_policy": "https://www.peerref.com/reviewer-guidelines",
          "name": "peer ref",
          "competing_interests": "Checked",
          "opportunity_for_author_response": "Included",
          "reviewer_selected_by": "Editor, service, or community",
          "recommendation": "Binary decision",
          "public_interaction": "Not included",
          "review_coverage": "Full paper",
          "review_requested_by": "Authors",
          "url": "https://peerref.com/",
          "reviewer_identity_known_to": "Public"
        }
      },
      {
        "id": "peerage of science",
        "reviewing_service_description": {
          "peer_review_policy": "",
          "name": "peerage of science",
          "competing_interests": "Checked",
          "opportunity_for_author_response": "Not included",
          "reviewer_selected_by": "Self-nominated",
          "recommendation": "Binary decision",
          "public_interaction": "Not included",
          "review_coverage": "Full paper",
          "review_requested_by": "Authors",
          "url": "https://www.peerageofscience.org/",
          "reviewer_identity_known_to": "Editor or service"
        }
      },
      {
        "id": "Peer Community In",
        "reviewing_service_description": {
          "peer_review_policy": "https://peercommunityin.org/how-does-it-work-2/",
          "name": "Peer Community In",
          "competing_interests": "Checked",
          "opportunity_for_author_response": "Included",
          "reviewer_selected_by": "Editor, service, or community",
          "recommendation": "Binary decision",
          "public_interaction": "Not included",
          "review_coverage": "Full paper",
          "review_requested_by": "Authors",
          "url": "https://peercommunityin.org",
          "reviewer_identity_known_to": "Editor or service"
        }
      }
    ]
