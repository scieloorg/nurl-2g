import urllib.parse
import urllib.request
import urllib.error
import socket
import logging

from . import (
    datastores,
    trackers,
    )


__all__ = ['Nurl', 'URLError', 'NotExists']


LOGGER = logging.getLogger(__name__)


DEFAULT_TIMEOUT = 10  # segundos


class URLError(Exception):
    """Representa erro na formação da URL.

    Os casos considerados erros são:
      - Ausência do `scheme`;
      - Não é possível resolver ou alcançar o servidor;
      - Nome do host não faz parte da lista dos permitidos;
    """


class NotExists(Exception):
    """Representa erro ao resolver ID que não corresponde a alguma URL.
    """


class Nurl:
    """Encurtador de URLs.

    :param store: instância de :class:`nurl.lib.datastores.DataStore`.
    :param idgen: executável que produz uma lista de IDs pseudo-aleatórios.
    :param whitelist: (opcional) coleção de strings de texto representando
                      hostnames permitidos de serem encurtados. O valor `None`
                      desliga o filtro.
    :param tracker: (opcional) instância de :class:`nurl.lib.trackers.Tracker`.
    :param timeout: (opcional) tempo máximo, em segundos, para resposta do 
                    ping.
    """
    def __init__(self, store, idgen, whitelist=None, tracker=None, 
            timeout=DEFAULT_TIMEOUT):
        self.store = store
        self.idgen = idgen
        self.whitelist = set(whitelist) if whitelist else None
        self.tracker = tracker
        self.timeout = timeout

    def shorten(self, url):
        if not is_valid_url(url, self.whitelist, self.timeout):
            raise URLError()

        for attempt, shortid in enumerate(self.idgen()):
            LOGGER.info('attempt #%s to shorten "%s"', attempt, url)
            try:
                self.store[shortid] = url
            except datastores.DuplicatedKeyError:
                LOGGER.info('could not store an URL due to a collision on key')
                continue
            except datastores.DuplicatedValueError:
                LOGGER.info('short id already exists for URL "%s"', url)
                return self.store.key(url)
            else:
                return shortid

    def resolve(self, shortid, access=None):
        assert isinstance(access, (type(None), trackers.Access))

        if access and self.tracker:
            self.tracker.add(shortid, access)
        else:
            LOGGER.info('could not track access to shortid "%s"', shortid)

        try:
            return self.store[shortid]
        except KeyError:
            raise NotExists() from None


class URLChecker:
    """Checador de URLs.
    """
    urllib_request = urllib.request  # para facilitar os testes

    def __init__(self, url, whitelist=None, timeout=DEFAULT_TIMEOUT):
        self.url = url
        self.parsed_url = urllib.parse.urlparse(self.url)
        self.whitelist = whitelist
        self.timeout = timeout

        if self.parsed_url.scheme not in ['http', 'https']:
            raise ValueError('missing URL schema')

    def is_allowed_hostname(self):
        """Verifica o nome do host contra uma lista-branca.
        """
        if self.whitelist is None:
            LOGGER.info('bypassing hostname check against the whitelist')
            return True

        return self.parsed_url.hostname in self.whitelist

    def ping(self):
        """Verifica se a URL alcança um servidor.
        """
        try:
            _ = self.urllib_request.urlopen(self.url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError,
                socket.timeout) as exc:
            LOGGER.info('cannot connect to URL "%s": %s', self.url, str(exc))
            return False
        else:
            return True


def is_valid_url(url, whitelist=None, timeout=DEFAULT_TIMEOUT):
    """Verifica se `url` é válida.
    """
    try:
        uc = URLChecker(url, whitelist, timeout)
    except ValueError as exc:
        LOGGER.info('cannot check URL "%s": %s', url, str(exc))
        return False

    return uc.is_allowed_hostname() and uc.ping()

