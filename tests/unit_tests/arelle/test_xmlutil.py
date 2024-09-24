import pytest
from unittest.mock import Mock, patch

from arelle.ModelObject import ModelObject
from arelle.ModelValue import qname
from arelle.XmlUtil import (
    escapedNode,
    replaceWhitespace,
    collapseWhitespace
)
from arelle.XhtmlValidate import (
    htmlEltUriAttrs,
    resolveHtmlUri,
)


@patch('arelle.XmlUtil.htmlEltUriAttrs', new=htmlEltUriAttrs)
@patch('arelle.XmlUtil.resolveHtmlUri', new=resolveHtmlUri)
def test_opaque_uris_not_path_normed():
    uri = 'data:image/png;base64,iVBORw0K//a'
    elt_attrs = {'src': uri}
    elt = Mock(
        spec=ModelObject,

        localName='img',
        namespaceURI='http://www.w3.org/1999/xhtml',
        modelDocument=Mock(htmlBase=None),
        prefix=None,

        get=elt_attrs.get,
        items=elt_attrs.items,
    )
    elt.qname = qname(elt)
    node = escapedNode(elt, start=True, empty=True, ixEscape=True, ixResolveUris=True)
    assert node == f'<img src="{uri}">'


REPLACE_WHITESPACE_TESTS = [
    ("\n", " "),
    ("\r", " "),
    ("\t", " "),
    ("\r\v\t", " \v "),
    ("\r\t\n", "   "),
    ("\t\t \n\n \r\r", " " * 8),
    (" m u s h r o o m  ", " m u s h r o o m  "),
    (" m u s h\tr o o m  ", " m u s h r o o m  "),
]


@pytest.mark.parametrize("value, expected", REPLACE_WHITESPACE_TESTS)
def test_replaceWhitespace(value, expected):
    result = replaceWhitespace(value)
    assert result == expected


COLLAPSE_WHITESPACE_TESTS = [
    ("\n", ""),
    ("\r", ""),
    ("\t", ""),
    ("\r\v\t", "\v"),
    ("\r\t\n", ""),
    ("\t\t \n\n \r\r", ""),
    (" " * 100, ""),
    ("\r \n \t", ""),
    ("\r \n \t", ""),
    ("\v v \v", "\v v \v"),
    ("  \v  v  \v  ", "\v v \v"),
    (" " * 100 + "\v1" + " ", "\v1"),
    (" x  xm   xml    xmln     ", "x xm xml xmln"),
    ("time: \n\tround\n\ttuit  \r\n", "time: round tuit")
]


@pytest.mark.parametrize("value, expected", COLLAPSE_WHITESPACE_TESTS)
def test_collapseWhitespace(value, expected):
    result = collapseWhitespace(value)
    assert result == expected

