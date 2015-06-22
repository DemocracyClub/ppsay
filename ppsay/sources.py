from urlparse import urlparse
from domains import domain_whitelist, add_domain
from tasks import task_get_page
from dates import add_date
from matches import add_matches, resolve_matches, add_quotes
from ml.assign import get_machine
from db import db_web_cache, db_articles

def process_doc(doc, state):
    try:
        doc['page']['date_published'] = add_date(doc)
    except ValueError: # ignore date errors for now
        pass

    doc['domain'] = add_domain(doc)

    doc['matches'], doc['possible'] = add_matches([doc['page']['text'],
                                                   doc['page']['title'],])

    doc['quotes'], doc['tags'] = add_quotes(doc['matches'],
                                            [doc['page']['text'],
                                             doc['page']['title']])
    
    doc['machine'] = get_machine(doc)

    resolve_matches(doc)

    doc['state'] = state

    return

def get_source_whitelist(source_url, source):
    """
        Get a source and save it if the domain is in the whitelist.
    """

    source_url_parsed = urlparse(source_url)
    
    if source_url_parsed.netloc in domain_whitelist:
        article_doc = get_source(source_url, source, 'approved')

        return article_doc
    else:
        return None

def get_source_if_matches(source_url, source, state, min_candidates=1, min_parties=0, min_constituencies=0):
    """
        Get a source and save it if there are matches.
    """

    doc_cache = db_web_cache.find_one({'url': source_url})

    if doc_cache is not None:
        print "Already in cache, skipping"
        return None

    new, doc = task_get_page(source_url, source, False)
    
    if new and doc['page'] is not None:
        print "  New"

        process_doc(doc, state) 

        # Only save if it has matches
        if len(doc['possible']['candidates']) >= min_candidates and \
           len(doc['possible']['constituencies']) >= min_constituencies and \
           len(doc['possible']['parties']) >= min_parties:

            print "    Matches"

            doc['_id'] = db_articles.save(doc)
        else:
            print "    No matches"
    else:
        print "  Not new"

    return doc

def get_source(source_url, source, state):
    """
        Get a source and save it, no matter what.
    """

    new, doc = task_get_page(source_url, source)

    if new and doc['page'] is not None:
        process_doc(doc, state) 

        doc['_id'] = db_articles.save(doc)

    return doc

