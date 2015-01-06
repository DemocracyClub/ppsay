import requests
import json
from urlparse import urlparse

from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
from flask import Blueprint, url_for, render_template, request, jsonify, abort, redirect

from ppsay.log import log
from ppsay.tasks import task_get_page
from ppsay.dates import add_date
from ppsay.domains import add_domain
from ppsay.matches import add_matches, resolve_matches
from ppsay.data import (
    constituencies,
    constituencies_index,
    constituencies_names,
    get_candidate,
    get_candidates,
)

db_client = MongoClient()

db_articles = db_client.news.articles
db_log = db_client.news.action_log

app = Blueprint('ppsay',
                __name__,
                template_folder='templates')

def get_person(person_id):
  req = requests.get("http://yournextmp.popit.mysociety.org/api/v0.1/persons/{}".format(person_id))

  return req.json()['result']

def get_mapit_area(area_id):
  req = requests.get("http://mapit.mysociety.org/area/{}".format(area_id))

  return req.json()

@app.route('/')
def index():
  article_docs = db_articles.find() \
                         .sort([('time_added', -1)])

  return render_template('index.html',
                         articles=article_docs)

@app.route('/person/<int:person_id>')
def person(person_id):
  article_docs = db_articles.find({'candidates':
                                {'$elemMatch': {'id': str(person_id)}}}) \
                         .sort([('time_added', -1)])

  person_doc = get_person(person_id)

  person_doc['current_party'] = person_doc['party_memberships'][max(person_doc['party_memberships'])]

  return render_template('person.html',
                         articles=article_docs,
                         person=person_doc)

@app.route('/constituency/<int:constituency_id>')
def constituency(constituency_id):
  article_docs = db_articles.find({'constituencies':
                                {'$elemMatch': {'id': str(constituency_id), 'state': {'$ne': 'removed'}}}}) \
                         .sort([('time_added', -1)])

  area_doc = get_mapit_area(constituency_id)
  #posts_doc = get_person(person_id)

  #person_doc['current_party'] = person_doc['party_memberships'][max(person_doc['party_memberships'])]

  return render_template('constituency.html',
                         articles=article_docs,
                         area=area_doc)

with open('../parse_data/sources_news.dat', 'r') as f:
    domain_whitelist = {line.split()[0] for line in f}

@app.route('/article', methods=['POST'])
def article_add():
    url = request.form.get('url', None)

    if url is None:
        return abort(500, "URL of article not supplied")

    url_parsed = urlparse(url)

    if url_parsed.scheme == "":
        url = "http://" + url
        url_parsed = urlparse(url)

    if url_parsed.netloc not in domain_whitelist:
        return render_template("article_add_fail.html",
                               url=url,
                               domain=url_parsed.netloc)

    doc_id = task_get_page(url, "User")

    doc = db_articles.find_one({'_id': doc_id})

    add_date(doc)
    add_domain(doc)
    add_matches(doc)

    resolve_matches(doc)

    db_articles.save(doc)
    
    return redirect(url_for(".article", doc_id=str(doc['_id'])))


@app.route('/article/<doc_id>')
def article(doc_id):
    doc_id = ObjectId(doc_id)

    doc = db_articles.find_one({'_id': doc_id})

    return render_template('article.html',
                           article=doc)

@app.route('/article/<doc_id>/people', methods=['PUT'])
def article_person_confirm(doc_id):
    doc_id = ObjectId(doc_id)
    doc = db_articles.find_one({'_id': doc_id})

    person_id = request.form.get('person_id', None)

    doc['user']['candidates']['confirm'].append(person_id)

    if person_id in doc['user']['candidates']['remove']:
        doc['user']['candidates']['remove'].remove(person_id)
    
    doc['user']['candidates']['confirm'] = list(set(doc['user']['candidates']['confirm']))
    doc['user']['candidates']['remove'] = list(set(doc['user']['candidates']['remove']))
   
    resolve_matches(doc)
 
    db_articles.save(doc)

    log('person_confirm', url_for('.article', doc_id=str(doc_id)), {'person_id': person_id,
                                                                   'person_name': get_candidate(person_id)['name']})
 
    return render_template('article_people_tagged.html',
                           article=doc)
 
@app.route('/article/<doc_id>/people', methods=['DELETE'])
def article_person_remove(doc_id):
    doc_id = ObjectId(doc_id)
    doc = db_articles.find_one({'_id': doc_id})
    
    person_id = request.form.get('person_id', None)

    doc['user']['candidates']['remove'].append(person_id)
    
    if person_id in doc['user']['candidates']['confirm']:
        doc['user']['candidates']['confirm'].remove(person_id)
    
    doc['user']['candidates']['confirm'] = list(set(doc['user']['candidates']['confirm']))
    doc['user']['candidates']['remove'] = list(set(doc['user']['candidates']['remove']))

    resolve_matches(doc)

    db_articles.save(doc)
    
    log('person_remove', url_for('.article', doc_id=str(doc_id)), {'person_id': person_id, 
                                                                  'person_name': get_candidate(person_id)['name']})
 
    return render_template('article_people_tagged.html',
                           article=doc)

