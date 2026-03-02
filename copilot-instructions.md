# instructions.md  

## Collaborative Recipe Management System – Copilot Implementation Guide

---

## 1. Project Overview

You are building a **Collaborative Recipe Management System** designed specifically for a **Community or Family environment**.

The system must treat recipes as **structured, dynamic, and interactive data**, not static text entries.

This platform replaces disorganized notebooks, scattered screenshots, and group chat messages with a centralized, searchable, and socially interactive cooking workspace.

---

## 2. Core Value Proposition

### Organizational Impact

The system must help families or small communities:

- Eliminate duplicate recipes and inconsistent versions
- Track modifications and improvements over time
- Scale recipes accurately for events and gatherings
- Filter recipes based on dietary needs or time constraints
- Maintain allergen visibility for safety

### Social Collaboration

The platform should:

- Encourage sharing of tips and improvements
- Allow recipe forking and personalization
- Notify users when others interact with their recipes
- Provide feedback via ratings and comments
- Make cooking a shared digital experience

### Why This Is Better Than a Physical Notebook

| Physical Notebook | This System |
|-------------------|------------|
| Static text | Dynamic scaling |
| No version control | Forking & version history |
| Hard to search | Multi-criteria filtering |
| No collaboration | Reviews, comments, notifications |
| No safety controls | Allergen auditing |
| Easily lost | Centralized and backed up |

---

## 3. System Architecture Requirements

The solution must:

- Use authenticated user accounts
- Implement role-based access control
- Use relational data modeling
- Support notification mechanisms
- Maintain referential integrity for recipe forking
- Enable dynamic calculations (ingredient scaling)

---

## 4. User Roles

### 4.1 Contributor

A standard authenticated user.

**Capabilities:**

- Create recipes
- View recipes
- Fork recipes
- Leave comments and tips
- Submit star ratings
- Save recipes
- View personal dashboard

**Restrictions:**

- Cannot manage users
- Cannot modify lookup lists
- Cannot generate system-wide reports

---

### 4.2 Curator (Administrator)

Full administrative privileges.

**Capabilities:**

- Create, edit, delete users
- Manage user notification email settings
- Manage lookup lists (e.g., allowed units such as grams, ounces, cups)
- Generate system activity reports
- Audit allergens
- View user contribution statistics

---

## 5. Functional Requirements

### 5.1 Authenticated User Roles

- Must implement secure authentication
- Must enforce role-based authorization
- Must store user metadata (email, notification preferences)

---

### 5.2 Recipe Templates

The system must support at least two distinct template types.

---

#### A. Standard Recipe

**Required fields:**

- Title
- Description
- Ingredients (item + quantity + unit)
- Step-by-step instructions
- Prep time
- Cook time
- Category (e.g., Appetizer, Dessert)
- Dietary tags (e.g., Nut-Free, Keto)
- Allergen indicators
- Base serving size (required for scaling)

---

#### B. Quick Tip

**Required fields:**

- Title
- Short explanation
- Optional related ingredient
- Optional category tag

Quick Tips must be lightweight and distinct from full recipes.

---

## 6. Dynamic Ingredient Scaling

Users must be able to:

1. View a recipe
2. Enter desired serving size
3. Automatically recalculate ingredient quantities

**Implementation Requirements:**

- Store base serving size
- Store numeric quantities in structured format
- Perform scaling calculation dynamically
- Never overwrite base values in database

**Formula Example:**

`scaled_quantity = (requested_servings / base_servings) * original_quantity`

## 7. Recipe Forking & Versioning

### Forking Requirements

Forking must:

- Create a new recipe record  
- Maintain a foreign key reference to the original recipe  
- Track original author  
- Allow full editing of forked version  
- Preserve link to master recipe  

### Version Tracking Requirements

Version tracking must allow:

- Viewing lineage (Original → Fork → Fork of Fork)  
- Identifying most forked source recipe  
- Counting fork relationships for reporting  

---

## 8. Personalized Dashboard – "My Kitchen"

Each authenticated user must have a dashboard displaying:

- Authored recipes  
- Forked recipes  
- Saved recipes  
- Recent activity notifications  
- Pending reviews or comments  

The dashboard should serve as the user’s central workspace.

---

## 9. Search and Filtering

The system must allow multi-criteria filtering by:

- Category  
- Dietary tag  
- Total time (prep + cook)  
- Author  
- Allergen presence  

Search must support:

- Text search (title, description)  
- Tag-based filtering  
- Combined filters (AND conditions)  

---

## 10. Social Feedback Loop

Users must be able to:

- Leave star rating (1–5)  
- Leave text review  
- Comment on recipes  

