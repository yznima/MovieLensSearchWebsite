import pymysql
from pymysql.constants import CLIENT

from flask import current_app, g

def init_db():
    get_db()

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