@app.route('/article/<doc_id>/constituencies', methods=['PUT'])
def article_constituency_confirm(doc_id):
    doc_id = ObjectId(doc_id)
    doc = db_articles.find_one({'_id': doc_id})

    constituency_id = request.form.get('constituency_id', None)

    doc['user']['constituencies']['confirm'].append(constituency_id)

    if constituency_id in doc['user']['constituencies']['remove']:
        doc['user']['constituencies']['remove'].remove(constituency_id)
    
    doc['user']['constituencies']['confirm'] = list(set(doc['user']['constituencies']['confirm']))
    doc['user']['constituencies']['remove'] = list(set(doc['user']['constituencies']['remove']))
    
    resolve_matches(doc)

    db_articles.save(doc)
    
    log('constituency_confirm', url_for('.article', doc_id=str(doc_id)), {'constituency_id': constituency_id,
                                                                         'constituency_name': constituencies_index[constituency_id]['name']})
 
    return render_template('article_constituencies_tagged.html',
                           article=doc)
 
@app.route('/article/<doc_id>/constituencies', methods=['DELETE'])
def article_constituency_remove(doc_id):
    doc_id = ObjectId(doc_id)
    doc = db_articles.find_one({'_id': doc_id})

    constituency_id = request.form.get('constituency_id', None)

    doc['user']['constituencies']['remove'].append(constituency_id)

    if constituency_id in doc['user']['constituencies']['confirm']:
        doc['user']['constituencies']['confirm'].remove(constituency_id)
    
    doc['user']['constituencies']['confirm'] = list(set(doc['user']['constituencies']['confirm']))
    doc['user']['constituencies']['remove'] = list(set(doc['user']['constituencies']['remove']))
    
    resolve_matches(doc)

    db_articles.save(doc)
    
    log('constituency_remove', url_for('.article', doc_id=str(doc_id)), {'constituency_id': constituency_id,
                                                                        'constituency_name': constituencies_index[constituency_id]['name']})
 
    return render_template('article_constituencies_tagged.html',
                           article=doc)

@app.route('/autocomplete/person', methods=['GET'])
def autocomplete_person():
    partial_person_name = request.args.get('term')

    matches = []
    for candidate in get_candidates():
        if candidate['name'].lower().startswith(partial_person_name.lower()):
            party = constituency = 'Unknown'

            if '2015' in candidate['candidacies']:
                party = candidate['candidacies']['2015']['party']['name']
                constituency = candidate['candidacies']['2015']['constituency']['name']
            elif '2010' in candidate['candidacies']:
                party = candidate['candidacies']['2010']['party']['name']
                constituency = candidate['candidacies']['2010']['constituency']['name']

            label = u"{} ({}) - {}".format(candidate['name'], party, constituency)
            matches.append({'label': label, 'value': candidate['id']})

    return json.dumps(matches)

@app.route('/autocomplete/constituency', methods=['GET'])
def autocomplete_constituency():
    partial_constituency_name = request.args.get('term')

    matches = []
    for constituency_id, names in constituencies_names.items():
        for name in names:
            if name.lower().startswith(partial_constituency_name.lower()):
                matches.append({'label': name, 'value': constituency_id})

    return json.dumps(matches)

dashboard_queries = [{'query': {},
                      'id': 'num_articles',
                      'name': 'Number of articles',},
                     {'query': {'page': None},
                      'id': 'num_articles_no_page',
                      'name': 'Number of unscraped articles',},
                     {'query': {'page.date_published': None},
                      'id': 'num_articles_no_date',
                      'name': 'Number of articles without a date',},
                     {'query': {'possible.candidates': {'$size': 0}},
                      'id': 'num_articles_no_candidates',
                      'name': 'Number of articles with no candidates',},
                     {'query': {'possible.constituencies': {'$size': 0}},
                      'id': 'num_articles_no_constituencies',
                      'name': 'Number of articles with no constituencies',},
                    ]

dashboard_query_index = {q['id']: q for q in dashboard_queries}
          
@app.route('/dashboard')
def dashboard():
    stats = {query['id']: db_articles.find(query['query']).count() for query in dashboard_queries}

    return render_template('dashboard.html',
                           queries=dashboard_queries,
                           stats=stats)

@app.route('/dashboard/articles/<query_id>')
def dashboard_article(query_id):
    query = dashboard_query_index[query_id]
    docs = db_articles.find(query['query'])

    return render_template('dashboard_query.html',
                           query=query,
                           articles=docs)

@app.route('/recent')
def action_log():
    log = db_log.find() \
                .sort([('time_now', -1)])[:50]

    return render_template('action_log.html',
                           log=log)


