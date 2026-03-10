# Open Kitchen – Class & Sequence Diagrams

## 1. Class Diagram

The class diagram below covers every model class, the Flask blueprints, and the
key relationships derived from the database schema and Python source code.

```mermaid
classDiagram
    %% ── Blueprint / Controller layer ──────────────────────────────────────────
    class AuthBlueprint {
        +register()
        +login()
        +logout()
        +load_logged_in_user()
        +login_required(view)
        +curator_required(view)
    }

    class RecipesBlueprint {
        +index()
        +view(id)
        +create()
        +edit_ingredients(id)
        +edit_instructions(id)
        +delete_ingredient(id)
        +delete_instruction(id)
        +fork(id)
        +save(id)
    }

    class DashboardBlueprint {
        +index()
    }

    class AdminBlueprint {
        +index()
        +users()
        +toggle_notifications(id)
        +most_forked()
        +allergen_audit()
        +user_activity()
        +units()
        +add_unit()
    }

    %% ── Model layer ────────────────────────────────────────────────────────────
    class User {
        +int id
        +str username
        +str email
        +str password_hash
        +int role_id
        +int notifications_enabled
        +datetime created_at
        +datetime updated_at
        +create(username, email, password, role_id)$
        +get_by_id(user_id)$
        +get_by_username(username)$
        +get_all()$
        +verify_password(user, password)$
        +toggle_notifications(user_id)$
    }

    class Role {
        +int id
        +str name
        +get_all()$
        +get_by_name(name)$
    }

    class Recipe {
        +int id
        +str title
        +str description
        +str template_type
        +int author_id
        +int base_servings
        +int prep_time_minutes
        +int cook_time_minutes
        +int parent_recipe_id
        +int is_public
        +datetime created_at
        +datetime updated_at
        +create(title, description, template_type, author_id, ...)$
        +get_by_id(recipe_id)$
        +get_all_public(filters)$
        +get_by_author(author_id)$
        +get_forked_by_author(author_id)$
        +fork(recipe_id, author_id, username)$
        +get_recent(limit)$
        +get_stats()$
    }

    class Ingredient {
        +int id
        +int recipe_id
        +str name
        +float quantity
        +int unit_id
        +int allergen_id
        +get_by_recipe(recipe_id)$
        +copy_for_recipe(source_recipe_id, target_recipe_id)$
    }

    class Instruction {
        +int id
        +int recipe_id
        +int step_number
        +str content
        +get_by_recipe(recipe_id)$
        +copy_for_recipe(source_recipe_id, target_recipe_id)$
    }

    class Review {
        +int id
        +int recipe_id
        +int user_id
        +int rating
        +str comment
        +datetime created_at
        +get_by_recipe(recipe_id)$
    }

    class Comment {
        +int id
        +int recipe_id
        +int user_id
        +str content
        +datetime created_at
        +get_by_recipe(recipe_id)$
    }

    class SavedRecipe {
        +int user_id
        +int recipe_id
        +datetime saved_at
        +get_by_user(user_id)$
        +is_saved(user_id, recipe_id)$
        +save(user_id, recipe_id)$
        +unsave(user_id, recipe_id)$
    }

    class Unit {
        +int id
        +str name
        +str abbreviation
        +get_all()$
        +create(name, abbreviation)$
    }

    class Category {
        +int id
        +str name
        +get_all()$
    }

    class Tag {
        +int id
        +str name
        +get_all()$
    }

    class Allergen {
        +int id
        +str name
        +get_all()$
    }

    class Notification {
        +int id
        +int user_id
        +str type
        +int reference_id
        +str message
        +int is_read
        +datetime created_at
        +create(user_id, type, reference_id, message)$
        +get_by_user(user_id, limit)$
    }

    class ActivityLog {
        +int id
        +int user_id
        +str action_type
        +str entity_type
        +int entity_id
        +datetime created_at
        +log(user_id, action_type, entity_type, entity_id)$
        +get_user_activity_report(days)$
    }

    class Report {
        +most_forked_recipes()$
        +recipes_with_allergen(allergen_id)$
    }

    class Friendship {
        +int id
        +int requester_id
        +int addressee_id
        +str status
        +datetime created_at
    }

    %% ── Blueprint ↔ Model dependencies ────────────────────────────────────────
    AuthBlueprint ..> User : uses
    RecipesBlueprint ..> Recipe : uses
    RecipesBlueprint ..> Ingredient : uses
    RecipesBlueprint ..> Instruction : uses
    RecipesBlueprint ..> Review : uses
    RecipesBlueprint ..> Comment : uses
    RecipesBlueprint ..> SavedRecipe : uses
    RecipesBlueprint ..> Unit : uses
    RecipesBlueprint ..> Allergen : uses
    RecipesBlueprint ..> Category : uses
    RecipesBlueprint ..> Tag : uses
    RecipesBlueprint ..> ActivityLog : uses
    DashboardBlueprint ..> Recipe : uses
    DashboardBlueprint ..> SavedRecipe : uses
    DashboardBlueprint ..> Notification : uses
    AdminBlueprint ..> User : uses
    AdminBlueprint ..> Unit : uses
    AdminBlueprint ..> Allergen : uses
    AdminBlueprint ..> ActivityLog : uses
    AdminBlueprint ..> Report : uses

    %% ── Model associations (mirrors DB foreign keys) ──────────────────────────
    User "1" --> "1" Role : has role
    User "1" --> "0..*" Recipe : authors
    User "1" --> "0..*" Review : writes
    User "1" --> "0..*" Comment : posts
    User "1" --> "0..*" SavedRecipe : saves
    User "1" --> "0..*" Notification : receives
    User "1" --> "0..*" ActivityLog : generates
    User "1" --> "0..*" Friendship : initiates (requester)
    User "1" --> "0..*" Friendship : receives (addressee)

    Recipe "1" --> "0..*" Ingredient : contains
    Recipe "1" --> "0..*" Instruction : has steps
    Recipe "1" --> "0..*" Review : receives
    Recipe "1" --> "0..*" Comment : has
    Recipe "1" --> "0..*" SavedRecipe : saved by
    Recipe "0..1" --> "0..*" Recipe : forked as (parent_recipe_id)
    Recipe "0..*" --> "0..*" Category : classified in
    Recipe "0..*" --> "0..*" Tag : tagged with

    Ingredient --> Unit : measured in
    Ingredient --> "0..1" Allergen : may contain
```

