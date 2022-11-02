from argparse import ArgumentParser
from datetime import datetime
from dateutil.parser import parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment
from smtplib import SMTP, SMTPException
from ssl import SSLContext

import common.logging
from neoflask.queries import BY_DOIS
from peerreview.queries import REFEREED_PREPRINTS_POSTED_AFTER
from . import DB, SMTP_HOST, SMTP_STARTTLS_PORT, SMTP_PASSWORD, SMTP_USERNAME

LOGGER = common.logging.get_logger(__name__)

FROM = "reviewcommons-updates@embl.de"

template = """New Review Commons refereed preprint posted:

<p>
    <a href="{{ eeb_link }}">{{ eeb_link }}</a>

<p>
    <b>Title:</b>
    {{ title }}

<p>
    <b>Authors:</b>
    {% for author in authors -%}
        {%- if author.orcid -%}
            <a href="{{ author.orcid }}">
        {%- endif -%}
        {{ author.surname }} {{ author.given_names }}
        {%- if author.orcid -%}
            </a>
        {%- endif -%}
        {%- if author.corresp == "yes" -%}*{%- endif -%}
        {%- if not loop.last %}, {% endif -%}
    {%- endfor %}

<p>
    <b>Abstract:</b>
    {{ abstract }}

<p>
    <b>DOI:</b>
    <a href="https://doi.org/{{ doi }}">{{ doi }}</a>

<p>
    <b>Peer reviews</b> (
    {%- if review_process_dates.earliest == review_process_dates.latest -%}
        published on {{ review_process_dates.earliest }}
    {%- else -%}
        published between {{ review_process_dates.earliest }} and {{ review_process_dates.latest }}
    {%- endif -%}
    ):
    <ol>
        {%- for review in reviews %}
        <li>
            <pre style="white-space: pre-wrap;">{{ review }}</pre>
        </li>
        {% endfor -%}
    </ol>
{% if author_response %}

<p>
    <b>Author response</b> (published on {{ review_process_dates.response }}):
    <pre style="white-space: pre-wrap;">{{ author_response }}</pre>
{% endif %}
"""


def _limit(text, prefix_length, max_length, ellipsis):
    """
    Strips `text` of the first `prefix_length` characters and truncates the remainder to `max_length`.

    `ellipsis` is added to the truncated string to indicate that parts were removed (e.g. "[...]").
    The length of the returned string including `ellipsis` is `max_length`.
    
    After removing the prefix, any trailing whitespace is stripped.
    Therefore, more characters than `prefix_length` may be removed.
    """
    assert text is not None
    assert len(text) > prefix_length

    ellipsis_length = len(ellipsis)
    assert max_length > ellipsis_length

    stripped_text = text[prefix_length:].strip()
    if len(stripped_text) <= max_length:
        return stripped_text

    return stripped_text[: max_length - len(ellipsis)] + ellipsis


def _parse_date(date_string):
    return parse(date_string).date()

class Notify:
    def __init__(self, db):
        self.db = db
        self.max_text_length = 10 ** 6
        self.len_review_preamble = 203
        self.len_response_preamble = 204
        self.ellipsis = " [...]"

    def create_message(self, preprint):
        title = preprint["title"]
        doi = preprint["doi"]
        review_process = preprint["review_process"]

        reviews = review_process["reviews"]
        review_texts = [
            _limit(review["text"], self.len_review_preamble, self.max_text_length, self.ellipsis)
            for review in sorted(
                reviews, key=lambda r: r["review_idx"]
            )
        ]
        review_posting_dates = sorted([_parse_date(review["posting_date"]) for review in reviews])
        review_process_dates = {
            "earliest": review_posting_dates[0],
            "latest": review_posting_dates[-1],
        }

        response = review_process["response"]
        if response:
            review_process_dates["response"] = _parse_date(response["posting_date"])
            response_text = _limit(response["text"], self.len_response_preamble, self.max_text_length, self.ellipsis)
        else:
            response_text = None

        body_template = Environment(autoescape=True).from_string(template)
        body = body_template.render(
            eeb_link=f"https://eeb.embo.org/doi/{doi}",
            title=title,
            authors=reversed(
                sorted(preprint["authors"], key=lambda a: a["position_idx"])
            ),
            abstract=preprint["abstract"],
            doi=doi,
            review_process_dates=review_process_dates,
            reviews=review_texts,
            author_response=response_text,
        )
        subject = f"New refereed preprint: {title}"

        return subject, body

    def send_mails(self, preprints, recipient, dry_run):
        messages = []
        for preprint in preprints:
            subject, body = self.create_message(preprint)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = FROM
            msg["To"] = recipient
            msg.attach(MIMEText(body, "html"))
            messages.append(msg)

        if dry_run:
            linebreak = """
"""
            LOGGER.info(
                "This is a dry run, these messages would be sent: %s",
                linebreak.join([_limit(msg.as_string(), 500) for msg in messages]),
            )
            return

        try:
            with SMTP(SMTP_HOST, SMTP_STARTTLS_PORT) as server:
                server.starttls(context=SSLContext())
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                for msg in messages:
                    server.sendmail(FROM, recipient, msg.as_string())
        except SMTPException as e:
            LOGGER.exception(e)

    def find_refereed_preprints(self, after: datetime, reviewed_by: str):
        query = REFEREED_PREPRINTS_POSTED_AFTER(
            params={"after": after, "reviewed_by": reviewed_by}
        )
        dois_of_matching_refereed_preprints = [r["doi"] for r in self.db.query(query)]
        return self.db.query(BY_DOIS(params={"dois": dois_of_matching_refereed_preprints}))

    def run(self, after: datetime, reviewed_by: str, recipient: str, dry_run: bool = False):
        refereed_preprints = self.find_refereed_preprints(after, reviewed_by)
        if refereed_preprints:
            LOGGER.info(
                f"Notifying {recipient} about {len(refereed_preprints)} new preprints refereed by {reviewed_by} since {after}"
            )
            self.send_mails(refereed_preprints, recipient, dry_run)
        else:
            LOGGER.info(f"No new preprints refereed by {reviewed_by} since {after}")


def main():
    parser = ArgumentParser(
        description="""Send email notifications about (newly) published refereed preprints."""
    )
    parser.add_argument(
        "--after",
        help="Only send notifications about preprints with reviews published after this date. Required. Use an ISO8601 date/time format (2022-01-01, 2022-08-01T16:13:55+02:00, etc).",
        required=True,
    )
    parser.add_argument(
        "--reviewed-by",
        help="Only send notifications about preprints reviewed by this service. Required.",
        required=True,
    )
    parser.add_argument(
        "--recipient",
        help="Send notifications to this email address. Required.",
        required=True,
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually send emails. Without this flag, the messages that would be sent are only logged.",
    )
    args = parser.parse_args()
    after = args.after
    reviewed_by = args.reviewed_by
    recipient = args.recipient
    dry_run = not args.no_dry_run
    Notify(DB).run(after, reviewed_by, recipient, dry_run=dry_run)


if __name__ == "__main__":
    common.logging.configure_logging()
    main()
