import unittest
import operator

from nurl import datastores


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

