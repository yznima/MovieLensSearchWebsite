from .search import bp as search_bp

def init_app(app):
    app.register_blueprint(search_bp)