---

## 2. Sequence Diagrams

### 2a. User Registration

```mermaid
sequenceDiagram
    actor Browser
    participant AuthBP as Auth Blueprint
    participant UserModel as User Model
    participant DB as SQLite Database

    Browser->>AuthBP: GET /auth/register
    AuthBP-->>Browser: render register.html

    Browser->>AuthBP: POST /auth/register (username, email, password)
    AuthBP->>AuthBP: validate form fields
    AuthBP->>UserModel: create(username, email, password)
    UserModel->>UserModel: generate_password_hash(password)
    UserModel->>DB: INSERT INTO users (username, email, password_hash, role_id=1)
    DB-->>UserModel: lastrowid
    UserModel->>DB: SELECT user WHERE username=?
    DB-->>UserModel: user row
    UserModel-->>AuthBP: user object
    AuthBP-->>Browser: redirect → /auth/login
```

---

### 2b. User Login

```mermaid
sequenceDiagram
    actor Browser
    participant AuthBP as Auth Blueprint
    participant UserModel as User Model
    participant Session as Flask Session
    participant DB as SQLite Database

    Browser->>AuthBP: GET /auth/login
    AuthBP-->>Browser: render login.html

    Browser->>AuthBP: POST /auth/login (username, password)
    AuthBP->>UserModel: get_by_username(username)
    UserModel->>DB: SELECT user JOIN roles WHERE username=?
    DB-->>UserModel: user row (with role_name)
    UserModel-->>AuthBP: user object

    alt user not found
        AuthBP-->>Browser: flash "Incorrect username" → render login.html
    else password wrong
        AuthBP->>UserModel: verify_password(user, password)
        UserModel-->>AuthBP: False
        AuthBP-->>Browser: flash "Incorrect password" → render login.html
    else credentials valid
        AuthBP->>UserModel: verify_password(user, password)
        UserModel-->>AuthBP: True
        AuthBP->>Session: session['user_id'] = user.id
        AuthBP-->>Browser: redirect → /
    end
```

