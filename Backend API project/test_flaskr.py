import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format('postgres:mb@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Where is New York city located?',
            'answer': 'USA',
            'category': 3,
            'difficulty': 1
        }

        self.bad_question_request = {
            'question': 'Where is New York city located?',
            'answer': 'USA',
            'category': 3,
            'difficulty': []
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        """Test successful request to get categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test_404_not_found_when_request_categories(self):
        """Test error 404 when get request for categories is incorrectly given"""
        res = self.client().get('/categories/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_questions(self):
        """Test successful request to get questions"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_404_if_pagination_renders_no_questions(self):
        """Test 404 error if a selected page in pagination does not display any questions"""
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')
        
    def test_delete_question(self):
        """Test success of deleting a selected question by id"""
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], 5)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        """Test error 422 for unprocessible request when a question does not exist"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 1000).one_or_none()

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
        self.assertEqual(question, None)

    def test_create_question(self):
        """Test success of creating a new question"""
        res = self.client().post('/questions/add', json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_422_if_create_question_fails(self):
        """Test error 422 if request is unprocessable"""
        res = self.client().post('/questions/add', json = self.bad_question_request)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
        

    def test_search_question_by_key_word(self):
        """Test success of search for questions by key word"""
        res = self.client().post('/questions', json={'searchTerm': 'Title'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)

    def test_404_if_search_key_word_is_none(self):
        """Test 404 error search by key word has None value"""
        res = self.client().post('/questions', json={'searchTerm': None})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_questions_by_category_id(self):
        """Test success of get request for questions by category id"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 1)

    def test_404_if_questions_by_category_id_not_found(self):
        """Test 404 error if questions by category id are not found"""
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_random_quiz_question(self):
        """Test successful response of a random question for a quiz"""
        res = self.client().post('/quizzes', json = {'previous_questions': [], 'quiz_category': {'id': 1}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_404_if_no_quiz_question_found(self):
        """Test 404 error if no question found"""
        res = self.client().post('/quizzes', json = {'previous_questions': [], 'quiz_category': {'id': 10}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()