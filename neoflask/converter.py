"""
Custom converters for the flask router.
"""
import re
from werkzeug.routing import BaseConverter


class ListConverter(BaseConverter):

    def to_python(self, value):
        return value.split(',')

    def to_url(self, values):
        return ','.join(BaseConverter.to_url(value) for value in values)


class LuceneQueryConverter(BaseConverter):
    """
    Quotes and unquote Lucene search strings.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        lucene_special_chars = r'+-&|!(){}[]^"~*?:\\'
        self.pattern = re.compile(
            f"""# verbose regex, ignores whitespace during compilation
            (   # Capturing group #1

                # Match any of the lucene special characters exactly once. The chars
                # contain many regex special chars which need to be escaped.
                [{re.escape(lucene_special_chars)}] # Whitespace isn't ignored in [character clauses]
            )
            """,
            re.VERBOSE
        )


    def to_python(self, text: str) -> str:
        """
        Escapes lucene special characters.

        Here's what Lucene says needs to be escaped: `+ - && || ! ( ) { } [ ] ^ " ~ * ? : \`
        From https://lucene.apache.org/core/2_9_4/queryparsersyntax.html#Escaping%20Special%20Characters

        It's not clear whether && (and ||) should be escaped as \&& or \&\&, we're going with the latter.
        """

        replacement = r'\\\1'
        (quoted, number_of_subs_made) = re.subn(self.pattern, replacement, text)
        if self.pattern.match(text):
            print(self.pattern.match(text).groups())
        print(text)
        print(quoted)
        print(number_of_subs_made)
        return quoted

    def to_url(self, text: str):
        """
        Remove quotes added to escape lucene special characters.
        """
        unquoted = re.sub(r'"\\([\+\-!\(\)\{\}\[\]\^\"~\*\?\:\\/&\|])"', r'\1', text)
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
