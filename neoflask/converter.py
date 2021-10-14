"""
Custom converters for the flask router.
"""
import re
from werkzeug.routing import BaseConverter


class LuceneQueryConverter(BaseConverter):
    """
    Quotes and unquote Lucene search strings.
    """

    def to_python(self, text: str) -> str:
        """
        Quotes lucene special characters.
        """
        quoted = re.sub(r'([\+\-!\(\)\{\}\[\]\^\"~\*\?\:\\/&\|])', r'"\1"', text)
        return quoted

    def to_url(self, text: str):
        """
        Remove quotes added to escape lucene special characters.
        """
        unquoted = re.sub(r'"([\+\-!\(\)\{\}\[\]\^\"~\*\?\:\\/&\|])"', r'\1', text)
        return super().to_url(unquoted)

class ReviewServiceConverter(BaseConverter):
    """
    Maps review service names provided as parameter in the url with their internal names used in the database.
    """

    review_services = {
        'reviewcommons': 'review commons',
        'review commons': 'review commons',
        'elife': 'elife',
        'embopress': 'embo press',
        'embo press': 'embo press',
        'rrc19': 'MIT Press - Journals',
        'mit press - journals': 'MIT Press - Journals',
        'pci': 'Peer Community In',
        'peer community in': 'Peer Community In',
        'peerageofscience': 'peerage of science',
        'peerage of science': 'peerage of science',
    }

    def to_python(self, text: str) -> str:
        """
        Returns the internal review service name.
        """
        review_service_name = self.review_services[text.lower()]
        return review_service_name
