import csv
import zipfile

import click
import database
import flask
from flask import Blueprint, current_app

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

bp = Blueprint('cli', __name__)

@bp.cli.command("load-movielens")
def load_movielens():
    with zipfile.ZipFile('ml-latest-small.zip') as zip:
        zip.extractall()
    print('Extracted the ml-latest-small.zip')
    db = database.get_db()
    install_schema(db)
    insert_movies(db)
    insert_links(db)
    insert_ratings(db)
    insert_tags(db)
    insert_to_elasticsearch(db)

def install_schema(db):
    with current_app.open_resource('schema.sql') as f:
        with db.cursor() as cur:
            cur.execute(f.read().decode('utf8'), ())
            db.commit()

    print('Installed the schema')

def insert_movies(db):
    inserts = []
    genres = []
    with open('ml-latest-small/movies.csv') as movies:
            spamreader = csv.reader(movies)
            spamreader.__next__() # Ignore the header
            for row in spamreader:
                inserts.append(tuple(row[0:2]))
                gs = row[2].split("|")
                for g in gs:
                    genres.append((row[0], g))
    
    with db.cursor() as cur:
        cur.executemany('INSERT INTO movies(id,title) VALUES(%s, %s)', inserts)
        db.commit()
        cur.executemany('INSERT INTO genres(movie_id,genre) VALUES(%s, %s)', genres)
        db.commit()

    print('Inserted the movies')


def insert_links(db):
    inserts = []
    with open('ml-latest-small/links.csv') as links:
        spamreader = csv.reader(links)
        spamreader.__next__() # Ignore the header
        for row in spamreader:
            inserts.append((row[1], row[2] if row[2] != "" else 0, row[0]))

    with db.cursor() as cur:
        cur.executemany('UPDATE movies SET imdb_id = %s, tmdb_id = %s where id = %s', inserts)
        db.commit()

    print('Inserted the links')

def insert_ratings(db):
    inserts = []
    with open('ml-latest-small/ratings.csv') as ratings:
        spamreader = csv.reader(ratings)
        spamreader.__next__() # Ignore the header
        for row in spamreader:
            inserts.append(tuple(row))

    with db.cursor() as cur:
        cur.executemany('INSERT INTO ratings(user_id,movie_id,rating,timestamp) VALUES(%s, %s, %s, %s)', inserts)
        db.commit()

    print('Inserted the ratings')


def insert_tags(db):
    inserts = []
    with open('ml-latest-small/tags.csv') as tags:
        spamreader = csv.reader(tags)
        spamreader.__next__() # Ignore the header
        for row in spamreader:
            inserts.append(tuple(row))

    with db.cursor() as cur:
        cur.executemany('INSERT INTO tags(user_id,movie_id,tag,timestamp) VALUES(%s, %s, %s, %s)', inserts)
        db.commit()

    print('Inserted the tags')


def insert_to_elasticsearch(db):
    es = Elasticsearch(["search:9200"])
    es.indices.delete(index="movies")
    es.indices.create(index="movies", body="""
{
    "mappings":{
        "properties": {
            "title": {
                "type": "text"
            },
            "imdb_id": {
                "type": "keyword"
            },
            "tmdb": {
                "type": "keyword"
            },
            "rating": {
                "type": "float"
            },
            "genres": {
                "type": "text"
            },
            "tags": {
                "type": "text"
            }
        }
    }
}
    """, )

    with db.cursor() as cur:
            cur.execute('SELECT id, title, imdb_id, tmdb_id FROM movies')
            movies = cur.fetchall()

    actions = []
    for movie in movies:
        actions.append({
            '_index': "movies",
            '_op_type': "index",
            '_id': movie[0],
            'title': movie[1],
            'imdb': movie[2],
            'tmdb': movie[3]
        })
    result = bulk(es, actions)

    with db.cursor() as cur:
        cur.execute('SELECT movie_id, AVG(rating) FROM ratings GROUP By movie_id')
        ratings = cur.fetchall()

    actions = []
    for rating in ratings:
        actions.append({
            '_index': "movies",
            '_op_type': "update",
            '_id': rating[0],
            'doc': {'rating': rating[1]},
        })
    
    with db.cursor() as cur:
        cur.execute('SELECT movie_id, genre FROM genres')
        genres = cur.fetchall()

    actions_dict = {}
    for genre in genres:
        movie_id = genre[0]
        if movie_id not in actions_dict:
            actions_dict[movie_id] = []
        actions_dict[movie_id].append(genre[1])
    
    actions = []
    for movie_id in actions_dict:
        actions.append({
             '_index': "movies",
             '_op_type': "update",
             '_id': movie_id,
             'doc': {'genres': actions_dict[movie_id]},
         })

    result = bulk(es, actions)

    with db.cursor() as cur:
        cur.execute('SELECT DISTINCT movie_id, tag FROM tags')
        tags = cur.fetchall()

    actions_dict = {}
    for tag in tags:
        movie_id = tag[0]
        if movie_id not in actions_dict:
            actions_dict[movie_id] = []
        actions_dict[movie_id].append(tag[1])
    
    actions = []
    for movie_id in actions_dict:
        actions.append({
             '_index': "movies",
             '_op_type': "update",
             '_id': movie_id,
             'doc': {'tags': actions_dict[movie_id]},
         })

    result = bulk(es, actions)

