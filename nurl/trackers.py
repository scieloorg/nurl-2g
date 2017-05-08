import abc
from collections import namedtuple
from typing import Iterable


Access = namedtuple('Access', 'datetime referrer browser')


class Tracker(metaclass=abc.ABCMeta):
    """Registra acesso às URLs encurtadas.
    """
    @abc.abstractmethod
    def add(self, shortid: str, access: Access) -> None:
        return NotImplemented

    @abc.abstractmethod
    def get(self, shortid: str) -> Iterable[Access]:
        return NotImplemented


class InMemoryTracker(Tracker):
    def __init__(self):
        self.data = {}

    def add(self, shortid, access):
        shortid_rec = self.data.setdefault(shortid, [])
        shortid_rec.append(access)

    def get(self, shortid):
        return self.data[shortid]

