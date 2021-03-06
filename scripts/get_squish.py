# -*- coding: utf-8 -*-
import sys
import json
import re
import requests
from ppsay.data import constituencies_index, squish_constituencies

url = u"https://en.wikipedia.org/w/api.php?action=opensearch&search={}&limit=100&namespace=0&format=json"

token_re = re.compile(u'([^ ,‘’“”.!;:\'"?\-=+_\r\n\t()]+)')

def get_tokens(s):
    tokens = []
    spans = []
    
    for match in token_re.finditer(s):
        tokens.append(match.groups()[0])
        spans.append(match.span())
        
    return tokens, spans


def is_inside(l1, l2):
    for i in range(len(l2) - len(l1) + 1):
        if l1 == l2[i:i+len(l1)]:
            return True

    return False

def search_wikipedia(search):
    url = u"http://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&srlimit={}&sroffset={}&format=json"
    limit = 50
    offset = 0

    search_tokens = get_tokens(search.lower())[0]

    found = 0
    while offset < 10000:
        url_ = url.format(search, limit, offset)
        print >>sys.stderr, offset, " ",
        resp = requests.get(url_)

        data = resp.json()

        for obj in data['query']['search']:
            title = obj['title']
            title = re.sub(u'\(.*?\)', '', title).strip()
            title_tokens = get_tokens(title.lower())[0]

            if is_inside(search_tokens, title_tokens) and search_tokens != title_tokens:
                yield title
                found += 1

        #print >>sys.stderr, found

        if 'query-continue' in data:
            offset = data['query-continue']['search']['sroffset']
        else:
            break

#titles = set(search_wikipedia(sys.argv[1]))

#for title in titles:
#    print title

squish = squish_constituencies

print "{}/{} constituencies done".format(len(squish.keys()), len(constituencies_index.keys()))

constituencies = []

if len(sys.argv) > 1:
    constituencies.append(constituencies_index[sys.argv[1]])
else:
    constituencies = [x for constituency_id, x in constituencies_index.items() if constituency_id not in squish]

for constituency in constituencies:
    print
    print constituency['name']
    titles = set(search_wikipedia(constituency['name']))

    squish[constituency['id']] = list(titles)

    json.dump(squish, open('ppsay/data/squish_constituencies.json', 'w+'), indent=4)

