-- Open Kitchen Database Schema
-- SQLite Implementation with Foreign Key Support

PRAGMA foreign_keys = ON;

-- ========================================
-- Authentication & Authorization
-- ========================================

DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Seed roles
INSERT INTO roles (id, name) VALUES (1, 'Contributor');
INSERT INTO roles (id, name) VALUES (2, 'Curator');

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL DEFAULT 1,
    notifications_enabled INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- ========================================
-- Social Graph
-- ========================================

DROP TABLE IF EXISTS friendships;
CREATE TABLE friendships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER NOT NULL,
    addressee_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'accepted', 'blocked')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (addressee_id) REFERENCES users(id)
);

-- ========================================
-- Lookup Tables (Curator Managed)
-- ========================================

DROP TABLE IF EXISTS units;
CREATE TABLE units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    abbreviation TEXT
);

-- Seed common units
INSERT INTO units (name, abbreviation) VALUES 
    ('gram', 'g'),
    ('kilogram', 'kg'),
    ('ounce', 'oz'),
    ('pound', 'lb'),
    ('cup', 'cup'),
    ('tablespoon', 'tbsp'),
    ('teaspoon', 'tsp'),
    ('milliliter', 'ml'),
    ('liter', 'l'),
    ('piece', 'pc'),
    ('to taste', '');

DROP TABLE IF EXISTS allergens;
CREATE TABLE allergens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Seed common allergens
INSERT INTO allergens (name) VALUES 
    ('Peanuts'),
    ('Tree Nuts'),
    ('Milk'),
    ('Eggs'),
    ('Fish'),
    ('Shellfish'),
    ('Soy'),
    ('Wheat'),
    ('Gluten');

DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Seed common categories
INSERT INTO categories (name) VALUES 
    ('Appetizer'),
    ('Main Course'),
    ('Dessert'),
    ('Breakfast'),
    ('Lunch'),
    ('Dinner'),
    ('Snack'),
    ('Beverage'),
    ('Salad'),
    ('Soup'),
    ('Side Dish');

DROP TABLE IF EXISTS tags;
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- Seed common dietary tags
INSERT INTO tags (name) VALUES 
    ('Vegetarian'),
    ('Vegan'),
    ('Gluten-Free'),
    ('Dairy-Free'),
    ('Nut-Free'),
    ('Keto'),
    ('Paleo'),
    ('Low-Carb'),
    ('High-Protein'),
    ('Quick'),
    ('Easy');

-- ========================================
-- Core Recipe System
-- ========================================

DROP TABLE IF EXISTS recipes;
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    template_type TEXT NOT NULL CHECK(template_type IN ('standard', 'quick_tip')),
    author_id INTEGER NOT NULL,
    base_servings INTEGER,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    parent_recipe_id INTEGER,
    is_public INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (parent_recipe_id) REFERENCES recipes(id)
);

DROP TABLE IF EXISTS ingredients;
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit_id INTEGER NOT NULL,
    allergen_id INTEGER,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (allergen_id) REFERENCES allergens(id)
);

DROP TABLE IF EXISTS instructions;
CREATE TABLE instructions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

-- ========================================
-- Recipe Classification (Many-to-Many)
-- ========================================

DROP TABLE IF EXISTS recipe_categories;
CREATE TABLE recipe_categories (
    recipe_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, category_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

DROP TABLE IF EXISTS recipe_tags;
CREATE TABLE recipe_tags (
    recipe_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (recipe_id, tag_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- ========================================
-- Social Interaction
-- ========================================

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(recipe_id, user_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS saved_recipes;
CREATE TABLE saved_recipes (
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    saved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

-- ========================================
-- Notifications & Activity Tracking
-- ========================================

DROP TABLE IF EXISTS notifications;
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    reference_id INTEGER,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS activity_logs;
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ========================================
-- Indexes for Performance
-- ========================================

CREATE INDEX idx_recipes_author ON recipes(author_id);
CREATE INDEX idx_recipes_parent ON recipes(parent_recipe_id);
CREATE INDEX idx_recipes_template ON recipes(template_type);
CREATE INDEX idx_ingredients_recipe ON ingredients(recipe_id);
CREATE INDEX idx_instructions_recipe ON instructions(recipe_id);
CREATE INDEX idx_reviews_recipe ON reviews(recipe_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_comments_recipe ON comments(recipe_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_created ON activity_logs(created_at);
