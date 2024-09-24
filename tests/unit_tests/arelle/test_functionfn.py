import pytest
import regex

from arelle.FunctionFn import normalize_space, tokenize
from arelle.formula import XPathContext
from arelle import FunctionFn

# See https://www.w3.org/TR/xpath-functions/#func-tokenize for test sources:
TOKENIZE_TESTS = [
    # If $input is the empty sequence, or if $input is the zero-length string, the function returns the empty sequence.
    (("",), ([]), None),
    (("", r"."), ([]), None),
    (((),), ([]), None),
    (((), r"."), ([]), None),
    # If two alternatives within the supplied $pattern both match at the same position in the $input string, then the match that is chosen is the first. For example:
    (("abracadabra", r"ab|a"), ("", "r", "c", "d", "r", ""), None),
    (("abracadabra", r"(?:ab)|(?:a)"), ("", "r", "c", "d", "r", ""), None),
    # Should still work the same with capturing groups specified
    (("abracadabra", r"(ab)|(a)"), ("", "r", "c", "d", "r", ""), None),
    # Examples from
    ((" red green blue ",), ("red", "green", "blue"), None),
    (
        ("The cat sat on the mat", r"\s+"),
        ("The", "cat", "sat", "on", "the", "mat"),
        None,
    ),
    ((" red green blue ", r"\s+"), ("", "red", "green", "blue", ""), None),
    (("1, 15, 24, 50", r",\s*"), ("1", "15", "24", "50"), None),
    (("1,15,,24,50,", r","), ("1", "15", "", "24", "50", ""), None),
    (("abba", ".?"), None, "[err:FORX0003]"),
    (
        ("Some unparsed <br> HTML <BR> text", r"\s*<br>\s*", "i"),
        ("Some unparsed", "HTML", "text"),
        None,
    ),
    # Broken regex raises right error code
    (("a", "*"), None, "[err:FORX0002]"),
    (("a", "*", "i"), None, "[err:FORX0002]"),
    # Broken flags raises right error code
    (("a", ".", "p"), None, "[err:FORX0001]"),
    # Pattern not found in input, return input string as singleton
    (("asdf", "99", ""), ("asdf",), None),
    # Multi line
    (("\n\nwibble\n\n", ","), ("\n\nwibble\n\n",), None),
    (("\n\nwibble,wobble\n\n", ","), ("\n\nwibble", "wobble\n\n",), None),
    (("\n\nwibble\n\n",), ("wibble",), None),
    (("\n\nwibble \t \t wobble\n\n",), ("wibble", "wobble",), None),
    (("\n\nwibble \t , \t wobble\n\n", r"[\t\n ,]+"), ("", "wibble", "wobble", ""), None),
]


@pytest.mark.parametrize("args,expected,raises", TOKENIZE_TESTS)
def test_tokenize(args, expected, raises):
    xc = None
    p = None
    contextItem = None
    if raises is None:
        result = tokenize(xc, p, contextItem, args)
        assert result == list(expected)
    else:
        with pytest.raises(XPathContext.XPathException, match=regex.escape(raises)):
            result = tokenize(xc, p, contextItem, args)


# See https://www.w3.org/TR/xpath-functions-31/#func-normalize-space for test sources
NORMALIZE_SPACE_TESTS = [
    (("",), "", None, None),
    (((),), "", None, None),
    ((" The    wealthy curled darlings                                         of    our    nation. ",), "The wealthy curled darlings of our nation.", None, None),
    ((), "asdf xyzzy rhubarb", None, "asdf  xyzzy  rhubarb"),
    (("\0\r\n\0\t\0 \0",), "\0 \0 \0 \0", None, None),
    (("\r\n",), "", None, None),
    ((" \tasdf xyzzy\n   \n \n",), "asdf xyzzy", None, None)
]

@pytest.mark.parametrize("args,expected,raises,context", NORMALIZE_SPACE_TESTS)
def test_normalize_space(args, expected, raises, context, monkeypatch):
    xc = None
    p = None
    contextItem = None

    def fake_string(xc, p, contextItem, args):
        return context

    # the zero argument variant of normalize() calls fn:string() on the context
    # so fake up string() to always return the context specified in the test
    # data
    monkeypatch.setattr(FunctionFn, "string", fake_string)

    if raises is None:
        result = normalize_space(xc, p, contextItem, args)
        assert result == expected
    else:
        with pytest.raises(XPathContext.XPathException, match=regex.escape(raises)):
            result = normalize_space(xc, p, contextItem, args)
