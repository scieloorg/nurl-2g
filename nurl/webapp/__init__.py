from pyramid.config import Configurator
from pyramid.renderers import JSONP
from pyramid.events import NewRequest
import webassets


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('nurl.pyramid_nurl')

    # renderers
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    # URL patterns
    config.add_static_view(path='nurl.webapp:static', name='static',
            cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('shortened', '/{short_ref}')

    # restful endpoints
    config.add_route('shortener_v1', '/api/v1/shorten')

    css = webassets.Bundle(
        'bootstrap.min.css',
        webassets.Bundle('styles.css', filters='yui_css'),
        output='bundle.min.css')

    config.add_webasset('css', css)
    config.registry.settings['webassets_env'] = config.get_webassets_env()
    config.add_subscriber(add_webassets_env, NewRequest)

    config.scan()
    return config.make_wsgi_app()


def add_webassets_env(event):
    settings = event.request.registry.settings
    event.request.webassets_env = settings['webassets_env']

