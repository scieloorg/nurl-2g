FROM python:3.6.1-alpine
ENV PYTHONUNBUFFERED 1

# Build-time metadata as defined at http://label-schema.org
ARG BUILD_DATE
ARG VCS_REF
ARG WEBAPP_VERSION

ENV IMAGE_BUILD_DATE ${BUILD_DATE}
ENV IMAGE_VCS_REF ${VCS_REF}
ENV IMAGE_WEBAPP_VERSION ${WEBAPP_VERSION}

COPY requirements.txt production.ini whitelist.txt /app/
COPY dist/* /tmp/pypa/

RUN pip --no-cache-dir install -r /app/requirements.txt && \
    pip --no-cache-dir install -f file:///tmp/pypa -U nurl

RUN rm -rf /tmp/pypa

USER nobody
EXPOSE 6543

CMD gunicorn --paste /app/production.ini

