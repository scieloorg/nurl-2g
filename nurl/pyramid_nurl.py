"""Constrói uma instância de :class:`nurl.shortener.Nurl`, configurada de 
acordo com parâmetros fornecidos no arquivo de configurações do pyramid, e 
registra os pontos de acesso ``request.nurl`` e ``request.tracker`` para 
serem utilizados em view-functions.
"""
import sys
import logging

from pyramid.events import NewRequest
from pyramid.settings import asbool
import pymongo

from nurl import (
        base28,
        datastores,
        trackers,
        shortener,
        )


LOGGER = logging.getLogger(__name__)


DEFAULT_SETTINGS = [
        ('nurl.mongodb.uri', str, 'mongodb://localhost:27017/'),
        ('nurl.mongodb.db', str, 'nurl'),
        ('nurl.mongodb.data_col', str, 'urls'),
        ('nurl.mongodb.tracker_col', str,'accesses'),
        ('nurl.whitelist.path', str, ''),
        ('nurl.whitelist.enabled', asbool, False),
        ('nurl.whitelist.auto_www', asbool, True),
        ('nurl.shortref_len', int, 6),
        ]


def parse_settings(settings):
    parsed = {}
    cfg = list(DEFAULT_SETTINGS)

    for name, convert, default in cfg:
        value = settings.get(name, default)
        if convert is not None:
            value = convert(value)
        parsed[name] = value

    return parsed


def includeme(config):
    settings = parse_settings(config.registry.settings)
    config.registry.settings.update(settings)

    # mongodb client
    mongodb_uri = settings['nurl.mongodb.uri']
    mongodb_name = settings['nurl.mongodb.db']
    mongodb_dscol = settings['nurl.mongodb.data_col']
    mongodb_trcol = settings['nurl.mongodb.tracker_col']

    mongodb_client = pymongo.MongoClient(mongodb_uri, appname='nURL')
    data_collection = mongodb_client[mongodb_name][mongodb_dscol]
    trac_collection = mongodb_client[mongodb_name][mongodb_trcol]
    LOGGER.info('connecting to MongoDB instance "%s"', repr(mongodb_client))

    if settings['nurl.whitelist.enabled']:
        whitelist_path = settings['nurl.whitelist.path']
        whitelist_auto_www = settings['nurl.whitelist.auto_www']
        with open(whitelist_path) as wl_file:
            whitelist = get_whitelist(wl_file, whitelist_auto_www)

        # torna a lista disponível para a webapp
        config.registry.settings['nurl.whitelist'] = whitelist

        LOGGER.info('using the whitelist at "%s"', whitelist_path)
        LOGGER.info('whitelist auto-www is %s', 
                'enabled' if whitelist_auto_www else 'disabled')
    else:
        LOGGER.info('whitelist of domain names is not being used')
        whitelist = None

    # subscribers
    shortid_len = settings['nurl.shortref_len']
    idgen = lambda: base28.igenerate_id(shortid_len)
    access_tracker = trackers.MongoDBTracker(trac_collection)
    datastore = datastores.MongoDBDataStore(data_collection)

    nurl = shortener.Nurl(datastore, idgen, tracker=access_tracker, 
            whitelist=whitelist)
    LOGGER.debug('using the nURL instance "%s"', repr(nurl))

    config.registry.settings['nurl'] = nurl
    config.registry.settings['tracker'] = access_tracker
    config.add_subscriber(add_nurl, NewRequest)
    config.add_subscriber(add_access_tracker, NewRequest)


def add_nurl(event):
    settings = event.request.registry.settings
    event.request.nurl = settings['nurl']


def add_access_tracker(event):
    settings = event.request.registry.settings
    event.request.tracker = settings['tracker']


def get_whitelist(whitelist, auto_www=False):
    if auto_www:
        hostnames = []
        for host in whitelist:
            hostnames.append(host.strip('\n'))
            if not host.startswith('www'):
                hostnames.append('www.' + host.strip('\n'))
        return set(hostnames)
    else:
        return set((host.strip('\n') for host in whitelist))

