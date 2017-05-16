import os
import unittest
import operator

from nurl import datastores


IS_RUNNING_ON_TRAVISCI = os.environ.get('TRAVIS', False)


class InMemoryTests(unittest.TestCase):
    def setUp(self):
        self.store = datastores.InMemoryDataStore()

    def test_add_new_pair(self):
        self.store['foo'] = 'bar'
        self.assertEqual(self.store['foo'], 'bar')

    def test_add_new_value_on_existing_key(self):
        self.store['foo'] = 'bar'
        self.assertRaises(datastores.DuplicatedKeyError, 
                lambda: operator.setitem(self.store, 'foo', 'baz'))

    def test_add_existing_value_on_new_key(self):
        self.store['foo'] = 'bar'
        self.assertRaises(datastores.DuplicatedValueError,
                lambda: operator.setitem(self.store, 'baz', 'bar'))

    def test_add_existing_pair(self):
        self.store['foo'] = 'bar'
        self.assertRaises(datastores.DuplicatedKeyError,
                lambda: operator.setitem(self.store, 'foo', 'bar'))

    def test_get_key_for_value(self):
        self.store['foo'] = 'bar'
        self.assertEqual(self.store.key('bar'), 'foo')

    def test_get_key_for_non_existing_value(self):
        self.store['foo'] = 'bar'
        self.assertRaises(KeyError, lambda: self.store.key('baz'))


@unittest.skipUnless(IS_RUNNING_ON_TRAVISCI, 'requires travis-ci')
class MongoDBTests(unittest.TestCase):
    """Testes de integração executados apenas no Travis-CI.
    """
    def setUp(self):
        import pymongo
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.collection = self.client['nurl_tests']['urls']
        self.store = datastores.MongoDBDataStore(self.collection)

    def tearDown(self):
        self.client.drop_database('nurl_tests')

    def test_add_new_pair(self):
        self.store['foo'] = 'bar'
        self.assertEqual(self.store['foo'], 'bar')

    def test_add_new_value_on_existing_key(self):
        self.store['foo'] = 'bar'
        self.assertRaises(datastores.DuplicatedKeyError, 
                lambda: operator.setitem(self.store, 'foo', 'baz'))

    def test_add_existing_value_on_new_key(self):
        self.store['foo'] = 'bar'
        self.assertRaises(datastores.DuplicatedValueError,
                lambda: operator.setitem(self.store, 'baz', 'bar'))

    def test_add_existing_pair(self):
        self.store['foo'] = 'bar'
        self.assertRaises(datastores.DuplicatedKeyError,
                lambda: operator.setitem(self.store, 'foo', 'bar'))

    def test_get_key_for_value(self):
        self.store['foo'] = 'bar'
        self.assertEqual(self.store.key('bar'), 'foo')

    def test_get_key_for_non_existing_value(self):
        self.store['foo'] = 'bar'
        self.assertRaises(KeyError, lambda: self.store.key('baz'))

