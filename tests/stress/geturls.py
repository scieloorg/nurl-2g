from articlemeta.client import RestfulClient


def main():
    client = RestfulClient()

    urls = (j.url() for j in client.journals(collection='scl'))

    with open('urls.txt', 'w') as f:
        for url in urls:
            f.write(url+'\n')


if __name__ == '__main__':
    main()

