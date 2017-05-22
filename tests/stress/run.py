#!/usr/bin/env python3
from datetime import datetime
import concurrent.futures

import requests


def shorten(url):
    resp = requests.get('http://0.0.0.0:6543/api/v1/shorten', 
            params={'url': url})
    return resp.text


def main():
    with open('urls.txt') as f:
        urls = [line for line in f]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(shorten, url): url for url in urls}

        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('%r short version is %r' % (url, data))


if __name__ == '__main__':
    t1 = datetime.now()
    main()
    t2 = datetime.now()
    print('Total execution time:', t2 - t1)

