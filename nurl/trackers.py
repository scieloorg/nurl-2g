import abc
from collections import namedtuple
from typing import Iterable
import logging


LOGGER = logging.getLogger(__name__)


Access = namedtuple('Access', 'datetime referrer browser')


class Tracker(metaclass=abc.ABCMeta):
    """Registra acesso às URLs encurtadas.
    """
    @abc.abstractmethod
    def add(self, short_ref: str, access: Access) -> None:
        return NotImplemented

    @abc.abstractmethod
    def get(self, short_ref: str) -> Iterable[Access]:
        return NotImplemented


class InMemoryTracker(Tracker):
    def __init__(self):
        self.data = {}

    def add(self, short_ref, access):
        short_ref_rec = self.data.setdefault(short_ref, [])
        short_ref_rec.append(access)

    def get(self, short_ref):
        for access in self.data.get(short_ref, []):
            yield access


class MongoDBTracker(Tracker):

    def __init__(self, collection):
        self.collection = collection

        self.collection.create_index('short_ref')

    def add(self, short_ref, access):
        record = access._asdict()
        record['short_ref'] = short_ref

        r = self.collection.insert_one(record)
        LOGGER.info('access info was successfully saved to "%s"', r.inserted_id)

    def get(self, short_ref):
        records = self.collection.find({'short_ref': short_ref})
        for rec in records:
            access = Access(datetime=rec['datetime'],
                            referrer=rec['referrer'],
                            browser=rec['browser'])
            yield access
        
