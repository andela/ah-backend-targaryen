from authors.apps.articles.tests import BaseTestCaseArticles
from rest_framework import status


class ViewTestComments(BaseTestCaseArticles):

    def test_comment_creation(self):
        self.assertEqual(
            self.create_comment.status_code,status.HTTP_201_CREATED
        )

    def test_comment_retrieval(self):
        result = self.client.get(
            '/api/articles/{}/comments/'.format(
                self.create_article.data['article']['slug']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_comment_update(self):
        result = self.client.put(
            '/api/articles/{}/comments/{}/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            ),
            self.comment, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_comment_delete(self):
        result = self.client.delete(
            '/api/articles/{}/comments/{}/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("comment has been deleted successfully",
                      str(result.data['message']))
    
    def test_comment_delete_with_non_existent_article(self):
        result = self.client.delete(
            '/api/articles/no_article/comments/{}/'.format(
                self.create_comment.data['id']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The Article does not exist",
                      str(result.data['detail']))

    def test_thread_creation(self):
        result = self.client.post(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_thread_retrieval(self):
        result = self.client.get(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'],
                self.create_comment.data['id']
            )
        )
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    def test_create_comment_for_non_existent_article(self):
        result = self.client.post(
            '/api/articles/non-existent/comments/',
            self.comment, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The Article does not exist", str(result.data['detail']))

    def test_update_non_existent_comment(self):
        result = self.client.put(
            '/api/articles/{}/comments/{}/'.format(
                self.create_article.data['article']['slug'], int(100)
            ),
            self.comment, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The comment does not exist", str(result.data['detail']))

    def test_thread_creation_with_non_existent_article(self):
        result = self.client.post(
            '/api/articles/no-article/comments/{}/thread/'.format(
                self.create_comment.data['id']
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The Article does not exist", str(result.data['detail']))

    def test_thread_creation_with_non_existent_parent_comment(self):
        result = self.client.post(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'], int(30)
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("The parent comment does not exist",
                      str(result.data['detail']))

    def test_thread_creation_with_another_thread_as_parent(self):
        result = self.client.post(
            '/api/articles/{}/comments/{}/thread/'.format(
                self.create_article.data['article']['slug'],
                self.create_thread.data['id']
            ),
            self.thread, format="json"
        )
        self.assertEqual(result.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Parent comment is already a sub comment",
            str(result.data['message'])
        )
