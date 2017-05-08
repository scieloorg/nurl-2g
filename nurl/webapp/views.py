from datetime import datetime

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import httpexceptions

from nurl.shortener import (
        URLError,
        NotExists,
        )
from nurl.trackers import Access


@view_config(route_name='home', renderer='templates/home.pt')
def home(request):

    response_dict = {'project':'nurl'}

    incoming_url = request.params.get('url')
    if incoming_url is not None:
        try:
            short_url = url_shortener(request)
        except httpexceptions.HTTPBadRequest:
            errors = response_dict.setdefault('errors', [])
            response_dict['errors'].append(('Invalid URL',
                "Maybe this hostname is not allowed or you've typed something wrong."))
        else:
            response_dict.update({'short_url': short_url})

    return response_dict


@view_config(route_name='shortener_v1', renderer='jsonp')
def url_shortener(request):

    incoming_url = request.params.get('url')
    if not incoming_url:
        raise httpexceptions.HTTPBadRequest()

    try:
        short_ref = request.nurl.shorten(incoming_url)
    except URLError as exc:
        raise httpexceptions.HTTPBadRequest() from None

    return request.route_url('shortened', short_ref=short_ref)


@view_config(route_name='shortened')
def short_ref_resolver(request):
    access = Access(datetime=datetime.now(), referrer=request.referrer,
            browser=request.user_agent)
    try:
        plain_url = request.nurl.resolve(request.matchdict['short_ref'],
                access=access)
    except NotExists:
        raise httpexceptions.HTTPNotFound() from None

    raise httpexceptions.HTTPMovedPermanently(plain_url)