The system must:

- Notify recipe owner upon new review or comment  
- Display average rating  
- Prevent duplicate reviews from same user per recipe (unless updating)  

---

## 11. Automated Notifications

The system must support event-triggered notifications.

### Trigger Events

- Recipe forked  
- New review posted  
- Comment added  
- Admin updates affecting user settings  

### Notification Channels

- Email (required)  
- Optional in-app notification feed  

The Curator must be able to:

- Manage user email settings  
- Enable/disable notification preferences  

---

## 12. Curator Reports

The Curator must be able to generate the following reports:

### 12.1 Most Forked Recipes

- Ranked list  
- Include fork count  
- Identify original creator  

### 12.2 Allergen Audit Report

- Filter recipes containing specific allergen (e.g., Peanuts)  
- Used for safety and dietary compliance  

### 12.3 User Activity Report

- Recipes created in last 30 days  
- Forks created in last 30 days  
- Most active contributors  

Reports must be exportable (CSV preferred).

---

## 13. Data Model Expectations

### Suggested Core Entities

- User  
- Role  
- Recipe  
- RecipeTemplateType  
- Ingredient  
- Unit (lookup table, Curator-managed)  
- Tag  
- Category  
- Allergen  
- Review  
- Comment  
- Notification  
- ForkRelationship  
- SavedRecipe  

Relationships must maintain referential integrity.

---

## 14. Non-Functional Requirements

- Clean separation of concerns  
- Scalable architecture  
- Clear API boundaries (if using services)  
- Input validation for ingredient quantities  
- Secure authentication and authorization  
- Responsive UI design  
- Maintainable and modular codebase  

---

## 15. Success Criteria

The project succeeds if:

- Recipes behave as structured data, not text blobs  
- Users can scale ingredients instantly  
- Forking maintains lineage  
- Social feedback creates engagement  
- Admin can audit allergens and activity  
- Families prefer this system over a shared notebook  

---

## 16. Implementation Philosophy

### Prioritize:

- Data integrity over UI polish  
- Clear relationships over shortcuts  
- Extensibility for future features (meal planning, grocery lists, AI suggestions)  
- Clean, testable logic for scaling and versioning  

This is not a static content app.  
It is a collaborative, evolving culinary knowledge system designed for small communities.


--- 

# SQlite Implementation Notes (no password)

# 17. SQLite Database Design

## 17.1 High-Level Database Overview

**Database Name:** `community_kitchen.db`  
**Database Engine:** SQLite  
**Foreign Key Enforcement:** Enabled (`PRAGMA foreign_keys = ON;`)  

### Design Goals

The database must:

- Support authenticated roles (Contributor, Curator)
- Enable structured recipe storage (not text blobs)
- Support dynamic ingredient scaling
- Track recipe forking and lineage
- Enable social collaboration (reviews, comments, sharing)
- Support notifications and reporting
- Maintain referential integrity
- Be normalized and migration-ready (future PostgreSQL/MySQL)

---

## 17.2 Table Overview

### Authentication & Authorization
- `users`
- `roles`

### Social Graph
- `friendships`

### Core Recipe System
- `recipes`
- `ingredients`
- `instructions`
- `units`
- `categories`
- `recipe_categories`
- `tags`
- `recipe_tags`
- `allergens`

### Social Interaction
- `reviews`
- `comments`
- `saved_recipes`

### System Intelligence & Activity
- `notifications`
- `activity_logs`

---

# 17.3 Table Definitions & Fields

---

## 1. roles

Defines system access levels.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY |
| name | TEXT | UNIQUE NOT NULL |

Seed values:
- 1 → Contributor  
- 2 → Curator  

---

## 2. users

Stores authenticated users.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| username | TEXT | UNIQUE NOT NULL |
| email | TEXT | UNIQUE NOT NULL |
| password_hash | TEXT | NOT NULL |
| role_id | INTEGER | NOT NULL, FK → roles(id) |
| notifications_enabled | INTEGER | DEFAULT 1 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | |

---

## 3. friendships

Supports community-based sharing.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| requester_id | INTEGER | FK → users(id) |
| addressee_id | INTEGER | FK → users(id) |
| status | TEXT | CHECK(status IN ('pending','accepted','blocked')) |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

Purpose:
- Enables friend-only sharing
- Supports collaborative environment
- Restricts visibility where required

---

# 17.4 Core Recipe Structure

---

## 4. recipes

