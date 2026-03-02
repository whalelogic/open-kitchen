from flask import Blueprint, render_template, g
from app.db import get_db
from app.auth import login_required

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
def index():
    """User's personal dashboard - 'My Kitchen'."""
    db = get_db()
    user_id = g.user['id']
    
    # Get authored recipes
    authored = db.execute(
        'SELECT r.*, COUNT(DISTINCT rv.id) as review_count, '
        'AVG(rv.rating) as avg_rating '
        'FROM recipes r '
        'LEFT JOIN reviews rv ON r.id = rv.recipe_id '
        'WHERE r.author_id = ? '
        'GROUP BY r.id ORDER BY r.created_at DESC',
        (user_id,)
    ).fetchall()
    
    # Get forked recipes
    forked = db.execute(
        'SELECT r.*, orig.title as parent_title '
        'FROM recipes r '
        'LEFT JOIN recipes orig ON r.parent_recipe_id = orig.id '
        'WHERE r.author_id = ? AND r.parent_recipe_id IS NOT NULL '
        'ORDER BY r.created_at DESC',
        (user_id,)
    ).fetchall()
    
    # Get saved recipes
    saved = db.execute(
        'SELECT r.*, u.username as author_name, sr.saved_at '
        'FROM saved_recipes sr '
        'JOIN recipes r ON sr.recipe_id = r.id '
        'JOIN users u ON r.author_id = u.id '
        'WHERE sr.user_id = ? '
        'ORDER BY sr.saved_at DESC',
        (user_id,)
    ).fetchall()
    
    # Get notifications
    notifications = db.execute(
        'SELECT * FROM notifications '
        'WHERE user_id = ? '
        'ORDER BY created_at DESC LIMIT 10',
        (user_id,)
    ).fetchall()
    
    return render_template('dashboard/index.html',
                         authored=authored,
                         forked=forked,
                         saved=saved,
                         notifications=notifications)
