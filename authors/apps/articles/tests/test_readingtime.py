from django.test import TestCase
from authors.apps.articles.models import Article


class TestReadingTime(TestCase):
    body = "one two three\n four five six \n"

    def test_correct_time_returned(self):
        time = Article.article_reading_time(self.body * 200)
        self.assertEqual(time, '4 minutes')

    def test_correct_time_less_than_2_minutes(self):
        time = Article.article_reading_time(self.body * 75)
        self.assertEqual(time, 'About 1 minute')

    def test_correct_time_less_than_1_minute(self):
        time = Article.article_reading_time(self.body * 20)
        self.assertEqual(time, 'Less than a minute')
