import abc
import threading


__all__ = ['InMemoryDataStore', 'DuplicatedKeyError', 'DuplicatedValueError']


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

