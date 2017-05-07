import string
from random import randrange

BASE36 = string.digits + string.ascii_lowercase
# sem vogais, para nao formar palavras em portugues
# sem 1l0, para evitar confusões na leitura
BASE28 = ''.join(d for d in BASE36 if d not in '1l0aeiou')


def encode(n, digits):
    base = len(digits)
    s = []
    while n:
        n, d = divmod(n, base)
        s.insert(0, digits[d])
    if s:
        return ''.join(s)
    else:
        return digits[0]


def generate(length, digits=BASE28):
    arbitrary_value = randrange(len(digits) ** length)
    return encode(arbitrary_value, digits).rjust(length, digits[0])


def igenerate(length, digits=BASE28):
    while True:
        yield generate(length, digits)

