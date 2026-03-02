from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_db
from app.auth import curator_required
from datetime import datetime, timedelta

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@curator_required
def index():
    """Admin dashboard."""
    return render_template('admin/index.html')


@bp.route('/users')
@curator_required
def users():
    """Manage users."""
    db = get_db()
    users = db.execute(
        'SELECT u.*, r.name as role_name FROM users u '
        'JOIN roles r ON u.role_id = r.id '
        'ORDER BY u.created_at DESC'
    ).fetchall()
    return render_template('admin/users.html', users=users)


@bp.route('/users/<int:id>/toggle-notifications', methods=('POST',))
@curator_required
def toggle_notifications(id):
    """Toggle user notification settings."""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (id,)).fetchone()
    
    if user:
        new_value = 0 if user['notifications_enabled'] else 1
        db.execute(
            'UPDATE users SET notifications_enabled = ? WHERE id = ?',
            (new_value, id)
        )
        db.commit()
        flash(f"Notifications {'enabled' if new_value else 'disabled'} for user.")
    
    return redirect(url_for('admin.users'))


@bp.route('/reports/most-forked')
@curator_required
def most_forked():
    """Report: Most forked recipes."""
    db = get_db()
    
    recipes = db.execute(
        'SELECT r.id, r.title, u.username as author_name, '
        'COUNT(forks.id) as fork_count '
        'FROM recipes r '
        'JOIN users u ON r.author_id = u.id '
        'LEFT JOIN recipes forks ON forks.parent_recipe_id = r.id '
        'WHERE r.parent_recipe_id IS NULL '
        'GROUP BY r.id '
        'HAVING fork_count > 0 '
        'ORDER BY fork_count DESC'
    ).fetchall()
    
    return render_template('admin/most_forked.html', recipes=recipes)


@bp.route('/reports/allergen-audit')
@curator_required
def allergen_audit():
    """Report: Recipes by allergen."""
    db = get_db()
    allergen_id = request.args.get('allergen_id', type=int)
    
    allergens = db.execute('SELECT * FROM allergens ORDER BY name').fetchall()
    
    recipes = []
    if allergen_id:
        recipes = db.execute(
            'SELECT DISTINCT r.id, r.title, u.username as author_name, '
            'a.name as allergen_name '
            'FROM recipes r '
            'JOIN users u ON r.author_id = u.id '
            'JOIN ingredients i ON r.id = i.recipe_id '
            'JOIN allergens a ON i.allergen_id = a.id '
            'WHERE a.id = ? '
            'ORDER BY r.title',
            (allergen_id,)
        ).fetchall()
    
    return render_template('admin/allergen_audit.html', 
                         allergens=allergens, 
                         recipes=recipes,
                         selected_allergen=allergen_id)


@bp.route('/reports/user-activity')
@curator_required
def user_activity():
    """Report: User activity in last 30 days."""
    db = get_db()
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    
    activity = db.execute(
        'SELECT u.username, '
        'COUNT(CASE WHEN al.action_type = "created" AND al.entity_type = "recipe" THEN 1 END) as recipes_created, '
        'COUNT(CASE WHEN al.action_type = "forked" THEN 1 END) as recipes_forked '
        'FROM users u '
        'LEFT JOIN activity_logs al ON u.id = al.user_id AND al.created_at >= ? '
        'GROUP BY u.id '
        'HAVING recipes_created > 0 OR recipes_forked > 0 '
        'ORDER BY (recipes_created + recipes_forked) DESC',
        (thirty_days_ago,)
    ).fetchall()
    
    return render_template('admin/user_activity.html', activity=activity)


@bp.route('/units')
@curator_required
def units():
    """Manage units lookup table."""
    db = get_db()
    units = db.execute('SELECT * FROM units ORDER BY name').fetchall()
    return render_template('admin/units.html', units=units)


@bp.route('/units/add', methods=('POST',))
@curator_required
def add_unit():
    """Add a new unit."""
    name = request.form['name']
    abbreviation = request.form.get('abbreviation')
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO units (name, abbreviation) VALUES (?, ?)',
            (name, abbreviation)
        )
        db.commit()
        flash('Unit added successfully.')
    except db.IntegrityError:
        flash('Unit already exists.')
    
    return redirect(url_for('admin.units'))
