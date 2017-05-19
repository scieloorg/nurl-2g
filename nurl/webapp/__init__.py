import sys
import logging

from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings
from pyramid.renderers import JSONP
from pyramid.events import NewRequest
import webassets
import pymongo

from nurl import (
        base28,
        datastores,
        trackers,
        shortener,
        )


LOGGER = logging.getLogger(__name__)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    set_cache_regions_from_settings(settings)
    config = Configurator(settings=settings)

    # renderers
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    # URL patterns
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('analytics', '/analytics/{short_ref}')
    config.add_route('shortened', '/{short_ref}')

    # restful endpoints
    config.add_route('shortener_v1', '/api/v1/shorten')

    # mongodb client
    mongodb_uri = settings.get('mongodb.db_uri')
    mongodb_name = settings.get('mongodb.db_name')
    mongodb_dscol = settings.get('mongodb.datastore_col_name')
    mongodb_trcol = settings.get('mongodb.tracker_col_name')
    if not all([mongodb_uri, mongodb_name, mongodb_dscol, mongodb_trcol]):
        sys.exit('Missing MongoDB configuration')

    mongodb_client = pymongo.MongoClient(mongodb_uri, appname='nURL')
    data_collection = mongodb_client[mongodb_name][mongodb_dscol]
    trac_collection = mongodb_client[mongodb_name][mongodb_trcol]
    LOGGER.info('connected to MongoDB')

    # subscribers
    shortid_len = int(config.registry.settings.get('nurl.digit_count', 6))
    idgen = lambda: base28.igenerate_id(shortid_len)
    access_tracker = trackers.MongoDBTracker(trac_collection)
    datastore = datastores.MongoDBDataStore(data_collection)

    nurl = shortener.Nurl(datastore, idgen, tracker=access_tracker)
    LOGGER.debug('using the nURL instance "%s"', repr(nurl))

    config.registry.settings['nurl'] = nurl
    config.registry.settings['tracker'] = access_tracker
    config.add_subscriber(add_nurl, NewRequest)
    config.add_subscriber(add_access_tracker, NewRequest)

    css = webassets.Bundle(
        'bootstrap.min.css',
        webassets.Bundle('styles.css', filters='yui_css'),
        output='bundle.min.css')
    config.add_webasset('css', css)
    config.registry.settings['webassets_env'] = config.get_webassets_env()
    config.add_subscriber(add_webassets_env, NewRequest)

    config.scan()
    return config.make_wsgi_app()


def add_nurl(event):
    settings = event.request.registry.settings
    event.request.nurl = settings['nurl']


def add_access_tracker(event):
    settings = event.request.registry.settings
    event.request.tracker = settings['tracker']


def add_webassets_env(event):
    settings = event.request.registry.settings
    event.request.webassets_env = settings['webassets_env']

