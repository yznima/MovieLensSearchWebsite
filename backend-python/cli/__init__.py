from . import load_movies

def init_app(app):
    app.register_blueprint(load_movies.bp, cli_group=None)
