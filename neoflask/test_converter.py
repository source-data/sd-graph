from pytest import fixture
from pytest import mark

from .converter import LuceneQueryConverter

@fixture
def lucene_query_converter():
    yield LuceneQueryConverter(map=None)

@mark.parametrize(
    "input, expected_output, message",
    [
        (r"no special characters", r"no special characters", 'string without special chars'),
        (r'+sp-ec*al| & {(cha:rs)} in "s\tr^ng&?]', r'\+sp\-ec\*al\| \& \{\(cha\:rs\)\} in \"s\\tr\^ng\&\?\]', 'lots of special chars somewhere in text'),
        (r'\+', r'\\\+', 'already escaped char'),
        (r'\\+', r'\\\\\+', 'escaped char preceeded by escaped backslash'),
        (r'\\\+', r'\\\\\\\+', 'already escaped char preceeded by escaped backslash'),
    ]
)
def test_lucene_query_converter_to_python(lucene_query_converter, input, expected_output, message):
    actual_output = lucene_query_converter.to_python(input)
    assert actual_output == expected_output, message