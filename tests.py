import unittest
import itertools

import nurl


DEFAULT_SHORTIDS = ['4kgjc', '5fv7w']


def cycling_idgen_stub(shortids=DEFAULT_SHORTIDS):
    for shortid in itertools.cycle(shortids):
        yield shortid


class NurlTests(unittest.TestCase):
    def setUp(self):
        self.store = {}
        self.idgen = cycling_idgen_stub(['4kgjc'])  # will not cycle by default
        self.nurl = nurl.Nurl(self.store, self.idgen)

    def test_shorten_url(self):
        self.assertEqual(self.nurl.shorten('http://www.scielo.br'), '4kgjc')

    def test_resolve_shortid(self):
        url = 'http://www.scielo.br'
        self.assertEqual(self.nurl.resolve(self.nurl.shorten(url)), url)

    def test_duplicated_shortid(self):
        store = nurl.UniqueStore({'4kgjc': 'http://www.scielo.br'})
        idgen = cycling_idgen_stub()
        local_nurl = nurl.Nurl(store, idgen)

        self.assertEqual(local_nurl.shorten('http://www.scielo.org'), '5fv7w')

    def test_duplicated_url(self):
        store = nurl.UniqueStore({'4kgjc': 'http://www.scielo.br'})
        idgen = cycling_idgen_stub(['5fv7w'])  # avoid collision logic for keys
        local_nurl = nurl.Nurl(store, idgen)

        self.assertEqual(local_nurl.shorten('http://www.scielo.br'), '4kgjc')


if __name__ == '__main__':
    unittest.main()

