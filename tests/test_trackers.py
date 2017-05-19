import os
import unittest
import operator
from datetime import datetime

from nurl import trackers


IS_RUNNING_ON_TRAVISCI = os.environ.get('TRAVIS', False)


class InMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tracker = trackers.InMemoryTracker()
        self.access_sample = trackers.Access(datetime=datetime.utcnow(),
                referrer='sample.com', browser='mozilla')

    def test_add_new(self):
        self.tracker.add('foo', self.access_sample)
        accesses = list(self.tracker.get('foo'))
        self.assertEqual(len(accesses), 1)
        self.assertEqual(accesses[0], self.access_sample)

    def test_add_new_on_existing_shortid(self):
        self.tracker.add('foo', self.access_sample)
        self.tracker.add('foo', self.access_sample)
        accesses = list(self.tracker.get('foo'))
        self.assertEqual(len(accesses), 2)

    def test_get_accesses(self):
        self.tracker.add('foo', self.access_sample)
        accesses = list(self.tracker.get('foo'))
        self.assertEqual(accesses, [self.access_sample])

    def test_get_accesses_for_unknown_shortid(self):
        accesses = list(self.tracker.get('unknown'))
        self.assertEqual(accesses, [])


@unittest.skipUnless(IS_RUNNING_ON_TRAVISCI, 'requires travis-ci')
class MongoDBTests(unittest.TestCase):
    """Testes de integração executados apenas no Travis-CI.
    """
    def setUp(self):
        import pymongo
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.collection = self.client['nurl_tests']['accesses']
        self.tracker = trackers.MongoDBTracker(self.collection)
        self.access_sample = trackers.Access(datetime='20170519',
                referrer='sample.com', browser='mozilla')

    def tearDown(self):
        self.client.drop_database('nurl_tests')

    def test_add_new(self):
        self.tracker.add('foo', self.access_sample)
        accesses = list(self.tracker.get('foo'))
        self.assertEqual(len(accesses), 1)
        self.assertEqual(accesses[0], self.access_sample)

    def test_add_new_on_existing_shortid(self):
        self.tracker.add('foo', self.access_sample)
        self.tracker.add('foo', self.access_sample)
        accesses = list(self.tracker.get('foo'))
        self.assertEqual(len(accesses), 2)

    def test_get_accesses(self):
        self.tracker.add('foo', self.access_sample)
        accesses = list(self.tracker.get('foo'))
        self.assertEqual(accesses, [self.access_sample])

    def test_get_accesses_for_unknown_shortid(self):
        accesses = list(self.tracker.get('unknown'))
        self.assertEqual(accesses, [])

