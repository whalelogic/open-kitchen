import os
from flask import Flask, render_template


def create_app(test_config=None):
    """Application factory for Open Kitchen."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'community_kitchen.db'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    from . import db
    db.init_app(app)

    # Register blueprints
    from . import auth, recipes, dashboard, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(recipes.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(admin.bp)

    # Index route
    @app.route('/')
    def index():
        from app.db import get_db
        db = get_db()
        
        # Get recent recipes
        recent_recipes = db.execute(
            'SELECT r.*, u.username as author_name, '
            'AVG(rv.rating) as avg_rating, '
            'COUNT(DISTINCT rv.id) as review_count '
            'FROM recipes r '
            'JOIN users u ON r.author_id = u.id '
            'LEFT JOIN reviews rv ON r.id = rv.recipe_id '
            'WHERE r.is_public = 1 '
            'GROUP BY r.id '
            'ORDER BY r.created_at DESC LIMIT 6'
        ).fetchall()
        
        # Get stats
        stats = {
            'total_recipes': db.execute('SELECT COUNT(*) FROM recipes WHERE is_public = 1').fetchone()[0],
            'total_users': db.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            'total_reviews': db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0],
        }
        
        # Get popular categories
        categories = db.execute('SELECT * FROM categories LIMIT 6').fetchall()
        
        return render_template('index.html', 
                             recipes=recent_recipes, 
                             stats=stats,
                             categories=categories)

    return app
