# Open Kitchen - Application Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│                    (HTML/CSS/JavaScript)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP Requests
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                          │
│                   (Application Factory)                         │
│                      app/__init__.py                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   MIDDLEWARE LAYER                        │  │
│  │  • Session Management (Flask-Session)                     │  │
│  │  • Request Context (g.user)                               │  │
│  │  • Database Connection Pool                               │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                         BLUEPRINTS                              │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │   auth.py    │  recipes.py  │ dashboard.py │  admin.py   │  │
│  │  /auth/*     │  /recipes/*  │ /dashboard/* │  /admin/*   │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │    db.py       │
                    │ (DB Interface) │
                    └────────┬───────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   SQLite Database      │
                │ community_kitchen.db   │
                │   (17 Tables)          │
                └────────────────────────┘
```

---

## Blueprint Architecture with HTTP Methods

### 1. Authentication Blueprint (`auth.py`)
**URL Prefix:** `/auth`

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTH BLUEPRINT                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GET  /auth/register  →  render_template('auth/register')   │
│  POST /auth/register  →  create_user() → redirect('/login') │
│                                                              │
│  GET  /auth/login     →  render_template('auth/login')      │
│  POST /auth/login     →  authenticate() → session['user']   │
│                                                              │
│  GET  /auth/logout    →  session.clear() → redirect('/')    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Database Tables: users, roles                               │
│  Decorators: @login_required, @curator_required              │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. Recipes Blueprint (`recipes.py`)
**URL Prefix:** `/recipes`

```
┌──────────────────────────────────────────────────────────────────┐
│                    RECIPES BLUEPRINT                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  GET  /recipes/                                                   │
│       → list_recipes(filters: category, tag, author, search)      │
│       → render_template('recipes/index')                          │
│                                                                   │
│  GET  /recipes/<id>                                               │
│       → get_recipe_with_ingredients_instructions_reviews()        │
│       → render_template('recipes/view')                           │
│                                                                   │
│  GET  /recipes/create        [@login_required]                    │
│       → render_template('recipes/create')                         │
│                                                                   │
│  POST /recipes/create        [@login_required]                    │
│       → validate_recipe_data()                                    │
│       → insert_recipe()                                           │
│       → log_activity('created', 'recipe')                         │
│       → redirect('/recipes/<new_id>')                             │
│                                                                   │
│  POST /recipes/<id>/fork     [@login_required]                    │
│       → copy_recipe_with_parent_id()                              │
│       → copy_ingredients_instructions()                           │
│       → create_notification(original_author)                      │
│       → log_activity('forked', 'recipe')                          │
│       → redirect('/recipes/<forked_id>')                          │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│  Database Tables:                                                 │
│    • recipes (with parent_recipe_id for forking)                  │
│    • ingredients (quantity, unit_id, allergen_id)                 │
│    • instructions (step_number, content)                          │
│    • recipe_categories, recipe_tags (many-to-many)                │
│    • reviews, comments                                            │
└──────────────────────────────────────────────────────────────────┘
```

---

### 3. Dashboard Blueprint (`dashboard.py`)
**URL Prefix:** `/dashboard`

```
┌─────────────────────────────────────────────────────────────┐
│                  DASHBOARD BLUEPRINT                         │
│                    "My Kitchen"                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GET  /dashboard/              [@login_required]             │
│       → get_authored_recipes(g.user.id)                      │
│       → get_forked_recipes(g.user.id)                        │
│       → get_saved_recipes(g.user.id)                         │
│       → get_notifications(g.user.id, limit=10)               │
│       → render_template('dashboard/index')                   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  Database Tables:                                            │
│    • recipes (WHERE author_id = user_id)                     │
│    • saved_recipes                                           │
│    • notifications                                           │
└─────────────────────────────────────────────────────────────┘
```

---

### 4. Admin Blueprint (`admin.py`)
**URL Prefix:** `/admin`

```
┌──────────────────────────────────────────────────────────────────┐
│                     ADMIN BLUEPRINT                               │
│                   (Curator Role Only)                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  GET  /admin/                          [@curator_required]        │
│       → render_template('admin/index')                            │
│                                                                   │
│  GET  /admin/users                     [@curator_required]        │
│       → list_all_users_with_roles()                               │
│       → render_template('admin/users')                            │
│                                                                   │
│  POST /admin/users/<id>/toggle-notifications  [@curator_required]│
│       → update_user_notification_setting()                        │
│       → redirect('/admin/users')                                  │
│                                                                   │
│  GET  /admin/reports/most-forked       [@curator_required]        │
│       → query_recipes_by_fork_count()                             │
│       → render_template('admin/most_forked')                      │
│                                                                   │
│  GET  /admin/reports/allergen-audit    [@curator_required]        │
│       → filter_recipes_by_allergen(allergen_id)                   │
│       → render_template('admin/allergen_audit')                   │
│                                                                   │
│  GET  /admin/reports/user-activity     [@curator_required]        │
│       → query_activity_logs(last_30_days)                         │
│       → render_template('admin/user_activity')                    │
│                                                                   │
│  GET  /admin/units                     [@curator_required]        │
│       → list_all_units()                                          │
│       → render_template('admin/units')                            │
│                                                                   │
│  POST /admin/units/add                 [@curator_required]        │
│       → insert_new_unit()                                         │
│       → redirect('/admin/units')                                  │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│  Database Tables:                                                 │
│    • users (manage all users)                                     │
│    • units (CRUD operations)                                      │
│    • activity_logs (reporting)                                    │
│    • allergens, recipes (reporting)                               │
└──────────────────────────────────────────────────────────────────┘
```

---

## Database Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                               │
│                  community_kitchen.db                              │
└────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              AUTHENTICATION & AUTHORIZATION                      │
├─────────────────────────────────────────────────────────────────┤
│  roles                                                           │
│    ├─ id (PK)                                                    │
│    └─ name (UNIQUE: 'Contributor', 'Curator')                    │
│                                                                   │
│  users                                                           │
│    ├─ id (PK)                                                    │
│    ├─ username (UNIQUE)                                          │
│    ├─ email (UNIQUE)                                             │
│    ├─ password_hash                                              │
│    ├─ role_id (FK → roles.id)                                    │
│    ├─ notifications_enabled                                      │
│    └─ created_at, updated_at                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    CORE RECIPE SYSTEM                            │
├─────────────────────────────────────────────────────────────────┤
│  recipes                                                         │
│    ├─ id (PK)                                                    │
│    ├─ title, description                                         │
│    ├─ template_type ('standard' | 'quick_tip')                   │
│    ├─ author_id (FK → users.id)                                  │
│    ├─ base_servings                                              │
│    ├─ prep_time_minutes, cook_time_minutes                       │
│    ├─ parent_recipe_id (FK → recipes.id) [FORKING LINEAGE]      │
│    ├─ is_public                                                  │
│    └─ created_at, updated_at                                     │
│         │                                                         │
│         ├──→ ingredients                                         │
│         │      ├─ id (PK)                                        │
│         │      ├─ recipe_id (FK)                                 │
│         │      ├─ name                                           │
│         │      ├─ quantity (REAL - for scaling)                  │
│         │      ├─ unit_id (FK → units.id)                        │
│         │      └─ allergen_id (FK → allergens.id)                │
│         │                                                         │
│         └──→ instructions                                        │
│                ├─ id (PK)                                        │
│                ├─ recipe_id (FK)                                 │
│                ├─ step_number                                    │
│                └─ content                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              LOOKUP TABLES (Curator Managed)                     │
├─────────────────────────────────────────────────────────────────┤
│  units           categories        tags           allergens     │
│  ├─ id           ├─ id             ├─ id          ├─ id         │
│  ├─ name         ├─ name           ├─ name        └─ name       │
│  └─ abbrev       └─ ...            └─ ...         (9 seeded)    │
│  (11 seeded)     (11 seeded)       (11 seeded)                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              MANY-TO-MANY RELATIONSHIPS                          │
├─────────────────────────────────────────────────────────────────┤
│  recipe_categories                 recipe_tags                  │
│  ├─ recipe_id (FK)                 ├─ recipe_id (FK)            │
│  └─ category_id (FK)               └─ tag_id (FK)               │
│  (Composite PK)                    (Composite PK)               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   SOCIAL INTERACTION                             │
├─────────────────────────────────────────────────────────────────┤
│  reviews                                                         │
│    ├─ id (PK)                                                    │
│    ├─ recipe_id (FK → recipes.id)                                │
│    ├─ user_id (FK → users.id)                                    │
│    ├─ rating (1-5)                                               │
│    ├─ comment                                                    │
│    └─ UNIQUE(recipe_id, user_id)                                 │
│                                                                   │
│  comments                                                        │
│    ├─ id (PK)                                                    │
│    ├─ recipe_id (FK → recipes.id)                                │
│    ├─ user_id (FK → users.id)                                    │
│    ├─ content                                                    │
│    └─ created_at                                                 │
│                                                                   │
│  saved_recipes                                                   │
│    ├─ user_id (FK → users.id)                                    │
│    ├─ recipe_id (FK → recipes.id)                                │
│    └─ saved_at                                                   │
│    (Composite PK)                                                │
│                                                                   │
│  friendships                                                     │
│    ├─ id (PK)                                                    │
│    ├─ requester_id (FK → users.id)                               │
│    ├─ addressee_id (FK → users.id)                               │
│    └─ status ('pending' | 'accepted' | 'blocked')                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              SYSTEM INTELLIGENCE                                 │
├─────────────────────────────────────────────────────────────────┤
│  notifications                                                   │
│    ├─ id (PK)                                                    │
│    ├─ user_id (FK → users.id)                                    │
│    ├─ type ('fork_created', 'review_posted', etc.)               │
│    ├─ reference_id                                               │
│    ├─ message                                                    │
│    ├─ is_read                                                    │
│    └─ created_at                                                 │
│                                                                   │
│  activity_logs                                                   │
│    ├─ id (PK)                                                    │
│    ├─ user_id (FK → users.id)                                    │
│    ├─ action_type ('created', 'forked', etc.)                    │
│    ├─ entity_type ('recipe', 'review', etc.)                     │
│    ├─ entity_id                                                  │
│    └─ created_at                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## HTTP Routes & Methods Map

### Public Routes (No Auth Required)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/` | `index()` | Landing page with recent recipes & stats |
| GET | `/recipes/` | `recipes.index()` | List all public recipes |
| GET | `/recipes/<id>` | `recipes.view()` | View single recipe (read-only) |
| GET | `/auth/register` | `auth.register()` | Registration form |
| POST | `/auth/register` | `auth.register()` | Create new user account |
| GET | `/auth/login` | `auth.login()` | Login form |
| POST | `/auth/login` | `auth.login()` | Authenticate user |

### Authenticated Routes (Login Required)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/auth/logout` | `auth.logout()` | Clear session |
| GET | `/recipes/create` | `recipes.create()` | Recipe creation form |
| POST | `/recipes/create` | `recipes.create()` | Save new recipe |
| POST | `/recipes/<id>/fork` | `recipes.fork()` | Fork existing recipe |
| GET | `/dashboard/` | `dashboard.index()` | User's personal kitchen |

### Admin Routes (Curator Role Required)

| Method | Route | Handler | Description |
|--------|-------|---------|-------------|
| GET | `/admin/` | `admin.index()` | Admin dashboard |
| GET | `/admin/users` | `admin.users()` | User management |
| POST | `/admin/users/<id>/toggle-notifications` | `admin.toggle_notifications()` | Update user settings |
| GET | `/admin/reports/most-forked` | `admin.most_forked()` | Fork statistics |
| GET | `/admin/reports/allergen-audit` | `admin.allergen_audit()` | Filter by allergen |
| GET | `/admin/reports/user-activity` | `admin.user_activity()` | 30-day activity report |
| GET | `/admin/units` | `admin.units()` | Manage units |
| POST | `/admin/units/add` | `admin.add_unit()` | Add new unit |

---

## Request Flow Example: Creating a Recipe

```
1. CLIENT
   │
   │  GET /recipes/create
   ▼
2. FLASK
   │  • Check session for user_id
   │  • Load user from database (g.user)
   │  • @login_required decorator validates
   ▼
3. recipes.create() [GET]
   │  • Render form template
   │
   └──→ RESPONSE: HTML form
   
4. CLIENT
   │
   │  POST /recipes/create
   │  Form Data: {title, description, template_type, ...}
   ▼
5. FLASK
   │  • Validate form data
   │  • Get database connection
   ▼
6. recipes.create() [POST]
   │  • INSERT INTO recipes
   │  • Get new recipe_id from cursor.lastrowid
   │  • INSERT INTO activity_logs
   │  • COMMIT transaction
   │
   └──→ REDIRECT: /recipes/<new_id>
```

---

## Request Flow Example: Forking a Recipe

```
1. CLIENT (logged in)
   │
   │  POST /recipes/42/fork
   ▼
2. recipes.fork(id=42)
   │
   ├─→ SELECT * FROM recipes WHERE id = 42
   │   (Get original recipe)
   │
   ├─→ INSERT INTO recipes 
   │   (parent_recipe_id = 42, author_id = g.user.id)
   │   Get new_recipe_id
   │
   ├─→ SELECT * FROM ingredients WHERE recipe_id = 42
   │   Loop: INSERT INTO ingredients (recipe_id = new_recipe_id)
   │
   ├─→ SELECT * FROM instructions WHERE recipe_id = 42
   │   Loop: INSERT INTO instructions (recipe_id = new_recipe_id)
   │
   ├─→ Copy recipe_categories and recipe_tags
   │
   ├─→ INSERT INTO activity_logs
   │   (action_type = 'forked', entity_id = new_recipe_id)
   │
   ├─→ IF original_author != current_user:
   │     INSERT INTO notifications
   │     (user_id = original_author, type = 'fork_created')
   │
   └─→ COMMIT and REDIRECT to /recipes/<new_recipe_id>
```

---

## Authorization Flow

```
┌──────────────┐
│  REQUEST     │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────┐
│  @bp.before_app_request     │
│  load_logged_in_user()      │
├─────────────────────────────┤
│  user_id = session.get()    │
│  if user_id:                │
│    g.user = SELECT users    │
│              JOIN roles     │
│  else:                      │
│    g.user = None            │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Route Decorators           │
├─────────────────────────────┤
│  @login_required            │
│    → if not g.user:         │
│        redirect('/login')   │
│                             │
│  @curator_required          │
│    → if not g.user:         │
│        redirect('/login')   │
│    → if role != 'Curator':  │
│        flash error + deny   │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Execute Route Handler      │
└─────────────────────────────┘
```

---

## Data Flow: Dynamic Ingredient Scaling

```
┌──────────────────────────────────────────────────────────┐
│  STORED IN DATABASE (Never Modified)                     │
├──────────────────────────────────────────────────────────┤
│  recipes.base_servings = 4                               │
│  ingredients:                                             │
│    • flour: quantity=2.0, unit='cup'                      │
│    • sugar: quantity=1.5, unit='cup'                      │
└──────────────────────────────────────────────────────────┘
                          │
                          │  User requests 8 servings
                          ▼
┌──────────────────────────────────────────────────────────┐
│  CALCULATED ON-THE-FLY (In View/Template)               │
├──────────────────────────────────────────────────────────┤
│  scaling_factor = 8 / 4 = 2.0                            │
│                                                           │
│  scaled_ingredients:                                      │
│    • flour: 2.0 × 2.0 = 4.0 cups                         │
│    • sugar: 1.5 × 2.0 = 3.0 cups                         │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Stack

```
┌──────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                       │
│  • Jinja2 Templates                                       │
│  • HTML5 + CSS3                                           │
│  • Responsive Design                                      │
└───────────────────┬──────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────────┐
│  APPLICATION LAYER                                        │
│  • Flask 3.1.3 (Web Framework)                            │
│  • Werkzeug (WSGI, Security, Password Hashing)            │
│  • Flask-WTF (Form Handling)                              │
│  • Jinja2 (Templating Engine)                             │
└───────────────────┬──────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────────┐
│  DATA LAYER                                               │
│  • SQLite 3 (Database)                                    │
│  • Foreign Key Constraints Enabled                        │
│  • Row Factory for dict-like access                       │
└──────────────────────────────────────────────────────────┘
```

---

## Key Design Patterns

### 1. Application Factory Pattern
```python
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # ... configuration
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(recipes.bp)
    # ... more blueprints
    return app
```

### 2. Blueprint Modularity
- Each feature area has its own blueprint
- URL prefixes prevent conflicts
- Blueprints can be tested independently

### 3. Request Context Pattern
```python
g.user  # Loaded before each request
g.db    # Database connection per request
```

### 4. Decorator-Based Authorization
```python
@login_required       # Requires any authenticated user
@curator_required     # Requires Curator role
```

### 5. Database Per Request
```python
get_db()    # Opens connection if not exists
close_db()  # Closes after request (teardown)
```

---

## Security Architecture

```
┌──────────────────────────────────────────────────────────┐
│  PASSWORD SECURITY                                        │
│  • Werkzeug generate_password_hash() with salt            │
│  • Never store plain text passwords                       │
│  • check_password_hash() for verification                 │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  SESSION MANAGEMENT                                       │
│  • Server-side sessions (Flask Session)                   │
│  • SECRET_KEY for session signing                         │
│  • session['user_id'] persists across requests            │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  AUTHORIZATION                                            │
│  • Role-based access control (RBAC)                       │
│  • Decorators enforce permissions                         │
│  • Foreign key integrity prevents orphaned data           │
└──────────────────────────────────────────────────────────┘
```

---

## Extensibility Architecture

The system is designed for future enhancements:

```
Current Implementation:
┌─────────────────────────────────────────────────────────┐
│  Core Features (MVP)                                     │
│  • Authentication & Authorization                        │
│  • Recipe CRUD with Forking                              │
│  • Social Features (Reviews, Comments)                   │
│  • Admin Reports                                         │
└─────────────────────────────────────────────────────────┘

Future Extensions (Architecture Ready):
┌─────────────────────────────────────────────────────────┐
│  • Dynamic Serving Size Calculator (UI Layer)            │
│  • Email Notifications (SMTP Integration)                │
│  • Recipe Image Uploads (File Storage)                   │
│  • Advanced Search (Full-Text Search)                    │
│  • Meal Planning (New Blueprint)                         │
│  • Grocery Lists (New Blueprint)                         │
│  • API Endpoints (REST API Blueprint)                    │
│  • Recipe Import/Export (CSV, JSON)                      │
│  • AI Recipe Suggestions (ML Integration)                │
└─────────────────────────────────────────────────────────┘
```

---

## File Structure

```
open-kitchen/
├── app/
│   ├── __init__.py          [Factory + Index Route]
│   ├── db.py                [DB Connection Management]
│   ├── schema.sql           [17 Tables + Seed Data]
│   │
│   ├── auth.py              [Blueprint: Authentication]
│   ├── recipes.py           [Blueprint: Recipe Management]
│   ├── dashboard.py         [Blueprint: User Dashboard]
│   ├── admin.py             [Blueprint: Admin Tools]
│   │
│   └── templates/
│       ├── base.html        [Master Template]
│       ├── index.html       [Landing Page]
│       ├── auth/            [Login, Register]
│       ├── recipes/         [Index, Create, View]
│       ├── dashboard/       [My Kitchen]
│       └── admin/           [Reports, User Mgmt]
│
├── instance/
│   └── community_kitchen.db [SQLite Database]
│
├── .flaskenv                [Flask Configuration]
├── requirements.txt         [Python Dependencies]
├── run.sh                   [Startup Script]
└── README.md                [Documentation]
```

---

## Deployment Considerations

```
┌─────────────────────────────────────────────────────────┐
│  CURRENT: Development Mode                               │
│  • Flask built-in server (Werkzeug)                      │
│  • SQLite file-based database                            │
│  • Debug mode enabled                                    │
│  • Port 8080, Host 0.0.0.0                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  PRODUCTION: Recommended Setup                           │
│  • WSGI Server (Gunicorn, uWSGI)                         │
│  • Reverse Proxy (Nginx)                                 │
│  • PostgreSQL or MySQL (if scaling needed)               │
│  • Environment-based configuration                       │
│  • HTTPS with SSL certificates                           │
└─────────────────────────────────────────────────────────┘
```

---

## Summary

**Architecture Style:** Monolithic MVC (Model-View-Controller)
**Pattern:** Application Factory with Blueprint Modularity
**Database:** Relational (SQLite) with Foreign Key Integrity
**Authentication:** Session-based with role-based authorization
**Scalability:** Ready for PostgreSQL migration, API layer addition
**Design Philosophy:** Clean separation, extensibility, data integrity
