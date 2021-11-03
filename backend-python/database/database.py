import pymysql
from pymysql.constants import CLIENT
from elasticsearch import Elasticsearch

from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            user="root",
            password="testpass",
            host="db",
            database="challenge",
            client_flag=CLIENT.MULTI_STATEMENTS
        )

    return g.db

def get_es():
    if 'es' not in g:
        g.es =  Elasticsearch(["search:9200"])

    return g.es