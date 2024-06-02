from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus
from news.models import News, Comment


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser',
                                            password='password')
        cls.news = News.objects.create(title='Title', text='Text')
        cls.comment = Comment.objects.create(news=cls.news, author=cls.user,
                                             text='Test Comment')

    def test_comment_edit_page_available_to_author(self):
        self.client.login(username='testuser', password='password')
        url = reverse('news:edit', args=(self.comment.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.client.logout()

    def test_comment_edit_page_unavailable_to_anonymous_user(self):
        url = reverse('news:edit', args=(self.comment.id,))
        response = self.client.get(url)
        self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_comment_edit_page_unavailable_to_non_author(self):
        self.client.login(username='testuser2', password='password')
        url = reverse('news:edit', args=(self.comment.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.client.logout()

    def test_comment_delete_page_available_to_author(self):
        self.client.login(username='testuser', password='password')
        url = reverse('news:delete', args=(self.comment.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.client.logout()

    def test_comment_delete_page_unavailable_to_anonymous_user(self):
        url = reverse('news:delete', args=(self.comment.id,))
        response = self.client.get(url)
        self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_comment_delete_page_unavailable_to_non_author(self):
        self.client.login(username='testuser2', password='password')
        url = reverse('news:delete', args=(self.comment.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.client.logout()
