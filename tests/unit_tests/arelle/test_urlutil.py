import pytest

from arelle.UrlUtil import _PSVI_SAFE_CHARS, anyUriQuoteForPSVI, isValidUriReference

URIS = [
    'ftp://ftp.is.co.za/rfc/rfc1808.txt',
    'http://www.ietf.org/rfc/rfc2396.txt',
    'ldap://[2001:db8::7]/c=GB?objectClass?one',
    'mailto:John.Doe@example.com',
    'news:comp.infosystems.www.servers.unix',
    'tel:+1-816-555-1212',
    'telnet://192.0.2.16:80/',
    'urn:oasis:names:specification:docbook:dtd:xml:4.1.2',
]

URI_REFERENCES = [
    'g',
    './g',
    'g/',
    '/g',
    '//g',
    '?y',
    'g?y',
    '#s',
    'g#s',
    'g?y#s',
    ';x',
    'g;x',
    'g;x?y#s',
    '',
    '.',
    './',
    '..',
    '../',
    '../g',
    '../..',
    '../../',
    '../../g',
]


@pytest.mark.parametrize('uri', URIS)
def test_uris(uri):
    assert isValidUriReference(uri)


@pytest.mark.parametrize('uri_reference', URI_REFERENCES)
def test_uri_references(uri_reference):
    assert isValidUriReference(uri_reference)


# ---------------------------------------------------------------------------
# anyUriQuoteForPSVI
#
# Columns: uri | modified (bool) | expected output when modified=True
# When modified=False the function must return the input unchanged.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('uri, modified, expected', [
    # --- clean: no unsafe chars, returned unchanged ---
    ('http://example.com/path',              False, None),
    ('http://example.com/path?query=1&b=2',  False, None),
    ('http://example.com/path#fragment',     False, None),
    ('http://example.com/already%20encoded', False, None),  # % is in safe=
    ('/relative/path',                       False, None),
    ('',                                     False, None),
    # ~ is in the unsafe set but also in safe=, so the quote() call preserves it
    ('http://example.com/~user',             False, None),
    # --- explicit unsafe chars ---
    ('http://example.com/ path',             True,  'http://example.com/%20path'),
    ('http://example.com/<tag>',             True,  'http://example.com/%3Ctag%3E'),
    ('http://example.com/a>b',               True,  'http://example.com/a%3Eb'),
    ('http://example.com/"q"',               True,  'http://example.com/%22q%22'),
    ('http://example.com/{c}',               True,  'http://example.com/%7Bc%7D'),
    ('http://example.com/a|b',               True,  'http://example.com/a%7Cb'),
    ('http://example.com/back\\slash',       True,  'http://example.com/back%5Cslash'),
    ('http://example.com/car^et',            True,  'http://example.com/car%5Eet'),
    ('http://example.com/back`tick',         True,  'http://example.com/back%60tick'),
    # --- control characters U+0000–U+001F (single UTF-8 byte each) ---
    ('http://example.com/\x00',              True,  'http://example.com/%00'),
    ('http://example.com/\x1f',              True,  'http://example.com/%1F'),
    # --- DEL (U+007F, single UTF-8 byte) ---
    ('http://example.com/\x7f',              True,  'http://example.com/%7F'),
    # --- U+0080–U+00FF: two UTF-8 bytes each ---
    ('http://example.com/\x80',              True,  'http://example.com/%C2%80'),
    ('http://example.com/\xff',              True,  'http://example.com/%C3%BF'),
    # --- Unicode above U+00FF: triggers quoting, encoded as UTF-8 ---
    ('http://example.com/cafĀ',         True,  'http://example.com/caf%C4%80'),
    ('http://example.com/中文',      True,  'http://example.com/%E4%B8%AD%E6%96%87'),
])
def test_anyUriQuoteForPSVI(uri, modified, expected):
    result = anyUriQuoteForPSVI(uri)
    assert (result != uri) == modified
    if modified:
        assert result == expected


def test_anyUriQuoteForPSVI_safe_chars_not_encoded_when_quoting_triggered():
    # A space forces quoting; the safe= characters must survive unencoded.
    result = anyUriQuoteForPSVI(f'http://example.com/ {_PSVI_SAFE_CHARS}')
    for c in _PSVI_SAFE_CHARS:
        assert c in result, f"safe char {c!r} was unexpectedly percent-encoded"
