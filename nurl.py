"""
    >>> dictstore = {}
    >>> nurl = Nurl(dictstore)
    >>> nurl.shorten('http://scielo.br')
    '4kgjc'

    >>> nurl.resolve('4kgjc')
    'http://scielo.br'
"""
import collections


class Nurl:
    def __init__(self, store, idgen):
        self.store = store
        self.idgen = idgen

    def shorten(self, url):
        for shortid in self.idgen:
            try:
                self.store[shortid] = url
            except DuplicatedKeyError:
                # could not store an URL due to a collision on key
                continue
            except DuplicatedValueError:
                return self.store.key(url)
            else:
                return shortid

    def resolve(self, shortid):
        return self.store[shortid]


class DuplicatedKeyError(Exception):
    pass


class DuplicatedValueError(Exception):
    pass


class UniqueStore(collections.UserDict):
    def __setitem__(self, key, value):
        if key in self.data:
            raise DuplicatedKeyError()

        elif value in self.data.values():
            raise DuplicatedValueError()

        else:
            self.data[key] = value

    def key(self, url):
        inv = {val:key for key, val in self.data.items()}
        return inv[url]

