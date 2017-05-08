#!/usr/bin/env python
#coding:utf-8
from __future__ import unicode_literals
from setuptools import setup, find_packages
import setuptools
import codecs
import sys


if sys.version_info[0:2] < (3, 3):
    raise RuntimeError('Requires Python 3.3 or newer')


INSTALL_REQUIRES = [
        'pyramid >= 1.8.3',
        'pyramid-chameleon >= 0.3',
        'pyramid-webassets >= 0.9',
        'yuicompressor >= 2.4.8',
        ]
TESTS_REQUIRE = []


setup(
    name="nurl",
    version="0.1",
    description="URL shortening tool for SciELO's resources.",
    long_description=codecs.open('README.rst', mode='r', encoding='utf-8').read() + '\n\n' +
                     codecs.open('HISTORY.rst', mode='r', encoding='utf-8').read(),
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    maintainer="Gustavo Fonseca",
    maintainer_email="gustavo.fonseca@scielo.org",
    license="BSD License",
    url="http://github.com/scieloorg/nurl-2g",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    tests_require=TESTS_REQUIRE,
    test_suite='tests',
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'paste.app_factory': [
            'main = nurl.webapp:main',
        ],
    },
)

