import requests
import random


def generate_dictionary():
    request = requests.get("http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain")

    words = request.content.splitlines()
    wordBank = []
    randInts = []
    for i in range(1070):
        while True:
            r = random.randint(0,len(words)-1)
            if r not in randInts:
                break

        randInts.append(r)
        words[r] = "".join(map(chr, words[r])).lower()
        words[r] = "".join(list(filter(lambda c: c.isalpha(), words[r])))
        wordBank.append(words[r])

    return wordBank
