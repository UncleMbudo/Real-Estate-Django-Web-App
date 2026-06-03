from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AccountViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='existing', password='pass1234',
            email='existing@test.com', first_name='John', last_name='Doe'
        )

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Alice', 'last_name': 'Smith',
            'username': 'alice', 'email': 'alice@test.com',
            'password': 'securepass1', 'password2': 'securepass1'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='alice').exists())

    def test_register_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Bob', 'last_name': 'Jones',
            'username': 'bob', 'email': 'bob@test.com',
            'password': 'pass1', 'password2': 'pass2'
        })
        self.assertRedirects(response, reverse('register'))

    def test_register_duplicate_username(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'X', 'last_name': 'Y',
            'username': 'existing', 'email': 'new@test.com',
            'password': 'pass1234', 'password2': 'pass1234'
        })
        self.assertRedirects(response, reverse('register'))

    def test_register_duplicate_email(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'X', 'last_name': 'Y',
            'username': 'newuser', 'email': 'existing@test.com',
            'password': 'pass1234', 'password2': 'pass1234'
        })
        self.assertRedirects(response, reverse('register'))

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'existing', 'password': 'pass1234'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': 'existing', 'password': 'wrongpass'
        })
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/accounts/login?next=/accounts/dashboard')

    def test_dashboard_authenticated(self):
        self.client.login(username='existing', password='pass1234')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John')

    def test_logout(self):
        self.client.login(username='existing', password='pass1234')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('index'))

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username='existing', password='pass1234')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_authenticated_user_redirected_from_register(self):
        self.client.login(username='existing', password='pass1234')
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('dashboard'))
