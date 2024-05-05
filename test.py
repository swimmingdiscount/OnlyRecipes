import unittest
from app import app, db
from app.models import RecipeRequest, Ingredient
from app.forms import RecipeRequestForm

class TestSearchFunctionality(unittest.TestCase):

    def setUp(self):
        # Set up test data
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Establish application context
        with app.app_context():
            db.create_all()

            # Add some test recipe requests
            recipe1 = RecipeRequest(title='Pancakes', description='Delicious pancakes recipe', meal_type='breakfast', user_id='1231')
            recipe2 = RecipeRequest(title='Spaghetti Carbonara', description='Classic Italian pasta dish', meal_type='dinner', user_id='12421')
            db.session.add_all([recipe1, recipe2])
            db.session.commit()

            # Add ingredients to recipes
            ingredient1 = Ingredient(name='Flour')
            ingredient2 = Ingredient(name='Eggs')
            ingredient3 = Ingredient(name='Milk')
            ingredient4 = Ingredient(name='Spaghetti')
            ingredient5 = Ingredient(name='Bacon')
            ingredient6 = Ingredient(name='Egg yolk')
            recipe1.ingredients.extend([ingredient1, ingredient2, ingredient3])
            recipe2.ingredients.extend([ingredient4, ingredient5, ingredient6])
            db.session.commit()

    def tearDown(self):
        # Clean up database session and drop all tables
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_search_by_ingredient(self):
        # Test searching for recipes by ingredient
        response = self.client.get('/search?ingredient=Eggs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pancakes', response.data)
        self.assertNotIn(b'Spaghetti Carbonara', response.data)

    def test_search_by_ingredient_and_meal_type(self):
        # Test searching for recipes by ingredient and meal type
        response = self.client.get('/search?ingredient=Bacon&meal_type=lunch')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Pancakes', response.data)
        self.assertIn(b'Spaghetti Carbonara', response.data)

    def test_search_no_results(self):
        # Test searching with an ingredient that doesn't exist in any recipe
        response = self.client.get('/search?ingredient=Chicken')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Pancakes', response.data)
        self.assertNotIn(b'Spaghetti Carbonara', response.data)
        self.assertIn(b'No recipes found.', response.data)

if __name__ == '__main__':
    unittest.main()