---

### 2c. Recipe Creation

```mermaid
sequenceDiagram
    actor Browser
    participant RecipesBP as Recipes Blueprint
    participant RecipeModel as Recipe Model
    participant ActivityLogModel as ActivityLog Model
    participant DB as SQLite Database

    Browser->>RecipesBP: GET /recipes/create
    RecipesBP->>DB: Category.get_all(), Tag.get_all()
    DB-->>RecipesBP: categories, tags
    RecipesBP-->>Browser: render create.html

    Browser->>RecipesBP: POST /recipes/create (title, template_type, servings, …)
    RecipesBP->>RecipesBP: validate (title required, template_type valid)
    RecipesBP->>RecipeModel: create(title, description, template_type, author_id, …)
    RecipeModel->>DB: INSERT INTO recipes (…)
    DB-->>RecipeModel: new recipe_id
    RecipeModel-->>RecipesBP: recipe_id

    RecipesBP->>DB: INSERT INTO recipe_categories (recipe_id, category_id) for each
    RecipesBP->>DB: INSERT INTO recipe_tags (recipe_id, tag_id) for each
    RecipesBP->>DB: COMMIT

    RecipesBP->>ActivityLogModel: log(user_id, "created", "recipe", recipe_id)
    ActivityLogModel->>DB: INSERT INTO activity_logs (…)

    RecipesBP-->>Browser: redirect → /recipes/<id>/ingredients
```

---

### 2d. Recipe Forking

```mermaid
sequenceDiagram
    actor Browser
    participant RecipesBP as Recipes Blueprint
    participant RecipeModel as Recipe Model
    participant IngredientModel as Ingredient Model
    participant InstructionModel as Instruction Model
    participant NotificationModel as Notification Model
    participant ActivityLogModel as ActivityLog Model
    participant DB as SQLite Database

    Browser->>RecipesBP: POST /recipes/<id>/fork
    RecipesBP->>RecipeModel: fork(recipe_id, author_id, username)

    RecipeModel->>DB: SELECT recipe WHERE id=?
    DB-->>RecipeModel: original recipe row

    RecipeModel->>DB: INSERT INTO recipes (title+" (Fork)", …, parent_recipe_id=id)
    DB-->>RecipeModel: new_recipe_id

    RecipeModel->>IngredientModel: copy_for_recipe(original_id, new_recipe_id)
    IngredientModel->>DB: SELECT ingredients WHERE recipe_id=original_id
    IngredientModel->>DB: INSERT INTO ingredients (new_recipe_id, …) for each

    RecipeModel->>InstructionModel: copy_for_recipe(original_id, new_recipe_id)
    InstructionModel->>DB: SELECT instructions WHERE recipe_id=original_id
    InstructionModel->>DB: INSERT INTO instructions (new_recipe_id, …) for each

    RecipeModel->>DB: INSERT INTO recipe_categories SELECT new_recipe_id, category_id …
    RecipeModel->>DB: INSERT INTO recipe_tags SELECT new_recipe_id, tag_id …

    RecipeModel->>ActivityLogModel: log(author_id, "forked", "recipe", new_recipe_id)
    ActivityLogModel->>DB: INSERT INTO activity_logs (…)

    alt original author ≠ forking user
        RecipeModel->>NotificationModel: create(original_author_id, "fork_created", …)
        NotificationModel->>DB: INSERT INTO notifications (…)
    end

    RecipeModel->>DB: COMMIT
    RecipeModel-->>RecipesBP: new_recipe_id

    RecipesBP-->>Browser: flash "Recipe forked!" → redirect → /recipes/<new_id>
```

---

### 2e. Viewing a Recipe (with dynamic ingredient scaling)

