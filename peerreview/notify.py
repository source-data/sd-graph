from argparse import ArgumentParser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment
from smtplib import SMTP, SMTPException
from ssl import SSLContext

import common.logging
from peerreview.queries import REFEREED_PREPRINTS_POSTED_AFTER
from . import DB, SMTP_HOST, SMTP_STARTTLS_PORT, SMTP_PASSWORD, SMTP_USERNAME

LOGGER = common.logging.get_logger(__name__)

FROM = "reviewcommons-updates@embl.de"
TO = "reviewcommons-updates@embl.de"

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
    <b>Peer reviews:</b>
    <ol>
        {%- for review in reviews %}
        <li>
            <pre style="white-space: pre-wrap;">{{ review }}</pre>
        </li>
        {% endfor -%}
    </ol>
{% if author_response %}

<p>
    <b>Author response:</b>
    <pre style="white-space: pre-wrap;">{{ author_response }}</pre>
{% endif %}
"""


def limit(text, length):
    text = text.strip()
    text_length = len(text)
    if text_length <= length:
        return text
    ellipsis = " [...]"
    return text[: length - len(ellipsis)] + ellipsis


class Notify:
    def __init__(self, db):
        self.db = db

    def create_message(self, preprint):
        title = preprint["title"]
        doi = preprint["doi"]
        review_process = preprint["review_process"]
        response = review_process["response"]

        len_review_preamble = 203
        len_response_preamble = 204
        max_text_length = 10 ** 6

        body_template = Environment(autoescape=True).from_string(template)
        body = body_template.render(
            eeb_link=f"https://eeb.embo.org/doi/{doi}",
            title=title,
            authors=reversed(
                sorted(preprint["authors"], key=lambda a: a["position_idx"])
            ),
            abstract=preprint["abstract"],
            doi=doi,
            reviews=[
                limit(review["text"][len_review_preamble:], max_text_length)
                for review in sorted(
                    review_process["reviews"], key=lambda r: r["review_idx"]
                )
            ],
            author_response=f'{limit(response["text"][len_response_preamble:], max_text_length)}'
            if response
            else None,
        )
        subject = f"New refereed preprint: {title}"

        return subject, body

    def send_mails(self, preprints, dry_run):
        messages = []
        for preprint in preprints:
            subject, body = self.create_message(preprint)
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = FROM
            msg["To"] = TO
            msg.attach(MIMEText(body, "html"))
            messages.append(msg)

        if dry_run:
            linebreak = """
"""
            LOGGER.info(
                "This is a dry run, these messages would be sent: %s",
                linebreak.join([limit(msg.as_string(), 500) for msg in messages]),
            )
            return

        try:
            with SMTP(SMTP_HOST, SMTP_STARTTLS_PORT) as server:
                server.starttls(context=SSLContext())
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                for msg in messages:
                    server.sendmail(FROM, TO, msg.as_string())
        except SMTPException as e:
            LOGGER.exception(e)

    def run(self, after: datetime, reviewed_by: str, dry_run: bool = False):
        query = REFEREED_PREPRINTS_POSTED_AFTER(
            params={"after": after, "reviewed_by": reviewed_by}
        )
        refereed_preprints = self.db.query(query)
        if refereed_preprints:
            LOGGER.info(
                f"Notifying {TO} about {len(refereed_preprints)} new preprints refereed by {reviewed_by} since {after}"
            )
            self.send_mails(refereed_preprints, dry_run)
        else:
            LOGGER.info(f"No new preprints refereed by {reviewed_by} since {after}")


def main():
    parser = ArgumentParser(
        description="""Send email notifications about (newly) posted refereed preprints."""
    )
    parser.add_argument(
        "--after",
        help="Only send notifications about preprints with reviews posted after this date. Required. Use an ISO8601 date/time format (2022-01-01, 2022-08-01T16:13:55+02:00, etc).",
        required=True,
    )
    parser.add_argument(
        "--reviewed-by",
        help="Only send notifications about preprints reviewed by this service. Required.",
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
    dry_run = not args.no_dry_run
    Notify(DB).run(after, reviewed_by, dry_run=dry_run)


if __name__ == "__main__":
    common.logging.configure_logging()
    main()
