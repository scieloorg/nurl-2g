from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings
from pyramid.renderers import JSONP
from pyramid.events import NewRequest
import webassets

from nurl import (
        base28,
        datastores,
        trackers,
        shortener,
        )


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

    # subscribers
    shortid_len = int(config.registry.settings.get('nurl.digit_count', 6))
    idgen = lambda: base28.igenerate_id(shortid_len)
    access_tracker = trackers.InMemoryTracker()
    nurl = shortener.Nurl(datastores.InMemoryDataStore(), idgen,
            tracker=access_tracker)
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

