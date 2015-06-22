import sys

from datetime import datetime
from article import ArticleGeneric

from db import db_articles

class UnrecognisedPageType(Exception):
  pass

def get_page(page_url):
  klass = ArticleGeneric #route_page(page_url)
  
  if klass is not None:
    try:
      page = klass(page_url)
    except klass.FetchError, e:
      print e
      return None

    return page.as_dict()
  else:
    raise UnrecognisedPageType(page_url)

def task_get_page(page_url, source, save=True):
    page_doc = db_articles.find_one({'keys': page_url})

    new = False

    if page_doc is None:
        try:
            page = get_page(page_url)
        except UnrecognisedPageType:
            print "Could not get page {}".format(page_url)

            return None
            
        page_doc = {'page': page,
                    'source': source,
                    'time_added': datetime.now(),
                    'keys': [page_url],}
       
        if save: 
            page_doc['_id'] = db_articles.save(page_doc)

        new = True

    return new, page_doc

def task_get_feed(feed_url, feed_type):
  klass = feed_types[feed_type]
  feed = klass(feed_url)

  source = {'feed_url': feed_url,
            'feed_type': feed_type,}

  for url in feed.get_urls():
    task_get_page(url, source=source)

if __name__ == "__main__":
  #task_get_feed(feeds[0][0], feeds[0][1])
  task_get_page(sys.argv[1], "Manual")

