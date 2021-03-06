import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

from settings import DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_categories_not_allowed(self):
        res = self.client().delete('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)


    def test_delete_question(self):
        question = Question(question="is a test?", answer="yes", category=2, difficulty=1)
        question.insert()
        question_id = question.id

        questions_before = Question.query.all()

        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        questions_after = Question.query.all()
        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertTrue(len(questions_before) - len(questions_after) == 1)
        self.assertEqual(question, None)



    def test_404_delete_question_not_found(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_question(self):
        new_question = {
            'question': 'hello',
            'answer': 'hi',
            'difficulty': 1,
            'category': 1
        }
        
        question_before = len(Question.query.all())
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        question_after = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question_after, question_before + 1)

    def test_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['searched_question'])
        self.assertIsNotNone(data['total_questions'])

    def test_404_search_question(self):
        res = self.client().post('/questions/search', json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])


    def test_404_get_category_questions(self):
        res = self.client().get('categories/a/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "resource not found")

    
    # def test_get_quiz(self):
    #     quiz = {
    #         'previous_questions': [13],
    #         'quiz_category': {
    #             'type': 'Entertainment',
    #             'id': '3'
    #         }
    #     }
    #     res = self.client().post('/quiz', json=quiz)
    #     data = json.loads(res.data)
    #     print(res)
    #     print(data)
       
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data['success'], True)
    #     self.assertEqual(data['question']['category'], '3')

    def test_404_get_quiz(self):
        quiz = {
            'previous_questions': [6],
            'quiz_category': {
                'type': 'XXX',
                'id': 'X'
            }
        }
        res = self.client().post('/quiz', json=quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()