import sys
import json
import numpy
from collections import defaultdict
from bson import ObjectId
from pymongo import MongoClient
from ppsay.data import get_candidate
from datetime import datetime, timedelta

two_weeks_ago = datetime.now() - timedelta(days=14)

client = MongoClient()
db_articles = client.news.articles

def person_article_count_week(person_id, time_now):
    article_count = db_articles.find({
        'state': 'approved',
        'time_added': {
            '$gte': time_now - timedelta(days=14),
        },
        'analysis.final.candidates': {
            '$elemMatch': {
                'id': person_id,
                'state': {'$nin': ['removed','removed_ml'],},
            },
        }
    }).count()

    return article_count

def vecs(article, return_all=False):
    constituencies = {}

    for possible_constituency in article['analysis']['possible']['constituencies']:
        constituencies[possible_constituency['id']] = possible_constituency

    parties = {}

    for possible_party in article['analysis']['possible']['parties']:
        parties[possible_party['id']] = possible_party

    people = {}
    people_party = defaultdict(list)
    people_constituency = defaultdict(list)

    for possible_candidate in article['analysis']['possible']['candidates']:
        person = get_candidate(possible_candidate['id'])

        if 'ge2015' in person['candidacies']:
            current_party_id = person['candidacies']['ge2015']['party']['id']
            current_constituency_id = person['candidacies']['ge2015']['constituency']['id']

        elif 'ge2010' in person['candidacies']:
            current_party_id = person['candidacies']['ge2010']['party']['id']
            current_constituency_id = person['candidacies']['ge2010']['constituency']['id']

        else:
            current_party_id = None
            current_constituency_id = None

        person['past_week_count'] = person_article_count_week(person['id'], article['time_added'])
        person['current_party_id'] = current_party_id
        person['current_constituency_id'] = current_constituency_id

        people[person['id']] = person
        people_party[current_party_id].append(person['id'])
        people_constituency[current_constituency_id].append(person['id'])
    
    vecs = {}

    for person in people.values():
        vec = {
               'other_party': len(people_party[person['current_party_id']]) - 1.0,
               'other_constituency': len(people_constituency[person['current_constituency_id']]) - 1.0,
               'party_mentioned': 1.0 if person['current_party_id'] in parties else 0.0,
               'constituency_mentioned': 1.0 if person['current_constituency_id'] in constituencies else 0.0,
               'past_week_count': numpy.log(person['past_week_count']+0.1),
        }

        vecs[person['id']] = {'X': vec.values(), 'y': None,}

        if True:
            vecs[person['id']].update({
                'person_id': person['id'],
                'doc_id': str(article.get('_id')),
                'person_name': person['name'],
            })

    if 'user' in article['analysis']:
        for candidate_id in article['analysis']['user']['candidates']['confirm']:
            if candidate_id in vecs:
                vecs[candidate_id]['y'] = 1.0

        for candidate_id in article['analysis']['user']['candidates']['remove']:
            if candidate_id in vecs:
                vecs[candidate_id]['y'] = 0.0
    else:
        print "No resolved candidate data"

    if return_all:
        return vecs.values()
    else:
        return [vec for vec in vecs.values() if vec['y'] is not None]

if __name__ == "__main__":

    if len(sys.argv) > 1:
        article_id = ObjectId(sys.argv[1])
        articles = db_articles.find({'_id': article_id})
    else:
        articles = db_articles.find()

    out_vecs = []
    for article in articles:
        if 'analysis' in article:
            out_vecs += vecs(article)

    print len(out_vecs)
    print "Positive", len([x for x in out_vecs if x['y'] == 1.0])
    print "Negative", len([x for x in out_vecs if x['y'] == 0.0])

    for out_vec in out_vecs:
        print out_vec

    json.dump(out_vecs, open('data.json', 'w+'))

