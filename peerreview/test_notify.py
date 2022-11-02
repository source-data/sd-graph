from unittest.mock import MagicMock
from peerreview.notify import Notify
from pytest import fixture


@fixture
def db_mock():
    return MagicMock()

@fixture
def notify_object(db_mock):
    return Notify(db_mock)

@fixture
def preprint_fixture(notify_object):
    response_prefix = " " * notify_object.len_response_preamble
    review_prefix = " " * notify_object.len_review_preamble
    preprint = {
        "authors": [
            {
                "given_names": "Jane",
                "position_idx": 0,
                "surname": "Doe",
            }
        ],
        "abstract": "Abstract of the preprint",
        "title": "Title of the preprint",
        "doi": "10.1234/567890",
        "review_process": {
            "reviews": [
                {
                    "posting_date": "2022-08-01T16:13:55+02:00",
                    "review_idx": "1",
                    "text": review_prefix + "The text of the review",
                },
            ],
            "response": None,
        },
    }
    return (preprint, review_prefix, response_prefix)

def test_create_message_with_response(notify_object, preprint_fixture):
    preprint, review_prefix, response_prefix = preprint_fixture
    
    response = {
        "posting_date": "2022-08-01T16:13:55+02:00",
        "text": response_prefix + "The text of the response",
    }
    preprint["review_process"]["response"] = response

    actual_subject, actual_message = notify_object.create_message(preprint)

    verify_message_content(preprint, review_prefix, actual_subject, actual_message)

    assert response["posting_date"][:10] in actual_message, "A response's posting date must be in the message body"
    assert response["text"][len(response_prefix):] in actual_message, "A response's full text must be in the message body"

def test_create_message_without_response(notify_object, preprint_fixture):
    preprint, review_prefix, _ = preprint_fixture
    preprint["response"] = None

    actual_subject, actual_message = notify_object.create_message(preprint)

    verify_message_content(preprint, review_prefix, actual_subject, actual_message)

def test_create_message_with_long_text(notify_object, preprint_fixture):
    preprint, review_prefix, _ = preprint_fixture

    notify_object.max_text_length = 10
    notify_object.ellipsis = ""
    review_text = preprint["review_process"]["reviews"][0]["text"][len(review_prefix):]
    expected_review_text = review_text[:notify_object.max_text_length]

    _, actual_message = notify_object.create_message(preprint)

    assert review_text not in actual_message, "A review's full text that is too long must not be in the message body in full"
    assert expected_review_text in actual_message, "A review's full text that is too long must be in the message body in a truncated version"

def verify_message_content(preprint, review_prefix, subject, body):
    assert preprint["title"] in subject, "The title must be in the message subject"

    assert preprint["abstract"] in body, "The abstract must be in the message body"
    assert preprint["doi"] in body, "The DOI must be in the message body"
    assert preprint["title"] in body, "The title must be in the message body"

    for author in preprint["authors"]:
        assert author["surname"] in body, "All authors' surnames must be in the message body"
        assert author["given_names"] in body, "All authors' given names must be in the message body"

    for review in preprint["review_process"]["reviews"]:
        assert review["posting_date"][:10] in body, "All reviews' posting dates must be in the message body"
        assert review["text"][len(review_prefix):] in body, "All reviews' full texts must be in the message body"