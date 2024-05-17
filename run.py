from app import create_app, db
from app.models import User, RecipeRequest, Recipe, RecipeReply, Ingredient, recipe_request_ingredients, recipe_ingredients, recipe_reply_ingredients

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    print("Dropped all tables.")

    # Create all tables
    db.create_all()
    print("Created all tables.")

    # Insert sample data
    # Add ingredients
    ingredient1 = Ingredient(name='egg')
    ingredient2 = Ingredient(name='milk')
    db.session.add(ingredient1)
    db.session.add(ingredient2)
    db.session.commit()

    # Add a sample user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Add recipe requests
    recipe_request1 = RecipeRequest(title='Eggs Benedict', description='How to make Eggs Benedict', meal_type='breakfast', user_id=user.id)
    db.session.add(recipe_request1)
    db.session.commit()

    # Add recipes
    recipe1 = Recipe(title='Scrambled Eggs', instructions='Mix eggs and milk, then scramble.', meal_type='breakfast', user_id=user.id)
    db.session.add(recipe1)
    db.session.commit()

    # Add replies
    recipe_reply1 = RecipeReply(content='Add some cheese for better flavor.', request_id=recipe_request1.id, user_id=user.id)
    db.session.add(recipe_reply1)
    db.session.commit()

    # Associate ingredients with recipes, requests, and replies
    recipe_request1.ingredients.append(ingredient1)
    recipe1.ingredients.append(ingredient1)
    recipe1.ingredients.append(ingredient2)
    recipe_reply1.ingredients.append(ingredient1)
    db.session.commit()

    print("Inserted sample data.")
