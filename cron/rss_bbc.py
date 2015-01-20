from ppsay.sources import get_source_if_matches
import feedparser

feed = feedparser.parse('http://feeds.bbci.co.uk/news/politics/rss.xml')

def clean_link(x):
    return x.split('#')[0]

for item in feed['items']:
    url = clean_link(item['link'])
    print url
    get_source_if_matches(url, 'rss', 'approved')
