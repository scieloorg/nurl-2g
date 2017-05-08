import unittest
from unittest import mock
import itertools

from nurl.shortener import (
        Nurl,
        NotExists,
        URLChecker,
        SOCKET_TIMEOUT,
        )
from nurl import datastores


DEFAULT_SHORTIDS = ['4kgjc', '5fv7w']


def cycling_idgen_stub(shortids=DEFAULT_SHORTIDS):
    for shortid in itertools.cycle(shortids):
        yield shortid


class NurlTests(unittest.TestCase):
    def setUp(self):
        self.store = datastores.InMemoryDataStore()
        self.idgen = lambda: cycling_idgen_stub(['4kgjc'])  # will not cycle by default
        self.nurl = Nurl(self.store, self.idgen)

    def test_shorten_url(self):
        self.assertEqual(self.nurl.shorten('http://www.scielo.br'), '4kgjc')

    def test_resolve_shortid(self):
        url = 'http://www.scielo.br'
        self.assertEqual(self.nurl.resolve(self.nurl.shorten(url)), url)

    def test_duplicated_shortid(self):
        store = datastores.InMemoryDataStore(initial={'4kgjc': 'http://www.scielo.br'})
        idgen = lambda: cycling_idgen_stub()
        local_nurl = Nurl(store, idgen)

        self.assertEqual(local_nurl.shorten('http://www.scielo.org'), '5fv7w')

    def test_duplicated_url(self):
        store = datastores.InMemoryDataStore(initial={'4kgjc': 'http://www.scielo.br'})
        idgen = lambda: cycling_idgen_stub(['5fv7w'])  # avoid collision logic for keys
        local_nurl = Nurl(store, idgen)

        self.assertEqual(local_nurl.shorten('http://www.scielo.br'), '4kgjc')

    def test_resolve_unknown_id_raises_keyerror(self):
        self.assertRaises(NotExists, lambda: self.nurl.resolve('xxxxx'))


class URLCheckerTests(unittest.TestCase):
    def setUp(self):
        self.url = 'http://www.scielo.br'
        self.whitelist = set(['www.scielo.br'])

    def test_url_without_scheme(self):
        self.assertRaises(ValueError,
                lambda: URLChecker('www.scielo.br'))

    def test_url_with_scheme(self):
        self.assertTrue(URLChecker(self.url))

    def test_hostname_is_allowed(self):
        nc = URLChecker(self.url, whitelist=self.whitelist)
        self.assertTrue(nc.is_allowed_hostname())

    def test_hostname_is_not_allowed(self):
        nc = URLChecker('http://www.scielo.org', whitelist=self.whitelist)
        self.assertFalse(nc.is_allowed_hostname())

    def test_missing_whitelist(self):
        nc = URLChecker('http://www.scielo.org')
        self.assertTrue(nc.is_allowed_hostname())

    def test_passing_none_to_whitelist(self):
        nc = URLChecker('http://www.scielo.org', whitelist=None)
        self.assertTrue(nc.is_allowed_hostname())

    def test_passing_empty_colection_to_whitelist(self):
        nc = URLChecker('http://www.scielo.org', whitelist=[])
        self.assertFalse(nc.is_allowed_hostname())
    
    def test_ping_opens_the_url(self):
        nc = URLChecker('http://www.scielo.br')
        urlopen = nc.urllib_request.urlopen = mock.MagicMock(return_value='foo')
        nc.ping()
        urlopen.assert_called_once_with('http://www.scielo.br', 
                timeout=SOCKET_TIMEOUT)

    def test_httperror_exc_makes_ping_return_false(self):
        import urllib.error
        class MyHTTPError(urllib.error.HTTPError):
            def __init__(self):
                """O inicializador original recebe diversos argumentos 
                obrigatórios. Aqui a coisa está sendo simplificada.
                """
                self.file = self.msg = ''
                self.code = 0

        def se(url, timeout):
            raise MyHTTPError()

        nc = URLChecker('http://www.scielo.br')
        urlopen = nc.urllib_request.urlopen = mock.MagicMock(side_effect=se)
        self.assertFalse(nc.ping())

    def test_urlerror_exc_makes_ping_return_false(self):
        import urllib.error
        class MyURLError(urllib.error.URLError):
            def __init__(self):
                """O inicializador original recebe diversos argumentos 
                obrigatórios. Aqui a coisa está sendo simplificada.
                """
                self.reason = ''

        def se(url, timeout):
            raise MyURLError()

        nc = URLChecker('http://www.scielo.br')
        urlopen = nc.urllib_request.urlopen = mock.MagicMock(side_effect=se)
        self.assertFalse(nc.ping())

    def test_socket_timeout_makes_ping_return_false(self):
        import socket

        def se(url, timeout):
            raise socket.timeout()

        nc = URLChecker('http://www.scielo.br')
        urlopen = nc.urllib_request.urlopen = mock.MagicMock(side_effect=se)
        self.assertFalse(nc.ping())


if __name__ == '__main__':
    unittest.main()

