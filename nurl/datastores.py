import abc
import threading
import logging

import pymongo


__all__ = ['InMemoryDataStore', 'DuplicatedKeyError', 'DuplicatedValueError',
        'MongoDBDataStore']


LOGGER = logging.getLogger(__name__)


class DuplicatedKeyError(Exception):
    pass


class DuplicatedValueError(Exception):
    pass


class DataStore(metaclass=abc.ABCMeta):
    """Armazena pares chave-valor.

    Deve apresentar as seguintes garantias:
      - Ao tentar armazenar uma chave já existente, a exceção 
        :class:`DuplicatedKeyError` será levantada.
      - Ao tentar armazenar um valor já existente, a exceção
        :class:`DuplicatedValueError` será levantada.
    """
    @abc.abstractmethod
    def __setitem__(self, key: str, value: str) -> None:
        return NotImplemented

    @abc.abstractmethod
    def __getitem__(self, key: str) -> str:
        return NotImplemented

    @abc.abstractmethod
    def key(self, url: str) -> str:
        return NotImplemented


class InMemoryDataStore(DataStore):
    def __init__(self, initial=None):
        self.data = {}
        self.revdata = {}
        self.lock = threading.Lock()

        if initial:
            for k, v in initial.items():
                self[k] = v

    def __setitem__(self, key, value):
        with self.lock:
            if key in self.data:
                raise DuplicatedKeyError()
            elif value in self.revdata:
                raise DuplicatedValueError()
            else:
                self.data[key] = value
                self.revdata[value] = key

    def __getitem__(self, key):
        return self.data[key]

    def key(self, url):
        return self.revdata[url]


class MongoDBDataStore(DataStore):
    def __init__(self, collection):
        self.collection = collection

        self.collection.create_index('short_ref', unique=True)
        self.collection.create_index('plain', unique=True)

    def __setitem__(self, key, value):
        record = {'plain': value, 'short_ref': key}
        try:
            _ = self.collection.insert_one(record)
        except pymongo.errors.DuplicateKeyError as exc:
            if 'plain' in str(exc):
                raise DuplicatedValueError() from None
            else:
                raise DuplicatedKeyError() from None

    def __getitem__(self, key):
        record = self.collection.find_one({'short_ref': key})
        if record is None:
            raise KeyError()
        else:
            return record['plain']

    def key(self, url):
        record = self.collection.find_one({'plain': url})
        if record is None:
            raise KeyError()
        else:
            return record['short_ref']

