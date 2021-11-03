from .database import get_es, get_db

def init_app(app):
    get_db()
    get_es()