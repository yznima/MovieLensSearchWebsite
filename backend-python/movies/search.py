import database
import flask
from elasticsearch.helpers import bulk
from flask import Blueprint

bp = Blueprint('search', __name__, url_prefix="/search")


@bp.route("/movies", methods = ['POST'])
def search_movies():
    body = flask.request.json
    query = body.get('query', '')
    page = body.get('page', {})
    tags = unique(body.get('tags', []))
    
    pageSize = min(page.get('size', 20), 20)
    pageStart = (page.get('next', 1) - 1) * pageSize

    bool_query = {
        'must': [],
        'filter': []
    }
    if query != "":
        bool_query['must'].append({
            'bool': {
                'should': [
                    { 'match': { 'title' : query } },
                    { 'prefix': { 'title' : { 'value' : query } } }
                ]
            }
        })

    if len(tags) != 0:
        bool_query['filter'].append({
            'bool': {
                'should': [ {'term': {'tags': tag}} for tag in tags ]
            }
        })

    result = database.get_es().search(index="movies", from_=pageStart, size=pageSize, query={
        'bool': bool_query
    })

    hits = result['hits']['hits']

    movies = []
    for hit in hits:
        print(hit)
        source = hit['_source']
        movies.append({
            'id': hit['_id'],
            'title': source['title'],
            'imdb': source['imdb'],
            'tmdb': source['tmdb'],
            'genres': source['genres'],
            'rating': source.get('rating', 0)
        })

    return flask.jsonify(dict(result=movies, totalCount=result['hits']['total']['value']))

def unique(list1):
    unique_list = []
    list_set = set(list1)
    return list(list_set)

@bp.route("/tags", methods = ['POST'])
def search_tags():
    body = flask.request.json
    query = body.get('query', '')
    page = body.get('page', {})
        
    db = database.get_db()
    with db.cursor() as cur:
        pageSize = 20
        pageStart = 0
        if query == "":
            cur.execute('SELECT DISTINCT tag FROM tags LIMIT %s,%s', (pageStart, pageSize))
            tags = cur.fetchall()
            cur.execute('SELECT COUNT(*) FROM tags')
            (count,) = cur.fetchone()
        else:
            cur.execute('SELECT DISTINCT tag FROM tags WHERE tag LIKE CONCAT("%%", %s, "%%") LIMIT %s,%s', (query, pageStart, pageSize))
            tags = cur.fetchall()
            cur.execute('SELECT COUNT(*) FROM tags WHERE tag LIKE CONCAT("%%", %s, "%%")', (query))
            (count,) = cur.fetchone()
        
        result = []
        for tag in tags:
            result.append(tag[0])

        return flask.jsonify(dict(result=result, totalCount=count))
    

    return flask.jsonify(dict(result=result))
