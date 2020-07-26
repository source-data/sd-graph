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
