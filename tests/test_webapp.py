import unittest

from pyramid import testing

from nurl import (
        shortener,
        trackers,
        datastores,
        base28,
        )
from nurl.webapp import views


class WebassetsStub(object):
    def urls(self):
        return ['/static/styles.css']


class ViewTests(unittest.TestCase):
    """
    Tests the HTTP API
    """
    def setUp(self):
        webassets_env = {'css':WebassetsStub()}
        tracker = trackers.InMemoryTracker()
        nurl = shortener.Nurl(datastores.InMemoryDataStore(), 
                              lambda: base28.igenerate_id(6),
                              whitelist=None,
                              tracker=tracker)
        self.request = testing.DummyRequest(nurl=nurl,
                                            tracker=tracker,
                                            webassets_env=webassets_env,
                                            referrer='',
                                            user_agent='')
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()