```mermaid
sequenceDiagram
    actor Browser
    participant RecipesBP as Recipes Blueprint
    participant RecipeModel as Recipe Model
    participant IngredientModel as Ingredient Model
    participant InstructionModel as Instruction Model
    participant ReviewModel as Review Model
    participant CommentModel as Comment Model
    participant SavedRecipeModel as SavedRecipe Model
    participant DB as SQLite Database

    Browser->>RecipesBP: GET /recipes/<id>[?servings=N]
    RecipesBP->>RecipeModel: get_by_id(id)
    RecipeModel->>DB: SELECT recipe JOIN users WHERE id=?
    DB-->>RecipeModel: recipe row
    RecipeModel-->>RecipesBP: recipe

    RecipesBP->>IngredientModel: get_by_recipe(id)
    IngredientModel->>DB: SELECT ingredients JOIN units LEFT JOIN allergens WHERE recipe_id=?
    DB-->>IngredientModel: ingredient rows
    IngredientModel-->>RecipesBP: ingredients

    RecipesBP->>InstructionModel: get_by_recipe(id)
    InstructionModel->>DB: SELECT instructions WHERE recipe_id=? ORDER BY step_number
    DB-->>InstructionModel: instruction rows

    RecipesBP->>ReviewModel: get_by_recipe(id)
    ReviewModel->>DB: SELECT reviews JOIN users WHERE recipe_id=?
    DB-->>ReviewModel: review rows

    RecipesBP->>CommentModel: get_by_recipe(id)
    CommentModel->>DB: SELECT comments JOIN users WHERE recipe_id=?
    DB-->>CommentModel: comment rows

    RecipesBP->>DB: SELECT categories WHERE recipe_id=?
    RecipesBP->>DB: SELECT tags WHERE recipe_id=?

    opt user is logged in
        RecipesBP->>SavedRecipeModel: is_saved(user_id, recipe_id)
        SavedRecipeModel->>DB: SELECT 1 FROM saved_recipes WHERE user_id=? AND recipe_id=?
        DB-->>SavedRecipeModel: row or None
        SavedRecipeModel-->>RecipesBP: True / False
    end

    note over Browser,RecipesBP: Dynamic scaling (client-side JS):<br/>scaled_qty = (requested_servings / base_servings) × original_qty

    RecipesBP-->>Browser: render view.html (recipe, ingredients, instructions, reviews, …)
```

# Use Case diagrams

---

## 2. Use Case Diagrams

### 2a. Recipe Authoring & Forking

```mermaid
usecaseDiagram
  actor Guest as G
  actor User as U
  actor Curator as C

  rectangle "Open Kitchen" {
    (Register Account) as UC_Register
    (Log In) as UC_Login

    (Browse Public Recipes) as UC_Browse
    (View Recipe) as UC_View
    (Scale Ingredients by Servings) as UC_Scale

    (Create Recipe) as UC_Create
    (Assign Categories/Tags) as UC_TagCat
    (Add/Edit Ingredients) as UC_EditIng
    (Add/Edit Instructions) as UC_EditInst

    (Fork Recipe) as UC_Fork
    (Copy Ingredients) as UC_CopyIng
    (Copy Instructions) as UC_CopyInst
    (Notify Original Author) as UC_Notify
    (Log Activity) as UC_Log
  }

  G --> UC_Register
  G --> UC_Login
  G --> UC_Browse
  G --> UC_View

  U --> UC_Browse
  U --> UC_View
  U --> UC_Create
  U --> UC_Fork

  C --> UC_Create

  UC_View .> UC_Scale : <<include>>

  UC_Create .> UC_TagCat : <<include>>
  UC_Create .> UC_EditIng : <<include>>
  UC_Create .> UC_EditInst : <<include>>
  UC_Create .> UC_Log : <<include>>

  UC_Fork .> UC_CopyIng : <<include>>
  UC_Fork .> UC_CopyInst : <<include>>
  UC_Fork .> UC_Log : <<include>>

  UC_Notify ..> UC_Fork : <<extend>>
