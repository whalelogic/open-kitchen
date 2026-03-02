from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.db import get_db
from app.auth import login_required

bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@bp.route('/')
def index():
    """List all public recipes with filtering."""
    db = get_db()
    
    # Get filter parameters
    category = request.args.get('category')
    tag = request.args.get('tag')
    author = request.args.get('author')
    search = request.args.get('search')
    
    # Build query
    query = '''
        SELECT DISTINCT r.*, u.username as author_name,
               AVG(rv.rating) as avg_rating,
               COUNT(DISTINCT rv.id) as review_count
        FROM recipes r
        JOIN users u ON r.author_id = u.id
        LEFT JOIN reviews rv ON r.id = rv.recipe_id
        WHERE r.is_public = 1
    '''
    params = []
    
    if category:
        query += ' AND r.id IN (SELECT recipe_id FROM recipe_categories WHERE category_id = ?)'
        params.append(category)
    
    if tag:
        query += ' AND r.id IN (SELECT recipe_id FROM recipe_tags WHERE tag_id = ?)'
        params.append(tag)
    
    if author:
        query += ' AND r.author_id = ?'
        params.append(author)
    
    if search:
        query += ' AND (r.title LIKE ? OR r.description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' GROUP BY r.id ORDER BY r.created_at DESC'
    
    recipes = db.execute(query, params).fetchall()
    
    return render_template('recipes/index.html', recipes=recipes)


@bp.route('/<int:id>')
def view(id):
    """View a single recipe with ingredients and instructions."""
    db = get_db()
    
    recipe = db.execute(
        'SELECT r.*, u.username as author_name '
        'FROM recipes r JOIN users u ON r.author_id = u.id '
        'WHERE r.id = ?',
        (id,)
    ).fetchone()
    
    if recipe is None:
        flash('Recipe not found.')
        return redirect(url_for('recipes.index'))
    
    # Get ingredients
    ingredients = db.execute(
        'SELECT i.*, u.name as unit_name, u.abbreviation, a.name as allergen_name '
        'FROM ingredients i '
        'JOIN units u ON i.unit_id = u.id '
        'LEFT JOIN allergens a ON i.allergen_id = a.id '
        'WHERE i.recipe_id = ?',
        (id,)
    ).fetchall()
    
    # Get instructions
    instructions = db.execute(
        'SELECT * FROM instructions WHERE recipe_id = ? ORDER BY step_number',
        (id,)
    ).fetchall()
    
    # Get reviews
    reviews = db.execute(
        'SELECT r.*, u.username FROM reviews r '
        'JOIN users u ON r.user_id = u.id '
        'WHERE r.recipe_id = ? ORDER BY r.created_at DESC',
        (id,)
    ).fetchall()
    
    # Get comments
    comments = db.execute(
        'SELECT c.*, u.username FROM comments c '
        'JOIN users u ON c.user_id = u.id '
        'WHERE c.recipe_id = ? ORDER BY c.created_at DESC',
        (id,)
    ).fetchall()
    
    return render_template('recipes/view.html', 
                         recipe=recipe, 
                         ingredients=ingredients,
                         instructions=instructions,
                         reviews=reviews,
                         comments=comments)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new recipe."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        template_type = request.form['template_type']
        base_servings = request.form.get('base_servings', type=int)
        prep_time = request.form.get('prep_time_minutes', type=int)
        cook_time = request.form.get('cook_time_minutes', type=int)
        
        error = None
        if not title:
            error = 'Title is required.'
        elif template_type not in ['standard', 'quick_tip']:
            error = 'Invalid template type.'
        
        if error is None:
            db = get_db()
            cursor = db.execute(
                'INSERT INTO recipes (title, description, template_type, author_id, '
                'base_servings, prep_time_minutes, cook_time_minutes) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (title, description, template_type, g.user['id'], 
                 base_servings, prep_time, cook_time)
            )
            db.commit()
            
            # Log activity
            db.execute(
                'INSERT INTO activity_logs (user_id, action_type, entity_type, entity_id) '
                'VALUES (?, ?, ?, ?)',
                (g.user['id'], 'created', 'recipe', cursor.lastrowid)
            )
            db.commit()
            
            return redirect(url_for('recipes.view', id=cursor.lastrowid))
        
        flash(error)
    
    return render_template('recipes/create.html')


@bp.route('/<int:id>/fork', methods=('POST',))
@login_required
def fork(id):
    """Fork an existing recipe."""
    db = get_db()
    
    # Get original recipe
    original = db.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    
    if original is None:
        flash('Recipe not found.')
        return redirect(url_for('recipes.index'))
    
    # Create forked recipe
    cursor = db.execute(
        'INSERT INTO recipes (title, description, template_type, author_id, '
        'base_servings, prep_time_minutes, cook_time_minutes, parent_recipe_id) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (f"{original['title']} (Fork)", original['description'], 
         original['template_type'], g.user['id'], original['base_servings'],
         original['prep_time_minutes'], original['cook_time_minutes'], id)
    )
    new_recipe_id = cursor.lastrowid
    
    # Copy ingredients
    ingredients = db.execute('SELECT * FROM ingredients WHERE recipe_id = ?', (id,)).fetchall()
    for ing in ingredients:
        db.execute(
            'INSERT INTO ingredients (recipe_id, name, quantity, unit_id, allergen_id) '
            'VALUES (?, ?, ?, ?, ?)',
            (new_recipe_id, ing['name'], ing['quantity'], ing['unit_id'], ing['allergen_id'])
        )
    
    # Copy instructions
    instructions = db.execute('SELECT * FROM instructions WHERE recipe_id = ?', (id,)).fetchall()
    for inst in instructions:
        db.execute(
            'INSERT INTO instructions (recipe_id, step_number, content) '
            'VALUES (?, ?, ?)',
            (new_recipe_id, inst['step_number'], inst['content'])
        )
    
    # Copy categories and tags
    db.execute(
        'INSERT INTO recipe_categories (recipe_id, category_id) '
        'SELECT ?, category_id FROM recipe_categories WHERE recipe_id = ?',
        (new_recipe_id, id)
    )
    db.execute(
        'INSERT INTO recipe_tags (recipe_id, tag_id) '
        'SELECT ?, tag_id FROM recipe_tags WHERE recipe_id = ?',
        (new_recipe_id, id)
    )
    
    # Log activity
    db.execute(
        'INSERT INTO activity_logs (user_id, action_type, entity_type, entity_id) '
        'VALUES (?, ?, ?, ?)',
        (g.user['id'], 'forked', 'recipe', new_recipe_id)
    )
    
    # Notify original author
    if original['author_id'] != g.user['id']:
        db.execute(
            'INSERT INTO notifications (user_id, type, reference_id, message) '
            'VALUES (?, ?, ?, ?)',
            (original['author_id'], 'fork_created', new_recipe_id,
             f"{g.user['username']} forked your recipe '{original['title']}'")
        )
    
    db.commit()
    flash('Recipe forked successfully!')
    return redirect(url_for('recipes.view', id=new_recipe_id))
