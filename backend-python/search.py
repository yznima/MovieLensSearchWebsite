import flask
from flask import Blueprint

from . import database

bp = Blueprint('search', __name__, url_prefix="/search")

@bp.route("/movies", methods = ['POST'])
def search_movies():
    body = flask.request.json
    query = body.get('query', '')
    page = body.get('page', {})
    tags = unique(body.get('tags', []))
        
    db = database.get_db()
    with db.cursor() as cur:
        pageSize = min(page.get('size', 20), 20)
        pageStart = (page.get('next', 1) - 1) * pageSize
        if len(tags) != 0:
            cur.execute("""
SELECT DISTINCT id, title, imdb_id, tmdb_id 
FROM movies 
JOIN tags ON id = movie_id 
WHERE tag IN %s LIMIT %s,%s
""", (tuple(tags), pageStart, pageSize))
            movies = cur.fetchall()
            cur.execute('SELECT COUNT(*) FROM movies JOIN tags ON id = movie_id WHERE tag IN %s', (tuple(tags),))
            (count,) = cur.fetchone()
        elif query == "":
            cur.execute('SELECT id, title, imdb_id, tmdb_id FROM movies LIMIT %s,%s', (pageStart, pageSize))
            movies = cur.fetchall()
            cur.execute('SELECT COUNT(*) FROM movies')
            (count,) = cur.fetchone()
        else:
            cur.execute('SELECT id, title, imdb_id, tmdb_id FROM movies WHERE title LIKE CONCAT("%%", %s, "%%") LIMIT %s,%s', (query, pageStart, pageSize))
            movies = cur.fetchall()
            cur.execute('SELECT COUNT(*) FROM movies WHERE title LIKE CONCAT("%%", %s, "%%")', (query, ))
            (count,) = cur.fetchone()
        
        result = []
        for movie in movies:
            result.append({
                'id': movie[0],
                'title': movie[1],
                'imdb': movie[2],
                'tmdb': movie[3]
            })

        return flask.jsonify(dict(result=result, totalCount=count))

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