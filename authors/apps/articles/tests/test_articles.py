from django.test import TestCase
from rest_framework import status
from authors.apps.articles.tests import BaseTestCaseArticles
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Article


class ViewTest(BaseTestCaseArticles):

    def method_to_call_on_route(self, end_point, endpoint_data):
        response = self.client.post(end_point, endpoint_data, format="json" )
        return response

    def test_can_create_article(self):
        response = self.client.post('/api/articles/', self.article,
                                    format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_can_create_article_with_tags(self):
        self.assertEqual(self.response3.status_code, status.HTTP_201_CREATED)

    def test_can_get_article(self):
        result = self.client.get('/api/articles/{}/'
                                 .format(self.response.data['article']['slug']))
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_can_update_article(self):
        result = self.client.put('/api/articles/{}/'
                                 .format(self.response.data['article']['slug']),
                                 self.update_data, format="json")
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_can_delete_article(self):
        result = self.client.delete('/api/articles/{}/'
                                    .format(self.response.data['article']['slug']))
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)

    def test_can_not_edit_unless_author(self):
        response = self.client.put('/api/articles/{}/'.format("no-work"),
                                   self.update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_not_delete_unless_author(self):
        response = self.client.delete('/api/articles/{}/'.format("no-work"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_unique_slug(self):
        self.assertNotEqual(self.response, self.response1)

    def test_can_get_all_articles(self):
        self.client.post('/api/articles/', self.article, format="json")
        self.client.post('/api/articles/', self.article, format="json")
        response = self.client.get('/api/article/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_get_article_that_doesnot_exist(self):
        response = self.client.get('/api/articles/{}/'.format("no-work-here"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_get_all_tags(self):
        result = self.client.get('/api/tags/')
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_share_article(self):
        resp = self.method_to_call_on_route('/api/article/share/', self.share_data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_share_article_with_invalid_email(self):
        response = self.method_to_call_on_route('/api/article/share/', self.invalid_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_share_article_with_no_content(self):
        response = self.method_to_call_on_route('/api/article/share/', self.no_content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ArticlesModelTestCase(TestCase):
    """Class with tests to do with interacting with the article model"""

    def setUp(self):
        """Define the test variables"""
        self.user = User.objects.create_user(
            username="red", email="red@gmail.com", password="password"
        )
        self.profile = Profile.objects.get(user=self.user)
        self.old_count = Article.objects.count()
        self.article = Article.objects.create(
            title="Test article",
            description="description of test article",
            body="this is the body of test article",
            author=self.profile
        )

    def test_creation_of_article(self):
        """Test that an article can be created."""
        self.new_count = Article.objects.count()
        self.assertNotEqual(self.old_count, self.new_count)

    def test_get_an_article_by_anyone(self):
        """Test that an article can be returned."""
        article = self.article.get_article('test-article')
        self.assertEqual(article.description, "description of test article")

    def test_an_article_can_be_deleted(self):
        """Test that an article can be deleted."""
        self.article.delete_article(self.user.email, 'test-article')
        self.new_count = Article.objects.count()
        self.assertEqual(self.old_count, self.new_count)


    def test_get_article_by_authenticated_user(self):
        """Test that an authenticated user can get an article"""
        protected_article = self.article.get_user_article(
            self.user.email, 'test-article'
        )
        self.assertEqual(protected_article.description, "description of test article")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  