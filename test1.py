import unittest
from app import app, db
from app.models import User, RecipeRequest, Ingredient, RecipeReply

class TestForum(unittest.TestCase):

    def setUp(self):
        # Set up test data
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # Clean up database session and drop all tables
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_multiple_users_same_username(self):
        # Test that two users cannot have the same username
        with self.app_context:
            user1 = User(username='testuser', email='test1@example.com')
            user1.set_password('testpassword')
            db.session.add(user1)
            db.session.commit()

            user2 = User(username='testuser', email='test2@example.com')
            user2.set_password('testpassword')
            db.session.add(user2)

            with self.assertRaises(Exception):
                db.session.commit()

    def test_multiple_requests_same_title(self):
        # Test that two recipe requests cannot have the same title
        with self.app_context:
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

            request1 = RecipeRequest(title='Test Recipe', description='This is a test', meal_type='dinner', author=user)
            db.session.add(request1)
            db.session.commit()

            request2 = RecipeRequest(title='Test Recipe', description='This is another test', meal_type='lunch', author=user)
            db.session.add(request2)

            with self.assertRaises(Exception):
                db.session.commit()

    def test_search_no_results(self):
        # Test searching with an ingredient that doesn't exist in any recipe
        with self.app_context:
            response = self.client.get('/search?ingredient=Chicken')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'No recipes found.', response.data)

    def test_search_multiple_results(self):
        # Test searching with an ingredient that exists in multiple recipes
        with self.app_context:
            ingredient = Ingredient(name='Chicken')
            db.session.add(ingredient)
            db.session.commit()

            user = User(username='testuser', email='test@example.com')
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

            request1 = RecipeRequest(title='Chicken Soup', description='This is a test', meal_type='dinner', author=user)
            request1.ingredients.append(ingredient)
            db.session.add(request1)

            request2 = RecipeRequest(title='Chicken Salad', description='This is another test', meal_type='lunch', author=user)
            request2.ingredients.append(ingredient)
            db.session.add(request2)

            db.session.commit()

            response = self.client.get('/search?ingredient=Chicken')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Chicken Soup', response.data)
            self.assertIn(b'Chicken Salad', response.data)

if __name__ == '__main__':
    unittest.main()