Stores all recipe metadata and fork relationships.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| title | TEXT | NOT NULL |
| description | TEXT | |
| template_type | TEXT | CHECK(template_type IN ('standard','quick_tip')) |
| author_id | INTEGER | NOT NULL, FK → users(id) |
| base_servings | INTEGER | |
| prep_time_minutes | INTEGER | |
| cook_time_minutes | INTEGER | |
| parent_recipe_id | INTEGER | FK → recipes(id) |
| is_public | INTEGER | DEFAULT 1 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| updated_at | DATETIME | |

Key Design Decisions:

- `parent_recipe_id` enables recipe forking and lineage tracking.
- `template_type` differentiates Standard Recipes and Quick Tips.
- Quick Tips may have NULL prep/cook times.

---

## 5. ingredients

Structured ingredient storage for scaling.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| recipe_id | INTEGER | FK → recipes(id) |
| name | TEXT | NOT NULL |
| quantity | REAL | NOT NULL |
| unit_id | INTEGER | FK → units(id) |
| allergen_id | INTEGER | FK → allergens(id), NULLABLE |

Important:
- Quantities stored as REAL for dynamic scaling.
- No ingredient data stored as JSON blobs.

---

## 6. instructions

Step-by-step instructions for Standard Recipes.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| recipe_id | INTEGER | FK → recipes(id) |
| step_number | INTEGER | NOT NULL |
| content | TEXT | NOT NULL |

---

## 7. units (Curator Managed Lookup)

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | UNIQUE NOT NULL |
| abbreviation | TEXT | |

Managed only by Curator.

---

# 17.5 Classification & Filtering

---

## 8. categories

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | UNIQUE NOT NULL |

---

## 9. recipe_categories (Many-to-Many)

| Field | Type | Constraints |
|-------|------|------------|
| recipe_id | INTEGER | FK → recipes(id) |
| category_id | INTEGER | FK → categories(id) |

Composite primary key recommended.

---

## 10. tags

Dietary or descriptive labels.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | UNIQUE NOT NULL |

Examples:
- Keto
- Nut-Free
- Vegan

---

## 11. recipe_tags (Many-to-Many)

| Field | Type | Constraints |
|-------|------|------------|
| recipe_id | INTEGER | FK → recipes(id) |
| tag_id | INTEGER | FK → tags(id) |

---

## 12. allergens

Used for safety auditing.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | UNIQUE NOT NULL |

---

# 17.6 Social Interaction

---

## 13. reviews

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| recipe_id | INTEGER | FK → recipes(id) |
| user_id | INTEGER | FK → users(id) |
| rating | INTEGER | CHECK(rating BETWEEN 1 AND 5) |
| comment | TEXT | |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

Recommended constraint:

- UNIQUE(recipe_id, user_id)

Prevents duplicate reviews.

---

## 14. comments

General discussion threads.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| recipe_id | INTEGER | FK → recipes(id) |
| user_id | INTEGER | FK → users(id) |
| content | TEXT | NOT NULL |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

---

## 15. saved_recipes

User favorites.

| Field | Type | Constraints |
|-------|------|------------|
| user_id | INTEGER | FK → users(id) |
| recipe_id | INTEGER | FK → recipes(id) |
| saved_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

Composite primary key recommended.

---

# 17.7 Notifications & Reporting

---

## 16. notifications

Event-based alerts.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | FK → users(id) |
| type | TEXT | |
| reference_id | INTEGER | |
| message | TEXT | |
| is_read | INTEGER | DEFAULT 0 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

Example Types:
- fork_created
- review_posted
- comment_added

---

## 17. activity_logs

Tracks system activity for Curator reports.

| Field | Type | Constraints |
|-------|------|------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | FK → users(id) |
| action_type | TEXT | |
| entity_type | TEXT | |
| entity_id | INTEGER | |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |

Used for:

- Most Forked Recipes
- Allergen audits
- User activity reports (30-day window)
- Contribution tracking

---

# 17.8 Forking & Lineage Strategy

Forking is implemented via:

- `recipes.parent_recipe_id`
- Counting child recipes grouped by parent
- Activity log tracking

This allows:

- Lineage visualization (Original → Fork → Fork of Fork)
- Popularity ranking
- Full auditability of changes

---

# 17.9 Data Integrity Principles

- Foreign keys strictly enforced
- Lookup tables managed by Curator only
- No destructive cascade deletes (soft delete preferred)
- Quantities stored as REAL
- Serving size stored at recipe level
- Reviews limited to one per user per recipe
- Structured relational modeling (no embedded JSON for ingredients)

---

# 17.10 Architectural Readiness

Although built on SQLite, this schema is:

- Fully normalized
- Migration-ready
- Structured for future scaling
- Compatible with cloud database transition

This design ensures structured collaboration, scalable recipe management, social engagement tracking, and administrative oversight within a small community or family operating environment.
